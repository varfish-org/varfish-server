"""Code for supporting variant import."""
import json
import tempfile
import uuid as uuid_object

from bgjobs.models import LOG_LEVEL_ERROR, BackgroundJob, JobModelMessageMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from projectroles.models import Project
from projectroles.plugins import get_backend_api
from sqlalchemy import and_

from importer.management.helpers import open_file, tsv_reader
from variants.helpers import get_engine, get_meta
from variants.models.case import Case, CaseAlignmentStats, update_variant_counts
from variants.models.variants import AnnotationReleaseInfo, SmallVariant


class VariantImporterBase:
    """Base class for variant importer helper classes."""

    variant_set_attribute = None
    table_names = None
    latest_set = None
    #: Fill this with ``field_name: default_tsv_value`` in your subclass to ensure the fields are present.
    default_values = {}
    release_info = None

    def __init__(self, import_job):
        self.import_job = import_job

    def run(self):
        """Perform the variant import."""
        pedigree = list(self._yield_pedigree())
        # Create new case or get existing one.
        with transaction.atomic():
            case, case_created = Case.objects.get_or_create(
                name=self.import_job.case_name,
                project=self.import_job.project,
                defaults={
                    "index": self.import_job.index_name,
                    "pedigree": pedigree,
                },
            )
            # Create new variant set for case.
            variant_set = getattr(case, self.variant_set_attribute).create(state="importing")
        try:
            self._perform_import(variant_set)
        except Exception as e:
            self.import_job.add_log_entry("Problem during variant import: %s" % e, LOG_LEVEL_ERROR)
            self.import_job.add_log_entry("Rolling back variant set...")
            self._purge_variant_set(variant_set)
            raise RuntimeError("Problem during variant import ") from e
        with transaction.atomic():
            variant_set.state = "active"
            variant_set.save()
            if not case_created:  # Case needs to be updated.
                case.index = self.import_job.index_name
                case.pedigree = pedigree
            setattr(case, self.latest_set, variant_set)
            case.save()
            update_variant_counts(variant_set.case)
            self._post_import(variant_set)
        if variant_set.state == "active":
            self._clear_old_variant_sets(case, variant_set)
        else:
            self.import_job.add_log_entry("Problem during variant import", LOG_LEVEL_ERROR)
            self.import_job.add_log_entry("Rolling back variant set...")
            self._purge_variant_set(variant_set)
            raise RuntimeError("Problem during variant import")

    def _perform_import(self, variant_set):
        raise NotImplementedError("Override me!")

    def _post_import(self, variant_set):
        raise NotImplementedError("Override me!")

    def _purge_variant_set(self, variant_set):
        variant_set.__class__.objects.filter(pk=variant_set.id).update(state="deleting")
        for table_name, variant_set_attr in self.table_names:
            table = get_meta().tables[table_name]
            get_engine().execute(
                table.delete().where(
                    and_(
                        getattr(table.c, variant_set_attr) == variant_set.id,
                        table.c.case_id == variant_set.case.id,
                    )
                )
            )
        variant_set.__class__.objects.filter(pk=variant_set.id).delete()

    def _yield_pedigree(self):
        samples_in_genotypes = self._get_samples_in_genotypes()
        seen_index = False
        with open(self.import_job.path_ped, "rt") as pedf:
            for line in pedf:
                line = line.strip()
                _, patient, father, mother, sex, affected = line.split("\t")
                seen_index = seen_index or patient == self.import_job.index_name
                sex = int(sex)
                affected = int(affected)
                yield {
                    "patient": patient,
                    "father": father,
                    "mother": mother,
                    "sex": sex,
                    "affected": affected,
                    "has_gt_entries": patient in samples_in_genotypes,
                }
        if not seen_index:
            raise RuntimeError("Index {} not seen in pedigree!".format(self.import_job.index_name))

    def _get_samples_in_genotypes(self):
        """Return names from samples present in genotypes column."""
        with open_file(self.import_job.path_genotypes[0], "rt") as tsv:
            header = tsv.readline()[:-1].split("\t")
            first = tsv.readline()[:-1].replace('"""', '"').split("\t")
            values = dict(zip(header, first))
            return list(json.loads(values["genotype"]).keys())

    def _clear_old_variant_sets(self, case, keep_variant_set):
        self.import_job.add_log_entry("Starting to purge old variants")
        before = timezone.now()
        for variant_set in keep_variant_set.__class__.objects.filter(
            case=case, state="active", date_created__lt=keep_variant_set.date_created
        ):
            if variant_set.id != keep_variant_set.id:
                self._purge_variant_set(variant_set)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished purging old variants in %.2f s" % elapsed.total_seconds()
        )

    def _import_table(self, variant_set, token, path_attr, model_class):
        before = timezone.now()
        self.import_job.add_log_entry("Creating temporary %s file..." % token)
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            for i, path_genotypes in enumerate(getattr(self.import_job, path_attr)):
                with open_file(path_genotypes, "rt") as inputf:
                    header = inputf.readline().strip()
                    header_arr = header.split("\t")
                    try:
                        case_idx = header_arr.index("case_id")
                        set_idx = header_arr.index("set_id")
                    except ValueError as e:
                        raise RuntimeError(
                            "Column 'case_id' or 'set_id' not found in %s TSV" % token
                        ) from e
                    # Extend header for fields in self.default_values and build suffix to append to every line.
                    default_suffix = []
                    for field, value in self.default_values.items():
                        if field not in header_arr:
                            header += "\t%s" % field
                            default_suffix.append(str(value))
                    if i == 0:
                        tempf.write(header)
                        tempf.write("\n")
                    while True:
                        line = inputf.readline().strip()
                        if not line:
                            break
                        arr = line.split("\t")
                        arr[case_idx] = str(variant_set.case.pk)
                        arr[set_idx] = str(variant_set.pk)
                        tempf.write("\t".join(arr + default_suffix))
                        tempf.write("\n")
            tempf.flush()
            elapsed = timezone.now() - before
            self.import_job.add_log_entry("Wrote file in %.2f s" % elapsed.total_seconds())

            before = timezone.now()
            self.import_job.add_log_entry("Importing %s file..." % token)
            model_class.objects.from_csv(
                tempf.name,
                delimiter="\t",
                null=".",
                ignore_conflicts=True,
                drop_constraints=False,
                drop_indexes=False,
            )
            elapsed = timezone.now() - before
            self.import_job.add_log_entry(
                "Finished importing %s in %.2f s" % (token, elapsed.total_seconds())
            )

    def _import_annotation_release_info(self, variant_set):
        before = timezone.now()
        self.import_job.add_log_entry("Importing annotation release info...")
        for path_db_info in self.import_job.path_db_info:
            for entry in tsv_reader(path_db_info):
                self._get_release_info().objects.get_or_create(
                    genomebuild=entry["genomebuild"],
                    table=entry["db_name"],
                    case=variant_set.case,
                    variant_set=variant_set,
                    defaults={"release": entry["release"]},
                )
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing annotation release info in %.2f s" % elapsed.total_seconds()
        )

    def _get_release_info(self):
        if not self.release_info:
            raise NotImplementedError("Please set release_info!")
        return self.release_info


class VariantImporter(VariantImporterBase):
    """Helper class for importing variants."""

    variant_set_attribute = "smallvariantset_set"
    table_names = (
        ("variants_smallvariant", "set_id"),
        ("variants_casealignmentstats", "variant_set_id"),
    )
    latest_set = "latest_variant_set"
    # Ensure that the info and {refseq,ensembl}_exon_dist fields are present with default values.  This snippet
    # can go away once we are certain all TSV files have been created with varfish-annotator >=0.10
    default_values = {"info": "{}", "refseq_exon_dist": ".", "ensembl_exon_dist": "."}
    release_info = AnnotationReleaseInfo

    def _perform_import(self, variant_set):
        self._import_annotation_release_info(variant_set)
        self._import_alignment_stats(variant_set)
        self._import_table(variant_set, "genotypes", "path_genotypes", SmallVariant)

    def _post_import(self, variant_set):
        self._rebuild_small_variants_stats(variant_set)

    def _rebuild_small_variants_stats(self, variant_set):
        """Rebuild small variant statistics."""
        # This must be imported here to circumvent cyclic dependencies
        from variants.variant_stats import rebuild_case_variant_stats  # noqa

        before = timezone.now()
        self.import_job.add_log_entry("Computing variant statistics...")
        rebuild_case_variant_stats(get_engine(), variant_set, logger=self.import_job.add_log_entry)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished computing variant statistics in %.2f s" % elapsed.total_seconds()
        )

    def _import_alignment_stats(self, variant_set):
        before = timezone.now()
        self.import_job.add_log_entry("Importing alignment statistics...")
        for path_bam_qc in self.import_job.path_bam_qc:
            self.import_job.add_log_entry("... importing from %s" % path_bam_qc)
            # Enumerate is bad because empty iterator and iterator with one element result in the same count
            lineno = 0
            for entry in tsv_reader(path_bam_qc):
                case_stats, created = CaseAlignmentStats.objects.get_or_create(
                    variant_set=variant_set,
                    defaults={
                        "case": variant_set.case,
                        "bam_stats": json.loads(entry["bam_stats"].replace('"""', '"')),
                    },
                )
                if created:
                    self.import_job.add_log_entry(
                        "created entry for case '%s' with id %d and variant set id %d"
                        % (variant_set.case.name, variant_set.case.id, variant_set.id)
                    )
                else:  # needs update
                    case_stats.bam_stats = json.loads(entry["bam_stats"].replace('"""', '"'))
                    case_stats.case = variant_set.case
                    case_stats.save()
                    self.import_job.add_log_entry(
                        "updated entry (found stats entry for variant set id %d)" % variant_set.id
                    )
                lineno += 1
            self.import_job.add_log_entry("imported %d entries" % lineno)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing alignment statistics in %.2f s" % elapsed.total_seconds()
        )


def run_import_variants_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    import_job = ImportVariantsBgJob.objects.get(pk=pk)
    started = timezone.now()
    with import_job.marks():
        VariantImporter(import_job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=import_job.project,
                app_name="variants",
                user=import_job.bg_job.user,
                event_name="case_import",
                description='Import of small variants for case "%s" finished in %.2fs.'
                % (import_job.case_name, elapsed.total_seconds()),
                status_type="OK",
            )


class ImportVariantsBgJob(JobModelMessageMixin, models.Model):
    """Background job for importing variants."""

    #: Task description for logging.
    task_desc = "Import variants"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.import"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")
    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is imported to"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    #: The case name.
    case_name = models.CharField(max_length=128, blank=False, null=False, help_text="The case name")
    #: The index name.
    index_name = models.CharField(
        max_length=128, blank=False, null=False, help_text="The index name"
    )
    #: The path to the PED file.
    path_ped = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to PED file"
    )
    #: The path to the variant genotype calls TSV.
    path_genotypes = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to variants TSV file"
        )
    )
    #: The path to the db-info TSV file.
    path_db_info = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to db-info TSV file"
        )
    )
    #: The path to the bam-qc TSV file.
    path_bam_qc = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to bam-qc TSV file"
        ),
        default=list,
    )

    def get_human_readable_type(self):
        return "Import (small) variants into VarFish"

    def get_absolute_url(self):
        return reverse(
            "variants:import-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )

    def get_case(self):
        latest_case = self.project.case_set.filter(name=self.case_name).order_by("-date_created")
        if latest_case:
            return latest_case[0]
        return None

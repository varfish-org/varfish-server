from enum import Enum
import json
import re
import tempfile
import uuid as uuid_object

from bgjobs.models import LOG_LEVEL_ERROR, BackgroundJob, JobModelMessageMixin
from django.contrib import auth
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.urls import reverse
from django.utils import timezone
from projectroles.models import Project
from sqlalchemy import and_

from importer.management.helpers import open_file, tsv_reader
from svs.models import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    SvAnnotationReleaseInfo,
    SvQueryResultSet,
)
from varfish.utils import receiver_subclasses
from variants.helpers import get_engine, get_meta
from variants.models import (
    AnnotationReleaseInfo,
    Case,
    CaseAlignmentStats,
    CaseGeneAnnotationEntry,
    CoreCase,
    SmallVariant,
    SmallVariantQueryResultSet,
    SmallVariantSet,
    update_variant_counts,
)

User = auth.get_user_model()


class ImportInfo(models.Model):
    """Store information about background data data import."""

    #: Releas of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: Name of imported table
    table = models.CharField(max_length=512)
    #: Timestamp of import
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Further comments
    comment = models.CharField(max_length=1024)

    class Meta:
        unique_together = (("genomebuild", "table"),)


class CaseVariantType(Enum):
    """Enumeration of variant types in a case."""

    #: Small variants.
    SMALL = "variants"
    #: Structural variants.
    STRUCTURAL = "svs"


class CaseImportState(Enum):
    """Enumeration for the states."""

    #: Draft state, allows modification.
    DRAFT = "draft"
    #: Submitted for import.
    SUBMITTED = "submitted"
    #: Imported into database.
    IMPORTED = "imported"
    #: Previously in database but not any more.
    EVICTED = "evicted"
    #: Failed import.
    FAILED = "failed"


class VariantSetImportState(Enum):
    """Enumeration for the states."""

    #: Draft state, allows modification.
    DRAFT = "draft"
    #: Files uploaded for import.
    UPLOADED = "uploaded"
    #: Imported into database.
    IMPORTED = "imported"
    #: Previously in database but not any more.
    EVICTED = "evicted"
    #: Failed import.
    FAILED = "failed"


class CaseImportInfo(CoreCase):
    """Store import info for a case."""

    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Creator of the import info.
    owner = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, help_text="User that created the import info."
    )
    #: The project containing this case.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    case = models.ForeignKey(
        Case,
        null=True,
        unique=True,
        on_delete=models.CASCADE,
        help_text="The case that this is for, once created.",
        related_name="import_infos",
        related_query_name="import_infos",
    )

    state = models.CharField(
        max_length=32,
        choices=tuple((s.value, s.value) for s in CaseImportState),
        default=CaseImportState.DRAFT.value,
        help_text="State of the case import ",
    )

    def get_project(self):
        return self.project


class VariantSetImportInfo(models.Model):
    """Information for importing a variant set for a case."""

    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    genomebuild = models.CharField(
        max_length=32,
        choices=(("GRCh37", "GRCh37"), ("GRCh38", "GRCh38")),
        default="GRCh37",
        help_text="Genome build used in the variant set.",
    )

    case_import_info = models.ForeignKey(
        CaseImportInfo,
        on_delete=models.CASCADE,
        help_text="The import info for the case.",
    )

    variant_type = models.CharField(
        max_length=32,
        choices=(
            (CaseVariantType.SMALL.name, CaseVariantType.SMALL.value),
            (CaseVariantType.STRUCTURAL.name, CaseVariantType.STRUCTURAL.value),
        ),
        help_text="The type of variant set that is referenced.",
    )

    state = models.CharField(
        max_length=32,
        choices=tuple((s.value, s.value) for s in VariantSetImportState),
        default=VariantSetImportState.DRAFT.value,
        help_text="State of the variant set import",
    )

    def get_project(self):
        return self.case_import_info.get_project()

    class Meta:
        unique_together = (("case_import_info", "variant_type"),)


def set_member_file_url_upload_to(instance, filename):
    def to_snake_case(name):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    if hasattr(instance, "case_import_info"):
        return "importer/%s/%s/%s" % (
            instance.case_import_info.sodar_uuid,
            to_snake_case(type(instance).__name__),
            instance.sodar_uuid,
        )
    else:
        return "importer/%s/%s/%s" % (
            instance.variant_set_import_info.case_import_info.sodar_uuid,
            to_snake_case(type(instance).__name__),
            instance.sodar_uuid,
        )


class SetMemberFileUrl(models.Model):
    """Entry in a set of URLs to files URLs."""

    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    file = models.FileField(upload_to=set_member_file_url_upload_to, help_text="The uploaded file.")

    name = models.CharField(max_length=200, help_text="Original file name.")

    md5 = models.CharField(max_length=32, help_text="MD5 checksum of original file.")

    class Meta:
        abstract = True


class BamQcFile(SetMemberFileUrl):
    """Base class for the urls that can be attached to ``VariantSetImportInfo``."""

    case_import_info = models.ForeignKey(
        CaseImportInfo,
        on_delete=models.CASCADE,
        help_text="The case import info that this is for.",
    )

    def get_project(self):
        return self.case_import_info.get_project()

    class Meta:
        unique_together = (("case_import_info", "md5"),)


class CaseGeneAnnotationFile(SetMemberFileUrl):
    """Per-case gene annotations for display on the case overview page."""

    case_import_info = models.ForeignKey(
        CaseImportInfo,
        on_delete=models.CASCADE,
        help_text="The case import info that this is for.",
    )

    def get_project(self):
        return self.case_import_info.get_project()

    class Meta:
        unique_together = (("case_import_info", "md5"),)


class ImportVariantSetUrl(SetMemberFileUrl):
    """Base class for the urls that can be attached to ``VariantSetImportInfo``."""

    variant_set_import_info = models.ForeignKey(
        VariantSetImportInfo,
        on_delete=models.CASCADE,
        help_text="The variant set info that this is for.",
    )

    def get_project(self):
        return self.variant_set_import_info.get_project()

    class Meta:
        abstract = True
        unique_together = (("variant_set_import_info", "md5"),)


class GenotypeFile(ImportVariantSetUrl):
    """Genotype information of the variants."""


class EffectFile(ImportVariantSetUrl):
    """Information on the impact of the variants."""


class DatabaseInfoFile(ImportVariantSetUrl):
    """Information on the databases used for annotation."""


# NB: This must come **after** all specializations of ``SetMemberFileUrl``.
@receiver_subclasses(post_delete, SetMemberFileUrl, "set_member_file_url_post_delete")
def set_member_file_delete(sender, instance, **_kwargs):
    instance.file.delete(save=False)


class ImportCaseBgJob(JobModelMessageMixin, models.Model):
    """Background job for importing a case."""

    #: Task description for logging.
    task_desc = "Import case"

    #: String identifying model in BackgroundJob.
    spec_name = "importer.import_case"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of creation
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of modification")

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

    import_info = models.ForeignKey(
        CaseImportInfo,
        on_delete=models.CASCADE,
        null=True,
        help_text="Case import information to use.",
    )

    def get_human_readable_type(self):
        return "Import case (small/structural) variants into VarFish"

    def get_absolute_url(self):
        return reverse(
            "importer:import-case-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )

    def get_case(self):
        if self.import_info and self.import_info.case:
            return self.import_info.case
        else:
            return None


def run_import_case_bg_job(pk):
    """Perform the import of a case from a ``ImportCaseBgJob``"""
    job = ImportCaseBgJob.objects.get(id=pk)
    with job.marks():
        CaseImporter(job).run()


class CaseImporter:
    """Helper class to directly import from ``CaseImportInfo``."""

    # TODO: need to merge this with the old import info from CLI

    variant_type_map = {
        CaseVariantType.SMALL.name: "smallvariantset_set",
        CaseVariantType.STRUCTURAL.name: "structuralvariantset_set",
    }
    table_name_map = {
        CaseVariantType.SMALL.name: (
            ("variants_smallvariant", "set_id"),
            ("variants_casealignmentstats", "variant_set_id"),
        ),
        CaseVariantType.STRUCTURAL.name: (
            ("svs_structuralvariant", "set_id"),
            ("svs_structuralvariantgeneannotation", "set_id"),
        ),
    }
    latest_set_map = {
        CaseVariantType.SMALL.name: "latest_variant_set",
        CaseVariantType.STRUCTURAL.name: "latest_structural_variant_set",
    }

    def __init__(self, import_job):
        self.import_job: ImportCaseBgJob = import_job
        self.import_info = import_job.import_info
        self.case = None

    def run(self):
        """Perform the variant import."""
        # Create new case or get existing one.
        if self.import_info.case:
            self.case = self.import_info.case
            case_created = False
        else:
            with transaction.atomic():
                self.case, case_created = Case.objects.get_or_create(
                    name=self.import_info.name,
                    release=self.import_info.release,
                    project=self.import_info.project,
                    defaults={
                        "index": self.import_info.index,
                        "pedigree": self.import_info.pedigree,
                    },
                )
                if not case_created:
                    if self.case.release != self.import_info.release:
                        self.import_job.add_log_entry(
                            "Tried to import data for genome build %s into case with genome build %s"
                            % (self.import_info.release, self.case.release),
                            LOG_LEVEL_ERROR,
                        )
                        raise RuntimeError(
                            "Inconsistent genome builds for import and existing case"
                        )
                else:
                    SmallVariantQueryResultSet.objects.create(
                        case=self.case,
                        result_row_count=0,
                        start_time=self.case.date_created,
                        end_time=self.case.date_created,
                        elapsed_seconds=0,
                    )
                    SvQueryResultSet.objects.create(
                        case=self.case,
                        result_row_count=0,
                        start_time=self.case.date_created,
                        end_time=self.case.date_created,
                        elapsed_seconds=0,
                    )
                self._import_case_gene_annotation(self.import_info)
        for variant_set_info in self.import_info.variantsetimportinfo_set.filter(
            state=VariantSetImportState.UPLOADED.value
        ):
            attr_name = self.variant_type_map[variant_set_info.variant_type]
            table_names = self.table_name_map[variant_set_info.variant_type]
            latest_set = self.latest_set_map[variant_set_info.variant_type]
            variant_set = getattr(self.case, attr_name).create(state="importing")
            try:
                self.import_job.add_log_entry(
                    "Importing %s variants" % variant_set_info.variant_type
                )
                self._perform_import(variant_set, variant_set_info)
            except Exception as e:
                self.import_job.add_log_entry(
                    "Problem during variant import: %s" % e, LOG_LEVEL_ERROR
                )
                self.import_job.add_log_entry("Rolling back variant set ...")
                variant_set_info.state = VariantSetImportState.FAILED.value
                variant_set_info.save()
                self.import_info.state = CaseImportState.FAILED.value
                self.import_info.save()
                self._purge_variant_set(variant_set, table_names)
                raise RuntimeError("Problem during variant import ") from e

            self.import_job.add_log_entry("Activating variant set ...")

            with transaction.atomic():
                variant_set.state = "active"
                variant_set.save()
                if not case_created:  # Case needs to be updated.
                    self.case.index = self.import_info.index
                    self.case.pedigree = self.import_info.pedigree
                setattr(self.case, latest_set, variant_set)
                self.case.save()

            self.import_job.add_log_entry(
                "Updating variant counts for variant type %s" % variant_set_info.variant_type
            )

            with transaction.atomic():
                update_variant_counts(
                    self.case, variant_set_info.variant_type, logger=self.import_job.add_log_entry
                )

            self._post_import(variant_set, variant_set_info.variant_type)

            if variant_set.state == "active":
                self._clear_old_variant_sets(variant_set, table_names)
                variant_set_info.state = VariantSetImportState.IMPORTED.value
                variant_set_info.save()
            else:
                self.import_job.add_log_entry("Problem during variant import", LOG_LEVEL_ERROR)
                self.import_job.add_log_entry("Rolling back variant set ...")
                self.import_info.state = CaseImportState.FAILED.value
                self.import_info.save()
                variant_set_info.state = VariantSetImportState.FAILED.value
                variant_set_info.save()
                self._purge_variant_set(variant_set, table_names)
                raise RuntimeError("Problem during variant import")
        else:
            self.import_info.state = CaseImportState.IMPORTED.value
            self.import_info.save()

    def _purge_variant_set(self, variant_set, table_names):
        self.import_job.add_log_entry("Performing variant set purge ...")
        self.import_job.add_log_entry("... setting state to 'deleting'.")
        variant_set.__class__.objects.filter(pk=variant_set.id).update(state="deleting")
        self.import_job.add_log_entry("... removing linked entries in tables:")
        for table_name, variant_set_attr in table_names:
            self.import_job.add_log_entry("... - %s" % table_name)
            table = get_meta().tables[table_name]
            get_engine().execute(
                table.delete().where(
                    and_(
                        getattr(table.c, variant_set_attr) == variant_set.id,
                        table.c.case_id == variant_set.case.id,
                    )
                )
            )
        self.import_job.add_log_entry("... deleting variant set %d" % variant_set.pk)
        variant_set.__class__.objects.filter(pk=variant_set.id).delete()

    def _clear_old_variant_sets(self, keep_variant_set, table_names):
        self.import_job.add_log_entry("Starting to purge old variants")
        before = timezone.now()
        self.import_job.add_log_entry("... keeping variant set with id %d" % keep_variant_set.pk)
        for variant_set in keep_variant_set.__class__.objects.filter(
            case=self.case, state="active", date_created__lt=keep_variant_set.date_created
        ):
            self.import_job.add_log_entry("... found variant set with id %d" % variant_set.pk)
            if variant_set.id != keep_variant_set.id:
                self.import_job.add_log_entry("... purging variant set (%d)!" % variant_set.pk)
                self._purge_variant_set(variant_set, table_names)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished purging old variants in %.2f s" % elapsed.total_seconds()
        )

    def _import_table(
        self,
        variant_set_info,
        variant_set,
        token,
        path_attr,
        model_class,
        default_values=None,
        no_release=True,
    ):
        default_values = default_values or {}
        before = timezone.now()
        self.import_job.add_log_entry("Creating temporary %s file..." % token)
        case_genomebuild = self.case.release
        any_written = False
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            for i, import_variant_set_url in enumerate(getattr(variant_set_info, path_attr).all()):
                self.import_job.add_log_entry("Importing from %s" % import_variant_set_url.name)
                with open_file(import_variant_set_url.file, "rt") as inputf:
                    any_written = True
                    header = inputf.readline().strip()
                    header_arr = header.split("\t")
                    try:
                        if no_release:
                            release_idx = None
                        else:
                            release_idx = header_arr.index("release")
                        case_idx = header_arr.index("case_id")
                        set_idx = header_arr.index("set_id")
                    except ValueError as e:
                        raise RuntimeError(
                            "Column 'release', 'case_id' or 'set_id' not found in %s TSV" % token
                        ) from e
                    # Extend header for fields in self.default_values and build suffix to append to every line.
                    default_suffix = []
                    for field, value in default_values.items():
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
                        if release_idx is not None and arr[release_idx] != case_genomebuild:
                            raise RuntimeError(
                                "Incompatible genome build in %s TSV: %s vs %s from case"
                                % (token, arr[release_idx], case_genomebuild)
                            )
                        arr[case_idx] = str(variant_set.case.pk)
                        arr[set_idx] = str(variant_set.pk)
                        tempf.write("\t".join(arr + default_suffix))
                        tempf.write("\n")
            tempf.flush()
            elapsed = timezone.now() - before
            self.import_job.add_log_entry("Wrote file in %.2f s" % elapsed.total_seconds())

            if not any_written:
                self.import_job.add_log_entry("File is empty, skipping import")
            else:
                before = timezone.now()
                self.import_job.add_log_entry("Importing %s file..." % token)
                model_class.objects.from_csv(
                    tempf.name,
                    delimiter="\t",
                    null=".",
                    ignore_conflicts=False,
                    drop_constraints=False,
                    drop_indexes=False,
                )
                elapsed = timezone.now() - before
                self.import_job.add_log_entry(
                    "Finished importing %s in %.2f s" % (token, elapsed.total_seconds())
                )

    def _perform_import(self, variant_set, variant_set_info):
        if variant_set_info.genomebuild != self.case.release:
            raise RuntimeError(
                "Incompatible genome builds in import info: %s and existing case: %s"
                % (variant_set_info.genomebuild, self.case.release)
            )
        if variant_set_info.variant_type == CaseVariantType.SMALL.name:
            # Ensure that the info and {refseq,ensembl}_exon_dist fields are present with default values.  This snippet
            # can go away once we are certain all TSV files have been created with varfish-annotator >=0.10
            self._import_alignment_stats(self.import_info, variant_set)
            default_values = {"info": "{}", "refseq_exon_dist": ".", "ensembl_exon_dist": "."}
            self._import_annotation_release_info(
                variant_set_info, variant_set, AnnotationReleaseInfo
            )
            self._import_table(
                variant_set_info,
                variant_set,
                "genotypes",
                "genotypefile_set",
                SmallVariant,
                default_values,
            )
        else:
            assert variant_set_info.variant_type == CaseVariantType.STRUCTURAL.name
            self._import_table(
                variant_set_info,
                variant_set,
                "SVs",
                "genotypefile_set",
                StructuralVariant,
            )
            self._import_annotation_release_info(
                variant_set_info, variant_set, SvAnnotationReleaseInfo
            )
            self._import_table(
                variant_set_info,
                variant_set,
                "SV-gene annotation",
                "effectfile_set",
                StructuralVariantGeneAnnotation,
                no_release=True,
            )

    def _post_import(self, variant_set, variant_type):
        self.import_job.add_log_entry("Performing post import routine ...")
        if variant_type == CaseVariantType.SMALL.name:
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

    def _import_annotation_release_info(
        self, variant_set_info: VariantSetImportInfo, variant_set, release_info
    ):
        before = timezone.now()
        self.import_job.add_log_entry("Importing annotation release info...")
        # TODO: clear in the beginning
        total = 0
        updates = 0
        for db_info_file in variant_set_info.databaseinfofile_set.all():
            self.import_job.add_log_entry("... importing from %s" % db_info_file.name)
            for entry in tsv_reader(db_info_file.file):
                total += 1
                info, created = release_info.objects.get_or_create(
                    genomebuild=entry["genomebuild"],
                    table=entry["db_name"],
                    case=variant_set.case,
                    variant_set=variant_set,
                    defaults={"release": entry["release"]},
                )
                if not created:
                    updates += 1
                    info.release = entry["release"]
                    info.save()
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing annotation release (total: %d, updates: %d) info in %.2f s"
            % (total, updates, elapsed.total_seconds())
        )

    def _import_case_gene_annotation(self, import_info: CaseImportInfo):
        before = timezone.now()
        self.import_job.add_log_entry("Importing case gene annotations...")
        removed, _ = CaseGeneAnnotationEntry.objects.filter(case=self.case).delete()
        added = 0
        expected_keys = {"gene_symbol", "entrez_id", "ensembl_gene_id", "annotation"}
        for annotation_file in import_info.casegeneannotationfile_set.all():
            self.import_job.add_log_entry("... importing from %s" % annotation_file.name)
            first = True
            for entry in tsv_reader(annotation_file.file):
                keys = list(entry.keys())
                if first and set(keys) != expected_keys:
                    msg = f"Refusing to import invalid record with keys {keys}"
                    self.import_job.add_log_entry(msg, LOG_LEVEL_ERROR)
                    raise ValueError(msg)
                first = False
                CaseGeneAnnotationEntry.objects.create(
                    case=self.case,
                    gene_symbol=entry["gene_symbol"],
                    entrez_id=entry["entrez_id"],
                    ensembl_gene_id=entry["ensembl_gene_id"],
                    annotation=json.loads(entry["annotation"]),
                )
                added += 1
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing case gene annotation (removed: %d, added: %d) in %.2f s"
            % (removed, added, elapsed.total_seconds())
        )

    def _import_alignment_stats(self, import_info: CaseImportInfo, variant_set: SmallVariantSet):
        before = timezone.now()
        self.import_job.add_log_entry("Importing alignment statistics...")
        for bam_qc_file in import_info.bamqcfile_set.all():
            self.import_job.add_log_entry("... importing from %s" % bam_qc_file.name)
            # Enumerate is bad because empty iterator and iterator with one element result in the same count
            lineno = 0
            for entry in tsv_reader(bam_qc_file.file):
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
                else:
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

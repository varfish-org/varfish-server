"""Code for the Case model.

This will eventually go into the ``cases`` app.
"""

import contextlib
import itertools
from itertools import chain
import re
import uuid as uuid_object

from bgjobs.models import (
    LOG_LEVEL_CHOICES,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    BackgroundJob,
    JobModelMessageMixin,
)
from bgjobs.plugins import BackgroundJobsPluginPoint
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from postgres_copy import CopyManager
from projectroles.app_settings import AppSettingAPI
from projectroles.plugins import get_backend_api
from sqlalchemy import and_, func, select

from varfish.utils import JSONField
from variants.helpers import get_engine
from variants.models.projectroles import Project
from variants.models.variants import SmallVariant, SmallVariantSet

_app_settings = AppSettingAPI()

User = get_user_model()


def only_source_name(full_name):
    """Helper function that strips SNAPPY suffixes for samples."""
    if full_name.count("-") >= 3:
        tokens = full_name.split("-")
        return "-".join(tokens[:-3])
    else:
        return full_name


CASE_STATUS_CHOICES = (
    ("initial", "initial"),
    ("active", "active"),
    ("closed-unsolved", "closed as unsolved"),
    ("closed-uncertain", "closed as uncertain"),
    ("closed-solved", "closed as solved"),
)

#: Threshold for hom/het ratio for identifying sex.
CHRX_HET_HOM_THRESH = 0.45
#: Threshold for relatedness between parent and children.
THRESH_PARENT = 0.6
#: Threshold for relatedness between siblings.
THRESH_SIBLING = 0.6

#: Pedigree value for male.
PED_MALE = 1
#: Pedigree value for female.
PED_FEMALE = 2


class CoreCase(models.Model):
    """Abstract base class for Case core fields."""

    #: Genome build
    release = models.CharField(max_length=32, null=True, default="GRCh37")
    #: Name of the case.
    name = models.CharField(max_length=512)
    #: Identifier of the index in ``pedigree``.
    index = models.CharField(max_length=512)
    #: Pedigree information, ``list`` of ``dict`` with the information.
    pedigree = JSONField()
    #: Note field to summarize the current status
    notes = models.TextField(default="", null=True, blank=True)
    #: Status field
    status = models.CharField(max_length=32, default="initial", choices=CASE_STATUS_CHOICES)
    #: Tags field
    tags = ArrayField(models.CharField(max_length=32), default=list, null=True, blank=True)

    class Meta:
        unique_together = (("project", "name"),)
        abstract = True


class CaseManager(models.Manager):
    """Manager for custom table-level Case queries"""

    # TODO: properly test searching..

    def find(self, search_terms, _keywords=None):
        """
        Return objects or links matching the query.
        :param search_terms: Search terms (list of string)
        :param _keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset().order_by("name")
        term_query = Q()
        for t in search_terms:
            term_query.add(Q(name__iexact=t), Q.OR)
            term_query.add(Q(search_tokens__icontains=t), Q.OR)
        return objects.filter(term_query)


class Case(CoreCase):
    """Stores information about a (germline) case."""

    class Meta:
        ordering = ("-date_modified",)
        indexes = [models.Index(fields=["name"])]

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: The number of small variants, ``None`` if no small variants have been imported.
    num_small_vars = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name="Small variants",
        help_text="Number of small variants, empty if no small variants have been imported",
    )
    #: The number of structural variants, ``None`` if no structural variants have been imported.
    num_svs = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name="Structural variants",
        help_text="Number of structural variants, empty if no structural variants have been imported",
    )

    #: The project containing this case.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    #: Case manager with custom queries, supporting ``find()`` for the search.
    objects = CaseManager()
    #: List of additional tokens to search for, for aiding search
    search_tokens = ArrayField(
        models.CharField(max_length=128, blank=True),
        default=list,
        db_index=True,
        help_text="Search tokens",
    )

    #: The ``PresetSet`` to use for filtering this case.  When this is ``None``, the factory defaults are used.
    presetset = models.ForeignKey(
        "PresetSet",
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        help_text="The preset set to use for filtration, if any.",
    )

    latest_variant_set = models.ForeignKey(
        "SmallVariantSet",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="case_of_latest_variant_set",
    )

    latest_structural_variant_set = models.ForeignKey(
        "svs.StructuralVariantSet",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="case_of_latest_structuralvariant_set",
    )

    def latest_variant_set_id(self):
        variant_set = self.latest_variant_set
        if variant_set:
            return variant_set.id
        else:
            return -1

    def has_variants_and_variant_set(self):
        return bool(self.latest_variant_set) and bool(self.num_small_vars)

    def latest_structural_variant_set_id(self):
        structural_variant_set = self.latest_structural_variant_set
        if structural_variant_set:
            return structural_variant_set.id
        else:
            return -1

    def has_svs_and_structural_variant_set(self):
        return bool(self.latest_structural_variant_set) and bool(self.num_svs)

    def days_since_modification(self):
        return (timezone.now() - self.date_modified).days

    def save(self, *args, **kwargs):
        """Override save() to automatically update ``self.search_tokens``"""
        self._update_search_tokens()
        super().save(*args, **kwargs)

    def _update_search_tokens(self):
        """Force-update ``self.search_tokens``, will enable ``.save()`` call to always save."""
        # Get all IDs
        self.search_tokens = [self.name] + [x["patient"] for x in self.pedigree if x.get("patient")]
        # Remove -N1-DNA1-WES1 etc.
        self.search_tokens = [
            re.sub(r"-\S+\d+-\S+\d+-[^-]+\d+$", "", x) for x in self.search_tokens
        ]
        # Convert to lower case
        self.search_tokens = [x.lower() for x in self.search_tokens]
        # Strip non-alphanumeric characters
        self.search_tokens = [re.sub(r"[^a-zA-Z0-9]", "", x) for x in self.search_tokens]

    def get_sex(self, sample):
        """Return ``int``-value sex for the given ``sample`` in ``pedigree``."""
        for line in self.pedigree:
            if line["patient"] == sample:
                return line["sex"]

    def get_absolute_url(self):
        """Return absolute URL for the detail view of this case."""
        return reverse(
            "variants:case-detail",
            kwargs={"project": self.project.sodar_uuid, "case": self.sodar_uuid},
        )

    def get_filter_url(self):
        """Return absolute URL for the filtration view of this case."""
        return reverse(
            "variants:case-filter",
            kwargs={"project": self.project.sodar_uuid, "case": self.sodar_uuid},
        )

    def get_background_jobs(self):
        """Return list of ``BackgroundJob`` objects."""
        # TODO: need to be more dynamic here?
        return BackgroundJob.objects.filter(
            Q(variants_exportfilebgjob_related__case=self)
            | Q(cadd_submission_bg_job__case=self)
            | Q(distiller_submission_bg_job__case=self)
            | Q(spanr_submission_bg_job__case=self)
            | Q(filter_bg_job__case=self)
        )

    def get_members(self):
        """Return list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.pedigree])

    def get_filtered_pedigree_with_samples(self):
        """Return filtered pedigree lines with members with ``has_gt_entries``."""
        # TODO: unit test me
        return [x for x in self.pedigree if x["has_gt_entries"]]

    def get_family_with_filtered_pedigree_with_samples(self):
        """Concatenate the pedigrees of project's cases that have samples."""
        return {self.name: self.get_filtered_pedigree_with_samples()}

    def get_members_with_samples(self):
        """Returns names of members that genotype information / samples in imported VCF file."""
        # TODO: unit test me
        return sorted([x["patient"] for x in self.get_filtered_pedigree_with_samples()])

    def get_trio_roles(self):
        """Returns a dict with keys mapping ``index``, ``mother``, ``father`` to pedigree member names if present."""
        result = {"index": self.index}
        for member in self.pedigree:
            if member["patient"] == self.index:
                if member["father"] != "0":
                    result["father"] = member["father"]
                if member["mother"] != "0":
                    result["mother"] = member["mother"]
        return result

    def sex_errors_pedigree(self):
        """Return dict of sample to error messages indicating sex assignment errors that can be derived from the
        pedigree information.

        Inconsistencies can be determined from father/mother name and sex.
        """
        fathers = set([m["father"] for m in self.pedigree])
        mothers = set([m["mother"] for m in self.pedigree])
        result = {}
        for m in self.pedigree:
            if m["patient"] in fathers and m["sex"] != PED_MALE:
                result[m["patient"]] = ["used as father in pedigree but not male"]
            if m["patient"] in mothers and m["sex"] != PED_FEMALE:
                result[m["patient"]] = ["used as mother in pedigree not female"]
        return result

    def chrx_het_hom_ratio(self, sample):
        """Return het./hom. ratio on chrX for ``sample``."""
        try:
            variant_set = self.latest_variant_set
            if not variant_set:
                return -1
            else:
                sample_stats = variant_set.variant_stats.sample_variant_stats.get(
                    sample_name=sample
                )
                return sample_stats.chrx_het_hom
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return -1.0

    def sex_errors_variant_stats(self, reporter):
        """Return dict of sample to error messages indicating sex assignment errors that can be derived from
        het/hom ratio on chrX.
        """
        try:
            ped_sex = {m["patient"]: m["sex"] for m in self.pedigree}
            result = {}
            variant_set = self.latest_variant_set
            if variant_set:
                for sample_stats in variant_set.variant_stats.sample_variant_stats.all():
                    sample = sample_stats.sample_name
                    stats_sex = 1 if sample_stats.chrx_het_hom < CHRX_HET_HOM_THRESH else 2
                    if stats_sex != ped_sex[sample]:
                        result[sample] = reporter(stats_sex)
            return result
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return {}

    def sex_errors_to_fix(self):
        return self.sex_errors_variant_stats(lambda x: x)

    def sex_errors(self, disable_pedigree_sex_check=None):
        """Returns dict mapping sample to error messages from both pedigree and variant statistics."""

        result = {}

        if disable_pedigree_sex_check is None:
            disable_pedigree_sex_check = _app_settings.get_app_setting(
                "variants", "disable_pedigree_sex_check", project=self.project
            )

        if disable_pedigree_sex_check:
            return result

        for sample, msgs in chain(
            self.sex_errors_pedigree().items(),
            self.sex_errors_variant_stats(
                lambda x: [
                    "sex from pedigree conflicts with one derived from het/hom ratio on chrX"
                ]
            ).items(),
        ):
            result.setdefault(sample, [])
            result[sample] += msgs
        return result

    def rel_errors(self):
        """Returns dict mapping sample to list of relationship errors."""
        ped_entries = {m["patient"]: m for m in self.pedigree}
        result = {}

        try:
            variant_set = self.latest_variant_set
            if variant_set:
                for rel_stats in variant_set.variant_stats.relatedness.all():
                    relationship = "other"
                    if (
                        ped_entries[rel_stats.sample1]["father"]
                        == ped_entries[rel_stats.sample2]["father"]
                        and ped_entries[rel_stats.sample1]["mother"]
                        == ped_entries[rel_stats.sample2]["mother"]
                        and ped_entries[rel_stats.sample1]["father"] != "0"
                        and ped_entries[rel_stats.sample1]["mother"] != "0"
                    ):
                        relationship = "sibling-sibling"
                    elif (
                        ped_entries[rel_stats.sample1]["father"] == rel_stats.sample2
                        or ped_entries[rel_stats.sample1]["mother"] == rel_stats.sample2
                        or ped_entries[rel_stats.sample2]["father"] == rel_stats.sample1
                        or ped_entries[rel_stats.sample2]["mother"] == rel_stats.sample1
                    ):
                        relationship = "parent-child"
                    if (
                        relationship == "sibling-sibling"
                        and rel_stats.relatedness() < THRESH_SIBLING
                    ) or (
                        relationship == "parent-child" and rel_stats.relatedness() < THRESH_PARENT
                    ):
                        for sample in (rel_stats.sample1, rel_stats.sample2):
                            result.setdefault(sample, []).append(
                                (
                                    "pedigree shows {} relation for {} and {} but variants show low degree "
                                    "of relatedness"
                                ).format(
                                    relationship,
                                    only_source_name(rel_stats.sample1),
                                    only_source_name(rel_stats.sample2),
                                )
                            )
            return result
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return {}

    def shortened_notes_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.notes) > max_chars:
            return self.notes[:max_chars] + "..."
        else:
            return self.notes

    def get_annotation_sv_count(self):
        variants = set()
        for record in self.structural_variant_comments.all():
            variants.add((record.chromosome, record.start, record.end, record.sv_type))
        for record in self.structural_variant_flags.all():
            variants.add((record.chromosome, record.start, record.end, record.sv_type))
        return len(variants)

    def get_annotation_small_variant_count(self):
        variants = set()
        for record in self.small_variant_flags.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        for record in self.small_variant_comments.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        for record in self.acmg_ratings.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        return len(variants)

    def get_annotation_count(self):
        """Return annotation count."""
        return self.get_annotation_sv_count() + self.get_annotation_small_variant_count()

    def update_terms(self, terms):
        """Given a dict of individual names to list of terms, ensure that the appropriate ``CasePhenotypeTerms``
        records exist.
        """
        with transaction.atomic():
            self.phenotype_terms.all().delete()
            for name, lst in terms.items():
                self.phenotype_terms.create(individual=name, terms=lst)

    def __str__(self):
        """Return case name as human-readable description."""
        return self.name


class CasePhenotypeTerms(models.Model):
    """Phenotype annotation for an individual in a case."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, help_text="Record UUID", null=False, unique=True
    )

    #: The case that this belongs to.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="phenotype_terms",
        help_text="Case for this annotation",
    )

    #: The name of the individual that this belongs to.
    individual = models.CharField(max_length=128, null=False, blank=False, help_text="Individual")

    #: A list of HPO, Orphanet, and OMIM terms that the case has been annotated with.
    terms = ArrayField(
        models.CharField(max_length=128, blank=False),
        default=list,
        help_text="Phenotype annotation terms with HPO, Orphanet, and OMIM terms",
    )

    class Meta:
        unique_together = (("case", "individual"),)
        ordering = ("individual",)


@receiver(pre_delete)
def delete_case_cascaded(sender, instance, **kwargs):
    """Signal handler when attempting to delete a case

    Bulk deletes are atomic transactions, including pre/post delete signals.
    Comment From their code base in `contrib/contenttypes/fields.py`:

    ```
    if bulk:
        # `QuerySet.delete()` creates its own atomic block which
        # contains the `pre_delete` and `post_delete` signal handlers.
        queryset.delete()
    ```
    """
    if sender == Case:
        SmallVariant.objects.filter(case_id=instance.id).delete()
        for plugin in BackgroundJobsPluginPoint.get_plugins():
            for _, klass in plugin.job_specs.items():
                bgjobs = []
                if hasattr(klass, "case_id"):
                    bgjobs = klass.objects.filter(case_id=instance.id)
                elif hasattr(klass, "case_name"):
                    bgjobs = klass.objects.filter(project=instance.project, case_name=instance.name)
                for bgjob in bgjobs:
                    bgjob.bg_job.delete()


class CaseComments(models.Model):
    """Comments associated with a case."""

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Case for the comment
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="case_comments",
        help_text="Case for this comment",
    )
    #: User who created the comment
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="case_comments",
        help_text="User who created the comment",
    )
    #: User
    comment = models.TextField()

    class Meta:
        ordering = ["date_created"]

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.comment) > max_chars:
            return self.comment[:max_chars] + "..."
        else:
            return self.comment

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


class CaseAlignmentStats(models.Model):
    """Store alignment information about alignment statistics for a case."""

    #: Reference to the case.
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False)
    #: Reference to the small variant set.
    variant_set = models.OneToOneField(SmallVariantSet, on_delete=models.CASCADE, null=False)
    #: The BAM statistics information.  On the top level, there is one entry for each sample.  Below this are the keys
    #: bamstats, idxstats, min_cov_targets, min_cov_bases.  Below bamstats, there is an entry from "samtools stats"
    #: metric (as retrieved by ``grep '^SN'`` to the metric value.  Below idxstats, the contig name is mapped to
    #: a dict with "mapped" and "unmapped" entries.  Below min_cov_targets is a dict mapping coverage to the percentage
    #: of targets having a minimal coverage of the key value.  Below min_cov_bases is a dict mapping coverage to
    #: the percentage of *bases* having a minimal coverage of the key value.
    bam_stats = JSONField(default=dict, null=False)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = (models.Index(fields=["case"]),)


class SyncCaseListBgJob(JobModelMessageMixin, models.Model):
    """Background job for syncing project with remote site."""

    #: Task description for logging.
    task_desc = "Synchronise project cases with upstream"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.sync_project_upstream"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")

    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is to be synced"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    def get_human_readable_type(self):
        return "Synchronise with upstream SODAR"

    def get_absolute_url(self):
        return reverse(
            "variants:sync-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SyncCaseResultMessage(models.Model):
    """A part of the case list synchronisation."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the message.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Message UUID")
    #: The project that the message belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project for the message"
    )

    #: The entry's log level.
    level = models.CharField(
        max_length=50, choices=LOG_LEVEL_CHOICES, help_text="Level of log entry"
    )

    #: The message contained by the log entry.
    message = models.TextField(help_text="Log level's message")


class DeleteCaseBgJob(JobModelMessageMixin, models.Model):
    """Background job for deleting cases."""

    #: Task description for logging.
    task_desc = "Delete case"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.delete_case"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")

    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this object belongs"
    )

    #: Case that will be deleted
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to delete"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    def get_human_readable_type(self):
        return "Delete case"

    def get_absolute_url(self):
        return reverse(
            "variants:case-delete-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class DeleteCase:
    def __init__(self, job):
        self.job = job

    def run(self):
        from variants.queries import DeleteSmallVariantsQuery, DeleteStructuralVariantsQuery  # noqa

        case = self.job.case
        try:
            self.job.add_log_entry(
                "Deleting small and structural variants of case %s" % case.name, LOG_LEVEL_INFO
            )
            for query in itertools.chain(
                DeleteSmallVariantsQuery(get_engine()).run(case_id=case.id),
                DeleteStructuralVariantsQuery(get_engine()).run(case_id=case.id),
            ):
                with contextlib.closing(query):
                    pass
            self.job.add_log_entry("Deleting case %s" % case.name, LOG_LEVEL_INFO)
            case.delete()
        except Exception as e:
            self.job.add_log_entry("Problem during case deletion: %s" % e, LOG_LEVEL_ERROR)
            raise RuntimeError("Problem during case deletion") from e


def run_delete_case_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    job = DeleteCaseBgJob.objects.get(pk=pk)
    started = timezone.now()
    with job.marks():
        DeleteCase(job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=job.project,
                app_name="variants",
                user=job.bg_job.user,
                event_name="delete_case",
                description='Deletion of case "%s" finished in %.2fs.'
                % (job.case.name, elapsed.total_seconds()),
                status_type="OK",
            )


def update_variant_counts(case, kind=None, logger=lambda _: None):
    """Update the variant counts for the given case.

    This is done without changing the ``date_modified`` field.
    """
    from importer.models import CaseVariantType  # noqa
    from svs import models as sv_models  # noqa

    if not kind or kind == CaseVariantType.SMALL.name:
        logger("Updating variant counts for small variants ...")
        variant_set = case.latest_variant_set
        if variant_set:
            set_id = variant_set.pk
            logger("... found variant set with id %d" % set_id)
            stmt = (
                select([func.count()])
                .select_from(SmallVariant.sa.table)
                .where(and_(SmallVariant.sa.set_id == set_id, SmallVariant.sa.case_id == case.pk))
            )
            num_small_vars = get_engine().scalar(stmt)
            logger("... variant set has %d variants" % num_small_vars)
        else:
            logger("... no variant set found")
            num_small_vars = None
        case.num_small_vars = num_small_vars
        case.save()

    if not kind or kind == CaseVariantType.STRUCTURAL.name:
        logger("Updating variant counts for structural variants ...")
        structural_variant_set = case.latest_structural_variant_set
        if structural_variant_set:
            set_id = structural_variant_set.pk
            logger("... found variant set with id %d" % set_id)
            stmt = (
                select([func.count()])
                .select_from(sv_models.StructuralVariant.sa.table)
                .where(
                    and_(
                        sv_models.StructuralVariant.sa.set_id == set_id,
                        sv_models.StructuralVariant.sa.case_id == case.pk,
                    )
                )
            )
            num_svs = get_engine().scalar(stmt)
            logger("... variant set has %d variants" % num_svs)
        else:
            logger("... no variant set found")
            num_svs = None
        case.num_svs = num_svs
        case.save()

    logger("... num_small_vars is now %s" % case.num_small_vars)
    logger("... num_svs is now %s" % case.num_svs)


class CaseGeneAnnotationEntry(models.Model):
    #: The records UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )
    #: The case that is annotated
    case = models.ForeignKey(
        Case, null=False, blank=False, on_delete=models.CASCADE, help_text="The annotated case"
    )
    #: The annotated gene's symbol
    gene_symbol = models.CharField(
        max_length=32, null=False, blank=False, help_text="The gene symbol (informative only)"
    )
    #: The annotated gene's NCIB Entrez ID
    entrez_id = models.CharField(
        max_length=32, null=False, blank=False, help_text="The entrez gene ID"
    )
    #: The annotated gene's ENSEMBL ID
    ensembl_gene_id = models.CharField(
        max_length=32, null=False, blank=False, help_text="The ENSEMBL bene ID"
    )
    #: The JSON containing the annotation
    annotation = models.JSONField(default=dict, help_text="The annotation JSON")

    class Meta:
        ordering = ["gene_symbol"]

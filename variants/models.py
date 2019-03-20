import wrapt
from functools import lru_cache
from itertools import chain
import math
import re
import requests
import uuid as uuid_object

from postgres_copy import CopyManager

from django.db import models, transaction, connection, utils
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_delete

from projectroles.models import Project

from bgjobs.models import BackgroundJob, JobModelMessageMixin

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

#: Threshold for hom/het ratio for identifying sex.
CHRX_HET_HOM_THRESH = 1.0
#: Threshold for relatedness between parent and children.
THRESH_PARENT = 0.6
#: Threshold for relatedness between siblings.
THRESH_SIBLING = 0.6

#: Pedigree value for male.
PED_MALE = 1
#: Pedigree value for female.
PED_FEMALE = 2


def only_source_name(full_name):
    """Helper function that strips SNAPPY suffixes for samples."""
    if full_name.count("-") >= 3:
        tokens = full_name.split("-")
        return "-".join(tokens[:-3])
    else:
        return full_name


class CaseAwareProject(Project):
    """A project that is aware of its cases"""

    class Meta:
        proxy = True

    @lru_cache()
    def pedigree(self):
        """Concatenate the pedigrees of project's cases."""
        result = []
        seen = set()
        for case in self.case_set.all():
            for line in case.pedigree:
                if line["patient"] not in seen:
                    result.append(line)
                seen.add(line["patient"])
        return result

    @lru_cache()
    def get_filtered_pedigree_with_samples(self):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = []
        seen = set()
        for case in self.case_set.all():
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result.append(line)
                seen.add(line["patient"])
        return result

    @lru_cache()
    def sample_to_case(self):
        """Compute sample-to-case mapping."""
        result = {}
        for case in self.case_set.all():
            for line in case.pedigree:
                if line["patient"] not in result:
                    result[line["patient"]] = case
        return result

    @lru_cache()
    def chrx_het_hom_ratio(self, sample):
        """Forward to appropriate case"""
        case = self.sample_to_case().get(sample)
        if not case:
            return 0.0
        else:
            return case.chrx_het_hom_ratio(sample)

    @lru_cache()
    def sex_errors(self):
        """Concatenate all contained case's sex errors dicts"""
        result = {}
        for case in self.case_set.all():
            result.update(case.sex_errors())
        return result

    @lru_cache()
    def get_case_pks(self):
        """Return PKs for cases."""
        return [case.pk for case in self.case_set.all()]


class SmallVariant(models.Model):
    """"Information of a single variant, knows its case."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - position
    position = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Variant type
    var_type = models.CharField(max_length=8)
    #: Link to case ID
    case_id = models.IntegerField()
    #: Genotype information as JSONB
    genotype = JSONField()
    #: Number of hom. alt. genotypes
    num_hom_alt = models.IntegerField(default=0)
    #: Number of hom. ref. genotypes
    num_hom_ref = models.IntegerField(default=0)
    #: Number of het. genotypes
    num_het = models.IntegerField(default=0)
    #: Number of hemi alt. genotypes
    num_hemi_alt = models.IntegerField(default=0)
    #: Number of hemi ref. genotypes
    num_hemi_ref = models.IntegerField(default=0)
    #: Flag if in clinvar
    in_clinvar = models.NullBooleanField()
    #: Total ExAC allele frequency
    exac_frequency = models.FloatField(null=True)
    #: Total ExAC homoyzgous count
    exac_homozygous = models.IntegerField(null=True)
    #: Total ExAC heterozygous count
    exac_heterozygous = models.IntegerField(null=True)
    #: Total ExAC hemizgous count
    exac_hemizygous = models.IntegerField(null=True)
    #: Total thousand genomes frequency count
    thousand_genomes_frequency = models.FloatField(null=True)
    #: Total thousand genomes homozygous count
    thousand_genomes_homozygous = models.IntegerField(null=True)
    #: Total thousand genomes heterozygous count
    thousand_genomes_heterozygous = models.IntegerField(null=True)
    #: Total thousand genomes hemizygous count
    thousand_genomes_hemizygous = models.IntegerField(null=True)
    #: Total gnomAD exomes frequency
    gnomad_exomes_frequency = models.FloatField(null=True)
    #: Total gnomAD exomes homozygous count
    gnomad_exomes_homozygous = models.IntegerField(null=True)
    #: Total gnomAD exomes heterozygous count
    gnomad_exomes_heterozygous = models.IntegerField(null=True)
    #: Total gnomAD exomes hemizygous count
    gnomad_exomes_hemizygous = models.IntegerField(null=True)
    #: Total gnomAD genomes frequency
    gnomad_genomes_frequency = models.FloatField(null=True)
    #: Total gnomAD genomes homozygous count
    gnomad_genomes_homozygous = models.IntegerField(null=True)
    #: Total gnomAD genomes heterozygous count
    gnomad_genomes_heterozygous = models.IntegerField(null=True)
    #: Total gnomAD genomes hemizygous count
    gnomad_genomes_hemizygous = models.IntegerField(null=True)
    #: RefSeq gene ID
    refseq_gene_id = models.CharField(max_length=16, null=True)
    #: RefSeq transcript ID
    refseq_transcript_id = models.CharField(max_length=16, null=True)
    #: Flag RefSeq transcript coding
    refseq_transcript_coding = models.NullBooleanField()
    #: RefSeq HGVS coding sequence
    refseq_hgvs_c = models.CharField(max_length=512, null=True)
    #: RefSeq HGVS protein sequence
    refseq_hgvs_p = models.CharField(max_length=512, null=True)
    #: RefSeq variant effect list
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=16, null=True)
    #: Flag EnsEMBL transcript coding
    ensembl_transcript_coding = models.NullBooleanField()
    #: EnsEMBL HGVS coding sequence
    ensembl_hgvs_c = models.CharField(max_length=512, null=True)
    #: EnsEMBL HGVS protein sequence
    ensembl_hgvs_p = models.CharField(max_length=512, null=True)
    #: EnsEMBL variant effect list
    ensembl_effect = ArrayField(models.CharField(max_length=64, null=True))

    #: Allow bulk import
    objects = CopyManager()

    def get_description(self):
        """Return simple string description of variant"""
        return "-".join(
            map(
                str,
                (self.release, self.chromosome, self.position, self.reference, self.alternative),
            )
        )

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
            "case_id",
            "ensembl_gene_id",
            "refseq_gene_id",
        )
        indexes = [
            # For query: select all variants for a case.
            models.Index(fields=["case_id"]),
            # Filter query: the most important thing is to reduce the variants for a case quickly. It's questionable
            # how much adding homozygous/frequency really adds here.  Adding them back should only done when we
            # know that it helps.
            GinIndex(fields=["case_id", "refseq_effect"]),
            GinIndex(fields=["case_id", "ensembl_effect"]),
            models.Index(fields=["case_id", "in_clinvar"]),
            # Fast white-list queries of gene.
            models.Index(fields=["case_id", "ensembl_gene_id", "refseq_gene_id"]),
        ]


class SmallVariantSummary(models.Model):
    """Summary counts for the small variants.

    In the database, this is a materialized view.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - position
    position = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: Number of hom. ref. genotypes.
    count_hom_ref = models.IntegerField()
    #: Number of heterozygous genotypes.
    count_het = models.IntegerField()
    #: Number of hom. alt. genotypes.
    count_hom_alt = models.IntegerField()
    #: Number of hemi ref. genotypes.
    count_hemi_ref = models.IntegerField()
    #: Number of hemi alt. genotypes.
    count_hemi_alt = models.IntegerField()

    class Meta:
        managed = not settings.IS_TESTING
        db_table = "variants_smallvariantsummary"


def refresh_variants_smallvariantsummary():
    """Refresh the ``SmallVariantSummary`` materialized view."""
    with connection.cursor() as cursor:
        try:
            # This will fail if the materialized view is empty.
            with transaction.atomic():
                cursor.execute(
                    "REFRESH MATERIALIZED VIEW CONCURRENTLY variants_smallvariantsummary"
                )
        except utils.NotSupportedError:
            with transaction.atomic():
                cursor.execute("REFRESH MATERIALIZED VIEW variants_smallvariantsummary")


class CaseManager(models.Manager):
    """Manager for custom table-level Case queries"""

    # TODO: properly test searching..

    def find(self, search_term, _keywords=None):
        """
        Return objects or links matching the query.
        :param search_term: Search term (string)
        :param keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset().order_by("name")
        objects = objects.filter(
            Q(name__iexact=search_term) | Q(search_tokens__icontains=[search_term])
        )
        return objects


class Case(models.Model):
    """Stores information about a (germline) case."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    #: Name of the case.
    name = models.CharField(max_length=512)
    #: Identifier of the index in ``pedigree``.
    index = models.CharField(max_length=32)
    #: Pedigree information, ``list`` of ``dict`` with the information.
    pedigree = JSONField()

    #: The project containing this case.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    #: Case manager with custom queries, supporting ``find()`` for the search.
    objects = CaseManager()
    #: List of additional tokens to search for, for aiding search
    search_tokens = ArrayField(
        models.CharField(max_length=128, blank=True),
        default=list,
        db_index=True,
        help_text="Search tokens",
    )

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

    class Meta:
        indexes = [models.Index(fields=["name"])]

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
            | Q(distiller_submission_bg_job__case=self)
            | Q(filter_bg_job__case=self)
        )

    def get_members(self):
        """Return list of members in ``pedigree``."""
        return [x["patient"] for x in self.pedigree]

    def get_filtered_pedigree_with_samples(self):
        """Return filtered pedigree lines with members with ``has_gt_entries``."""
        # TODO: unit test me
        return [x for x in self.pedigree if x["has_gt_entries"]]

    def get_members_with_samples(self):
        """Returns names of members that genotype information / samples in imported VCF file."""
        # TODO: unit test me
        return [x["patient"] for x in self.get_filtered_pedigree_with_samples()]

    def get_trio_roles(self):
        """Returns a dict with keys mapping ``index``, ``mother``, ``father`` to pedigree member names if present.
        """
        result = {"index": self.index}
        for member in self.pedigree:
            if member["patient"] == self.index:
                if member["father"] != "0":
                    result["father"] = member["father"]
                if member["mother"] != "0":
                    result["mother"] = member["mother"]
        return result

    @lru_cache()
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

    @lru_cache()
    def chrx_het_hom_ratio(self, sample):
        """Return het./hom. ratio on chrX for ``sample``."""
        sample_stats = self.variant_stats.sample_variant_stats.get(sample_name=sample)
        return sample_stats.chrx_het_hom

    @lru_cache()
    def sex_errors_variant_stats(self):
        """Return dict of sample to error messages indicating sex assignment errors that can be derived from
        het/hom ratio on chrX.
        """
        ped_sex = {m["patient"]: m["sex"] for m in self.pedigree}
        result = {}
        for sample_stats in self.variant_stats.sample_variant_stats.all():
            sample = sample_stats.sample_name
            stats_sex = 1 if sample_stats.chrx_het_hom < CHRX_HET_HOM_THRESH else 2
            if stats_sex != ped_sex[sample]:
                result[sample] = [
                    "sex from pedigree conflicts with one derived from het/hom ratio on chrX"
                ]
        return result

    @lru_cache()
    def sex_errors(self):
        """Returns dict mapping sample to error messages from both pedigree and variant statistics."""
        result = {}
        for sample, msgs in chain(
            self.sex_errors_pedigree().items(), self.sex_errors_variant_stats().items()
        ):
            result.setdefault(sample, [])
            result[sample] += msgs
        return result

    @lru_cache()
    def rel_errors(self):
        """Returns dict mapping sample to list of relationship errors."""
        ped_entries = {m["patient"]: m for m in self.pedigree}
        result = {}
        for rel_stats in self.variant_stats.relatedness.all():
            relationship = "other"
            if (
                ped_entries[rel_stats.sample1]["father"] == ped_entries[rel_stats.sample2]["father"]
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
            if (relationship == "sibling-sibling" and rel_stats.relatedness() < THRESH_SIBLING) or (
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

    def __str__(self):
        """Return case name as human-readable description."""
        return self.name


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


class AnnotationReleaseInfo(models.Model):
    """Model to track the database releases used during annotation of a case.
    """

    #: Release of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: Name of imported table
    table = models.CharField(max_length=16)
    #: Timestamp of import
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Link to case
    case = models.ForeignKey(Case)

    class Meta:
        unique_together = ("genomebuild", "table", "release", "case")


#: File type choices for ``ExportFileBgJob``.
EXPORT_TYPE_CHOICE_TSV = "tsv"
EXPORT_TYPE_CHOICE_XLSX = "xlsx"
EXPORT_TYPE_CHOICE_VCF = "vcf"
EXPORT_FILE_TYPE_CHOICES = (
    (EXPORT_TYPE_CHOICE_TSV, "TSV File"),
    (EXPORT_TYPE_CHOICE_XLSX, "Excel File (XLSX)"),
    (EXPORT_TYPE_CHOICE_VCF, "VCF File"),
)


class ExportFileBgJobBase(JobModelMessageMixin, models.Model):
    """Base class for background file export jobs."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    #: The project that the job belongs to.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    #: The query arguments.
    query_args = JSONField(null=False, help_text="(Validated) query parameters")
    #: The file type to create.
    file_type = models.CharField(
        max_length=32, choices=EXPORT_FILE_TYPE_CHOICES, help_text="File types for exported file"
    )

    class Meta:
        ordering = ("-date_created",)
        abstract = True


class ExportFileBgJob(ExportFileBgJobBase):
    """Background job for exporting query results for a single case as a file."""

    # TODO: rename to reflect single-case purpose

    #: Task description for logging.
    task_desc = "Exporting single case to file"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.export_file_bg_job"

    #: The case to export.
    case = models.ForeignKey(Case, null=False, help_text="The case to export")

    def get_human_readable_type(self):
        return "Single-case File Export"

    def get_absolute_url(self):
        return reverse(
            "variants:export-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ExportFileJobResult(models.Model):
    """Result of ``ExportFileBgJob``."""

    job = models.OneToOneField(
        ExportFileBgJob,
        related_name="export_result",
        null=False,
        help_text="Related file export job",
    )
    expiry_time = models.DateTimeField(help_text="Time at which the file download expires")
    payload = models.BinaryField(help_text="Resulting exported file")


class ExportProjectCasesFileBgJob(ExportFileBgJobBase):
    """Background job for exporting query results for all cases in a project as a file."""

    # TODO: rename to reflect single-case purpose

    #: Task description for logging.
    task_desc = "Exporting all project cases to file"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.project_cases_export_file_bg_job"

    def get_human_readable_type(self):
        return "Project-wide Case File Export"

    def get_absolute_url(self):
        return reverse(
            "variants:project-cases-export-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ExportProjectCasesFileBgJobResult(models.Model):
    """Result of ``ExportProjectCasesFileBgJob``."""

    job = models.OneToOneField(
        ExportProjectCasesFileBgJob,
        related_name="export_result",
        null=False,
        help_text="Related file export job",
    )
    expiry_time = models.DateTimeField(help_text="Time at which the file download expires")
    payload = models.BinaryField(help_text="Resulting exported file")


class DistillerSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to MutationDistiller."""

    #: Task description for logging.
    task_desc = "Submission to MutationDistiller"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.distiller_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="distiller_submission_bg_job",
        help_text="Background job for state etc.",
    )
    case = models.ForeignKey(Case, null=False, help_text="The case to export")
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    distiller_project_id = models.CharField(
        max_length=100,
        null=True,
        help_text="The project ID that MutationDistiller assigned on submission",
    )

    def get_human_readable_type(self):
        return "MutationDistiller Submission"

    def get_distiller_project_url(self):
        """Returns URL to MutationDistiller project if ``distiller_project_id`` is set.

        Returns ``None`` otherwise.
        """
        if self.distiller_project_id:
            return (
                "https://www.mutationdistiller.org/temp/QE/vcf_%s/progress.html"
                % self.distiller_project_id
            )
        else:
            return None

    def get_absolute_url(self):
        return reverse(
            "variants:distiller-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SmallVariantComment(models.Model):
    """Model for commenting on a ``SmallVariant``."""

    #: User who created the comment.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="small_variant_comments",
        help_text="User who created the comment",
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: The position of the small variant coordinate.
    position = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="small_variant_comments",
        help_text="Case that this variant is flagged in",
    )

    #: The comment text.
    text = models.TextField(help_text="The comment text", null=False, blank=False)

    def get_variant_description(self):
        return "-".join(
            map(
                str,
                (self.release, self.chromosome, self.position, self.reference, self.alternative),
            )
        )

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            position=self.position,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    class Meta:
        indexes = (
            models.Index(
                fields=["release", "chromosome", "position", "reference", "alternative", "case"]
            ),
        )

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.text) > max_chars:
            return self.text[:max_chars] + "..."
        else:
            return self.text

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


#: Choices for visual inspect, wet-lab validation, or clinical/phenotype flag statuses.
VARIANT_RATING_CHOICES = (
    ("positive", "positive"),
    ("uncertain", "uncertain"),
    ("negative", "negative"),
    ("empty", "empty"),
)


class SmallVariantFlags(models.Model):
    """Small variant flag models, at most one per variant of each model."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: The position of the small variant coordinate.
    position = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="small_variant_flags",
        help_text="Case that this variant is flagged in",
    )

    # Boolean fields for checking

    #: Bookmarked: saved for later
    flag_bookmarked = models.BooleanField(default=False, null=False)
    #: Candidate variant
    flag_candidate = models.BooleanField(default=False, null=False)
    #: Finally selected causative variant
    flag_final_causative = models.BooleanField(default=False, null=False)
    #: Selected for wet-lab validation
    flag_for_validation = models.BooleanField(default=False, null=False)

    # Choice fields for gradual rating

    #: Visual inspection flag.
    flag_visual = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Wet-lab validation flag.
    flag_validation = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Phenotype/clinic suitability flag
    flag_phenotype_match = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Summary/colour code flag
    flag_summary = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )

    def human_readable(self):
        """Return human-redable version of flags"""
        if self.no_flags_set():
            return "no flags set"
        else:
            flag_desc = []
            for name in ("bookmarked", "for_validation", "candidate", "final causative"):
                if getattr(self, "flag_%s" % name.replace(" ", "_")):
                    flag_desc.append(name)
            for name in ("visual", "validation", "phenotype_match", "summary"):
                field = getattr(self, "flag_%s" % name)
                if field and field != "empty":
                    flag_desc.append("%s rating is %s" % (name.split("_")[0], field))
            return ", ".join(flag_desc)

    def get_variant_description(self):
        return "-".join(
            map(
                str,
                (self.release, self.chromosome, self.position, self.reference, self.alternative),
            )
        )

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#flags-" + self.get_variant_description()

    def no_flags_set(self):
        """Return true if no flags are set and the model can be deleted."""
        # TODO: unit test me
        return not any(
            (
                self.flag_bookmarked,
                self.flag_candidate,
                self.flag_final_causative,
                self.flag_for_validation,
                self.flag_visual != "empty",
                self.flag_validation != "empty",
                self.flag_phenotype_match != "empty",
                self.flag_summary != "empty",
            )
        )

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            position=self.position,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    class Meta:
        unique_together = ("release", "chromosome", "position", "reference", "alternative", "case")


class SmallVariantQueryBase(models.Model):
    """Base class for models storing queries to the ``SmallVariant`` model.

    Saving the query settings is implemented as a JSON plus a version field.  This design was chosen to allow for
    less rigid upgrade paths of the form schema itself.  Further, we will need a mechanism for upgrading the form
    "schemas" automatically and then storing the user settings.
    """

    #: DateTime of query.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: Query UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: User who created the query.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
        help_text="User who created the query",
    )

    #: The identifier of the form
    form_id = models.CharField(max_length=100, null=False, help_text="Identifier of the form")

    #: The version of the form when saving.
    form_version = models.IntegerField(null=False, help_text="Version of form when saving")

    #: The query settings as JSON.
    query_settings = JSONField(null=False, help_text="The query settings")

    #: Many-to-Many relationship with SmallVariant to store query results for faster future retrieval
    query_results = models.ManyToManyField(SmallVariant)

    #: Optional, user-assign query name.
    name = models.CharField(
        max_length=100, null=True, default=None, help_text="Optional user-assigned name"
    )

    #: Flag for being public or not.
    public = models.BooleanField(
        null=False, default=False, help_text="Case is flagged as public or not"
    )

    class Meta:
        abstract = True
        ordering = ("-date_created",)

    def is_prioritization_enabled(self):
        """Return whether prioritization is enabled in this query."""
        return all(
            (
                self.query_settings.get("prio_enabled"),
                self.query_settings.get("prio_algorithm"),
                self.query_settings.get("prio_hpo_terms", []),
            )
        )


class SmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of single-case queries to the ``SmallVariant`` model.
    """

    # TODO: rename to reflect single-case

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="small_variant_queries",
        help_text="The case that the query relates to",
    )


class ClinvarQuery(SmallVariantQueryBase):
    """Allow saving of clinvar queries.
    """

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="clinvar_queries",
        help_text="The case that the query relates to",
    )


class ProjectCasesSmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of whole-project queries to the ``SmallVariant`` model.

    """

    #: The related case.
    project = models.ForeignKey(
        CaseAwareProject,
        null=False,
        related_name="small_variant_queries",
        help_text="The project that the query relates to",
    )


class SmallVariantQueryGeneScores(models.Model):
    """Annotate ``SmallVariantQuery`` with gene scores (if configured to do so)."""

    #: The query to annotate.
    query = models.ForeignKey(SmallVariantQuery)

    #: The Entrez gene ID.
    gene_id = models.CharField(max_length=64, null=False, blank=False, help_text="Entrez gene ID")

    #: The gene symbol.
    gene_symbol = models.CharField(
        max_length=128, null=False, blank=False, help_text="The gene symbol"
    )

    #: The priority type.
    priority_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The priority type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The gene score")


class FilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing single case filter query and storing query results in table SmallVariantQueryBase."""

    #: Task description for logging.
    task_desc = "Single case filter query and store results"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="filter_bg_job",
        help_text="Background job for filtering and storing query results",
    )

    case = models.ForeignKey(Case, null=False, help_text="The case to filter")

    #: Link to the smallvariantquery object. Holds query arguments and results
    smallvariantquery = models.ForeignKey(
        SmallVariantQuery, null=False, help_text="Query that is executed."
    )

    def get_human_readable_type(self):
        return "Single-case query results"

    def get_absolute_url(self):
        return reverse(
            "variants:filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ClinvarBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing clinvar filter query and storing query results in table SmallVariantQueryBase."""

    #: Task description for logging.
    task_desc = "Clinvar query and store results"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clinvar_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="clinvar_bg_job",
        help_text="Background job for clinvar filtering and storing query results",
    )

    case = models.ForeignKey(Case, null=False, help_text="The case to filter")

    #: Link to the smallvariantquery object. Holds query arguments and results
    clinvarquery = models.ForeignKey(ClinvarQuery, null=False, help_text="Query that is executed.")

    def get_human_readable_type(self):
        return "Clinvar query results"

    def get_absolute_url(self):
        return reverse(
            "variants:clinvar-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ProjectCasesFilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing joint project filter query and storing query results in table SmallVariantQueryBase."""

    #: Task description for logging.
    task_desc = "Joint project filter query and store results."

    #: String identifying model in BackgroundJob.
    spec_name = "variants.project_cases_filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="project_cases_filter_bg_job",
        help_text="Background job for filtering joint project and storing query results.",
    )

    #: Link to the ProjectCaseSmallVariantQuery object. Holds query arguments and results.
    projectcasessmallvariantquery = models.ForeignKey(
        ProjectCasesSmallVariantQuery, null=False, help_text="Query that is executed."
    )

    def get_human_readable_type(self):
        return "Joint project query results"

    def get_absolute_url(self):
        return reverse(
            "variants:project-cases-filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class CaseVariantStats(models.Model):
    """Statistics on various aspects of variants of a case:

    - Ts/Tv ratio
    """

    #: The related ``Case``.
    case = models.OneToOneField(
        Case,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this case",
    )


class SampleVariantStatistics(models.Model):
    """Single-number variant statistics for donors in a ``Case`` via ``CaseVariantStats``."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="sample_variant_stats",
        help_text="Single-value variant statistics for one individual",
    )

    #: The name of the donor.
    sample_name = models.CharField(max_length=200, null=False)

    #: The number of on-target transitions (A <-> G, C <-> T).
    ontarget_transitions = models.IntegerField(null=False)
    #: The number of on-target transversions.
    ontarget_transversions = models.IntegerField(null=False)

    #: The number of on-target SNVs
    ontarget_snvs = models.IntegerField(null=False)
    #: The number of on-target Indels
    ontarget_indels = models.IntegerField(null=False)
    #: The number of on-target MNVs
    ontarget_mnvs = models.IntegerField(null=False)

    #: Counts for the different variant effects
    ontarget_effect_counts = JSONField(null=False)

    #: Histogram of indel sizes.
    ontarget_indel_sizes = JSONField(null=False)
    #: Histogram of read depths.
    ontarget_dps = JSONField(null=False)
    #: 5-value summary of on-target read depths.
    ontarget_dp_quantiles = ArrayField(models.FloatField(), size=5)

    #: Overall het ratio.
    het_ratio = models.FloatField(null=False)
    #: Hom/het ratio on chrX in PAR1 and PAR2, for sex checking.
    chrx_het_hom = models.FloatField(null=False)

    def ontarget_ts_tv_ratio(self):
        """Compute Ts/Tv ratio."""
        if not self.ontarget_transversions:
            return 0.0
        else:
            return self.ontarget_transitions / self.ontarget_transversions

    class Meta:
        ordering = ("sample_name",)


class BaseRelatedness(models.Model):
    """Shared functionality of relatedness of individuals in a collective.

    This could be a pedigree or a project.
    """

    #: First sample.
    sample1 = models.CharField(max_length=200, null=False)
    #: Second sample.
    sample2 = models.CharField(max_length=200, null=False)

    #: The Het_1_2 statistic
    het_1_2 = models.IntegerField(null=False)
    #: The Het_1 statistic
    het_1 = models.IntegerField(null=False)
    #: The Het_2 statistic
    het_2 = models.IntegerField(null=False)
    #: The N_IBS0 statistic
    n_ibs0 = models.IntegerField(null=False)
    #: The N_IBS1 statistic
    n_ibs1 = models.IntegerField(null=False)
    #: The N_IBS2 statistic
    n_ibs2 = models.IntegerField(null=False)

    def relatedness(self):
        """Return relatedness following Pedersen and Quinlan (2017)."""
        return (self.het_1_2 - 2 * self.n_ibs0) * 2 / math.sqrt(self.het_1 * self.het_2)

    class Meta:
        abstract = True
        ordering = ("sample1", "sample2")


class PedigreeRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a pedigree/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
    )


class ProjectVariantStats(models.Model):
    """Statistics on various aspects of variants of all cases in a project."""

    #: The related ``Project``.
    project = models.OneToOneField(
        Project,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this projects",
    )


class ProjectRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a case/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        ProjectVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
    )


class ComputeProjectVariantsStatsBgJob(JobModelMessageMixin, models.Model):
    """Background job for computing project variants statistics."""

    #: Task description for logging.
    task_desc = "Compute project-wide variants statistics"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.compute_project_variants_stats"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Job Specialization SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="compute_project_variants_stats",
        help_text="Background job for state etc.",
    )

    def get_human_readable_type(self):
        return "Project-wide Variant Statistics Computation"

    def get_absolute_url(self):
        return reverse(
            "variants:project-stats-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


# TODO: Improve wrapper so we can assign obj.phenotype_rank and score
class RowWithPhenotypeScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for phenotype score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_phenotype_rank = None
        self._self_phenotype_score = -1

    @property
    def phenotype_rank(self):
        return self._self_phenotype_rank

    @property
    def phenotype_score(self):
        return self._self_phenotype_score

    def __getitem__(self, key):
        if key == "phenotype_rank":
            return self.phenotype_rank
        elif key == "phenotype_score":
            return self.phenotype_score
        else:
            return self.__wrapped__.__getitem__(key)


def annotate_with_phenotype_scores(rows, gene_scores):
    """Annotate the results in ``rows`` with phenotype scores stored in ``small_variant_query``.
    """
    rows = [RowWithPhenotypeScore(row) for row in rows]
    for row in rows:
        row._self_phenotype_score = gene_scores.get(row.entrez_id, -1)
    rows.sort(key=lambda row: (row._self_phenotype_score, row.entrez_id or ""), reverse=True)
    # Re-compute ranks
    prev_gene = None
    rank = 1
    for row in rows:
        row._self_phenotype_rank = rank
        if row.entrez_id != prev_gene:
            prev_gene = row.entrez_id
            rank += 1
    return rows


def prioritize_genes(entrez_ids, query_settings):
    """Perform gene prioritization query.

    Yield quadruples (gene id, gene symbol, score, priority type) for the given gene list and query settings.
    """
    if not settings.VARFISH_ENABLE_EXOMISER_PRIORITISER:
        return

    prio_enabled = query_settings.get("prio_enabled")
    prio_algorithm = query_settings.get("prio_algorithm")
    hpo_terms = tuple(sorted(query_settings.get("prio_hpo_terms", [])))
    entrez_ids = tuple(
        list(sorted(set(entrez_ids)))[: settings.VARFISH_EXOMISER_PRIORITISER_MAX_GENES]
    )
    if not all((prio_enabled, prio_algorithm, hpo_terms, entrez_ids)):
        return  # nothing to do

    res = requests.request(
        method="get",
        url=settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
        params={"phenotypes": hpo_terms, "genes": entrez_ids, "prioritiser": prio_algorithm},
    )

    for entry in res.json().get("results", ()):
        yield entry["geneId"], entry["geneSymbol"], entry["score"], entry["priorityType"]

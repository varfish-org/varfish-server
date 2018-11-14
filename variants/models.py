import uuid as uuid_object

from postgres_copy import CopyManager

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_delete

from projectroles.models import Project

from bgjobs.models import BackgroundJob, JOB_STATE_DONE, JOB_STATE_FAILED, JOB_STATE_RUNNING

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class SmallVariant(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    var_type = models.CharField(max_length=8)
    case_id = models.IntegerField()
    genotype = JSONField()
    in_clinvar = models.NullBooleanField()
    exac_frequency = models.FloatField(null=True)
    exac_homozygous = models.IntegerField(null=True)
    exac_heterozygous = models.IntegerField(null=True)
    exac_hemizygous = models.IntegerField(null=True)
    thousand_genomes_frequency = models.FloatField(null=True)
    thousand_genomes_homozygous = models.IntegerField(null=True)
    thousand_genomes_heterozygous = models.IntegerField(null=True)
    thousand_genomes_hemizygous = models.IntegerField(null=True)
    gnomad_exomes_frequency = models.FloatField(null=True)
    gnomad_exomes_homozygous = models.IntegerField(null=True)
    gnomad_exomes_heterozygous = models.IntegerField(null=True)
    gnomad_exomes_hemizygous = models.IntegerField(null=True)
    gnomad_genomes_frequency = models.FloatField(null=True)
    gnomad_genomes_homozygous = models.IntegerField(null=True)
    gnomad_genomes_heterozygous = models.IntegerField(null=True)
    gnomad_genomes_hemizygous = models.IntegerField(null=True)
    refseq_gene_id = models.CharField(max_length=16, null=True)
    refseq_transcript_id = models.CharField(max_length=16, null=True)
    refseq_transcript_coding = models.NullBooleanField()
    refseq_hgvs_c = models.CharField(max_length=512, null=True)
    refseq_hgvs_p = models.CharField(max_length=512, null=True)
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    ensembl_transcript_id = models.CharField(max_length=16, null=True)
    ensembl_transcript_coding = models.NullBooleanField()
    ensembl_hgvs_c = models.CharField(max_length=512, null=True)
    ensembl_hgvs_p = models.CharField(max_length=512, null=True)
    ensembl_effect = ArrayField(models.CharField(max_length=64, null=True))
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
            # index for base query
            models.Index(
                fields=[
                    "exac_frequency",
                    "gnomad_exomes_frequency",
                    "gnomad_genomes_frequency",
                    "thousand_genomes_frequency",
                    "exac_homozygous",
                    "gnomad_exomes_homozygous",
                    "gnomad_genomes_homozygous",
                    "thousand_genomes_homozygous",
                    "refseq_effect",
                ]
            ),
            models.Index(
                fields=[
                    "exac_frequency",
                    "gnomad_exomes_frequency",
                    "gnomad_genomes_frequency",
                    "thousand_genomes_frequency",
                    "exac_homozygous",
                    "gnomad_exomes_homozygous",
                    "gnomad_genomes_homozygous",
                    "thousand_genomes_homozygous",
                    "ensembl_effect",
                ]
            ),
            # for join with clinvar, dbsnp
            models.Index(fields=["release", "chromosome", "position", "reference", "alternative"]),
            # for join with annotation
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                    "ensembl_gene_id",
                ]
            ),
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                    "refseq_gene_id",
                ]
            ),
            # for join with hgnc
            models.Index(fields=["ensembl_gene_id"]),
            models.Index(fields=["refseq_gene_id"]),
            # for join with case
            models.Index(fields=["case_id"]),
            # for filter query
            GinIndex(fields=["case_id", "refseq_effect"]),
            GinIndex(fields=["case_id", "ensembl_effect"]),
            models.Index(fields=["case_id", "in_clinvar"]),
        ]


class Case(models.Model):
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    name = models.CharField(max_length=512)
    index = models.CharField(max_length=32)
    pedigree = JSONField()
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

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

    def get_members(self):
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

    def __str__(self):
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


#: File type choices for ``ExportFileBgJob``.
EXPORT_TYPE_CHOICE_TSV = "tsv"
EXPORT_TYPE_CHOICE_XLSX = "xlsx"
EXPORT_FILE_TYPE_CHOICES = (
    (EXPORT_TYPE_CHOICE_TSV, "TSV File"),
    (EXPORT_TYPE_CHOICE_XLSX, "Excel File (XLSX)"),
)


class ExportFileBgJob(models.Model):
    """Background job for exporting query results as a TSV or Excel file."""

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="export_file_bg_job",
        help_text="Background job for state etc.",
    )
    case = models.ForeignKey(Case, null=False, help_text="The case to export")
    query_args = JSONField(null=False, help_text="(Validated) query parameters")
    file_type = models.CharField(
        max_length=32, choices=EXPORT_FILE_TYPE_CHOICES, help_text="File types for exported file"
    )

    def mark_start(self):
        """Mark the export job as started."""
        self.bg_job.status = JOB_STATE_RUNNING
        self.bg_job.add_log_entry("Starting export to file")
        self.bg_job.save()

    def mark_error(self, msg):
        """Mark the export job as complete successfully."""
        self.bg_job.status = JOB_STATE_FAILED
        self.bg_job.add_log_entry("Exporting to file failed: {}".format(msg))
        self.bg_job.save()

    def mark_success(self):
        """Mark the export job as complete successfully."""
        self.bg_job.status = JOB_STATE_DONE
        self.bg_job.add_log_entry("Exporting to file succeeded")
        self.bg_job.save()

    def add_log_entry(self, *args, **kwargs):
        return self.bg_job.add_log_entry(*args, **kwargs)

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

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        try:
            SmallVariant.objects.get(
                case_id=self.case.pk,
                release=self.release,
                chromosome=self.chromosome,
                position=self.position,
                reference=self.reference,
                alternative=self.alternative,
            )
        except SmallVariant.DoesNotExit as e:
            raise ValidationError("No corresponding variant in case") from e


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
            )
        )

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        try:
            SmallVariant.objects.get(
                case_id=self.case.pk,
                release=self.release,
                chromosome=self.chromosome,
                position=self.position,
                reference=self.reference,
                alternative=self.alternative,
            )
        except SmallVariant.DoesNotExit as e:
            raise ValidationError("No corresponding variant in case") from e

    class Meta:
        unique_together = ("release", "chromosome", "position", "reference", "alternative", "case")
        indexes = [
            # index for base query
            models.Index(fields=["release", "chromosome", "position", "reference", "alternative"])
        ]

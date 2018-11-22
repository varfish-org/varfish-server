import re
import uuid as uuid_object

from postgres_copy import CopyManager

from django.db import models
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
            # For query: select all variants for a case.
            models.Index(fields=["case_id"]),
            # Filter query: the most important thing is to reduce the variants for a case quickly. It's questionable
            # how much adding homozygous/frequency really adds here.  Adding them back should only done when we
            # know that it helps.
            GinIndex(fields=["case_id", "refseq_effect"]),
            GinIndex(fields=["case_id", "ensembl_effect"]),
            models.Index(fields=["case_id", "in_clinvar"]),
        ]


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

    # Set manager for custom queries
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


class ExportFileBgJob(JobModelMessageMixin, models.Model):
    """Background job for exporting query results as a TSV or Excel file."""

    #: String identifying model in BackgroundJob.
    spec_name = "variants.export_file_bg_job"

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

    def get_human_readable_type(self):
        """Implement to implement a human-readable type in the views."""
        return "File Export"

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


class DistillerSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to MutationDistiller."""

    #: String identifying model in BackgroundJob.
    spec_name = "variants.export_file_bg_job"

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
        """Implement to implement a human-readable type in the views."""
        return "MutationDistiller Submission"

    def get_distiller_project_url(self):
        """Returns URL to MutationDistiller project if ``distiller_project_id`` is set.

        Returns ``None`` otherwise.
        """
        if self.distiller_project_id:
            return (
                "https://mutationdistiller.org/temp/QE/vcf_%s/progress.html"
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
    #: The annotated gene.
    ensembl_gene_id = models.CharField(max_length=64)

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
        try:
            SmallVariant.objects.get(
                case_id=self.case.pk,
                release=self.release,
                chromosome=self.chromosome,
                position=self.position,
                reference=self.reference,
                alternative=self.alternative,
                ensembl_gene_id=self.ensembl_gene_id,
            )
        except SmallVariant.DoesNotExist as e:
            raise ValidationError("No corresponding variant in case") from e

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
            "case",
            "ensembl_gene_id",
        )
        indexes = (
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                    "case",
                    "ensembl_gene_id",
                ]
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
    #: The annotated gene.
    ensembl_gene_id = models.CharField(max_length=64)

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
        try:
            SmallVariant.objects.get(
                case_id=self.case.pk,
                release=self.release,
                chromosome=self.chromosome,
                position=self.position,
                reference=self.reference,
                alternative=self.alternative,
                ensembl_gene_id=self.ensembl_gene_id,
            )
        except SmallVariant.DoesNotExist as e:
            raise ValidationError("No corresponding variant in case") from e

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
            "case",
            "ensembl_gene_id",
        )


class SmallVariantQuery(models.Model):
    """Allow saving of queries to the ``SmallVariant`` model.

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

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="small_variant_queries",
        help_text="The case that the query relates to",
    )

    #: User who created the query.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="small_variant_queries",
        help_text="User who created the query",
    )

    #: The identifier of the form
    form_id = models.CharField(max_length=100, null=False, help_text="Identifier of the form")

    #: The version of the form when saving.
    form_version = models.IntegerField(null=False, help_text="Version of form when saving")

    #: The query settings as JSON.
    query_settings = JSONField(null=False, help_text="The query settings")

    #: Optional, user-assign query name.
    name = models.CharField(
        max_length=100, null=True, default=None, help_text="Optional user-assigned name"
    )

    #: Flag for being public or not.
    public = models.BooleanField(
        null=False, default=False, help_text="Case is flagged as public or not"
    )

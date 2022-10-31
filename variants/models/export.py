"""Code for export of query results."""
import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.db import models
from django.urls import reverse

from varfish.utils import JSONField
from variants.models.projectroles import Project

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
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
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
    case = models.ForeignKey(
        "Case", on_delete=models.CASCADE, null=False, help_text="The case to export"
    )

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
        on_delete=models.CASCADE,
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

    #: Cohort to export
    cohort = models.ForeignKey("cohorts.Cohort", on_delete=models.CASCADE, null=True)

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
        on_delete=models.CASCADE,
        related_name="export_result",
        null=False,
        help_text="Related file export job",
    )
    expiry_time = models.DateTimeField(help_text="Time at which the file download expires")
    payload = models.BinaryField(help_text="Resulting exported file")

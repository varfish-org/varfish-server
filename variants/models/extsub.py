"""Code supporting submission to external tools.

This will eventually go into their own apps via a plugin.
"""

import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.db import models
from django.urls import reverse

from varfish.utils import JSONField
from variants.models.projectroles import Project


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
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="distiller_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        "Case", on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
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


class CaddSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to CADD."""

    #: Task description for logging.
    task_desc = "Submission to CADD"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.cadd_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="cadd_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        "Case", on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    cadd_version = models.CharField(
        max_length=100, help_text="The CADD version used for the annotation"
    )

    cadd_job_id = models.CharField(
        max_length=100,
        null=True,
        help_text="The project ID that CADD assigned on submission",
    )

    def get_human_readable_type(self):
        return "CADD Submission"

    def get_cadd_result_url(self):
        """Returns URL to CADD result download if ``cadd_job_id`` is set.

        Returns ``None`` otherwise.
        """
        if self.cadd_job_id:
            return "https://cadd.gs.washington.edu/check_avail/%s_anno_%s.tsv.gz" % (
                self.cadd_version,
                self.cadd_job_id,
            )
        else:
            return None

    def get_absolute_url(self):
        return reverse(
            "variants:cadd-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SpanrSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to SPANR."""

    #: Task description for logging.
    task_desc = "Submission to SPANR"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.spanr_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="spanr_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        "Case", on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    spanr_job_url = models.CharField(max_length=100, null=True, help_text="The SPANR job URL")

    def get_human_readable_type(self):
        return "SPANR Submission"

    def get_absolute_url(self):
        return reverse(
            "variants:spanr-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )

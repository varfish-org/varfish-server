"""Code for supporting maintenance jobs."""

import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, models, transaction, utils
from django.urls import reverse

User = get_user_model()


class SiteBgJobBase(JobModelMessageMixin, models.Model):
    """Base class for global (site-wide) background jobs of the Variants module."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
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
        return "Site-wide Maintenance"

    class Meta:
        ordering = ("-date_created", "pk")
        abstract = True


class ClearExpiredExportedFilesBgJob(SiteBgJobBase):
    """Background job for clearing expired exported files."""

    #: Task description for logging.
    task_desc = "Clearing expired exported files"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_expired_exported_files_bg_job"

    def get_absolute_url(self):
        return reverse(
            "variants:clear-expired-job-detail",
            kwargs={"job": self.sodar_uuid},
        )


class ClearInactiveVariantSetsBgJob(SiteBgJobBase):
    """Background job for clearing inactive variant sets."""

    #: Task description for logging.
    task_desc = "Clearing inactive variant sets"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_inactive_variant_sets_bg_job"

    def get_absolute_url(self):
        return reverse(
            "variants:clear-inactive-variant-set-job",
            kwargs={"job": self.sodar_uuid},
        )


class RefreshSmallVariantSummaryBgJob(SiteBgJobBase):
    """Background job for refreshing small variant summaries."""

    #: Task description for logging.
    task_desc = 'Refreshing small variant summaries (aka "in-house database")'

    #: String identifying model in BackgroundJob.
    spec_name = "variants.refresh_small_variant_summaries"

    def get_absolute_url(self):
        return reverse(
            "variants:refresh-small-variant-summaries-job-detail",
            kwargs={"job": self.sodar_uuid},
        )


def refresh_variants_smallvariantsummary():
    """Refresh the ``SmallVariantSummary`` materialized view."""

    with transaction.atomic():
        bg_job = BackgroundJob.objects.create(
            name='Refreshing small variant summaries (aka "in-house database")',
            project=None,
            job_type=RefreshSmallVariantSummaryBgJob.spec_name,
            user=User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER),
        )
        refresh_job = RefreshSmallVariantSummaryBgJob.objects.create(bg_job=bg_job)
    with refresh_job.marks():
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

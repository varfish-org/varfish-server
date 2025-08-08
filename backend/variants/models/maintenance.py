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


def drop_variants_smallvariantsummary():
    """Drop the ``SmallVariantSummary`` materialized view."""

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DROP MATERIALIZED VIEW IF EXISTS variants_smallvariantsummary")


SQL_OUTER = r"""
DROP MATERIALIZED VIEW IF EXISTS variants_smallvariantsummary;

CREATE MATERIALIZED VIEW variants_smallvariantsummary
AS
    %s
WITH NO DATA;

CREATE UNIQUE INDEX variants_smallvariantsummary_id ON variants_smallvariantsummary(id);
CREATE INDEX variants_smallvariantsummary_coord ON variants_smallvariantsummary(
    release, chromosome, start, "end", bin, reference, alternative
);
"""


SQL_INNER = r"""
WITH excluded_case_ids AS (
    SELECT DISTINCT variants_case.id AS case_id
    FROM variants_case
    JOIN projectroles_project ON variants_case.project_id = projectroles_project.id
    JOIN projectroles_appsetting ON
        projectroles_project.id = projectroles_appsetting.project_id AND
        projectroles_appsetting.name = 'exclude_from_inhouse_db' AND
        projectroles_appsetting.value = '1'
)
SELECT
    row_number() OVER (PARTITION BY true) AS id,
    release,
    chromosome,
    start,
    "end",
    bin,
    reference,
    alternative,
    sum(num_hom_ref) AS count_hom_ref,
    sum(num_het) AS count_het,
    sum(num_hom_alt) AS count_hom_alt,
    sum(num_hemi_ref) AS count_hemi_ref,
    sum(num_hemi_alt) AS count_hemi_alt
FROM (
    SELECT DISTINCT
        variants.release,
        variants.chromosome,
        variants.start,
        variants."end",
        variants.bin,
        variants.reference,
        variants.alternative,
        variants.num_hom_ref,
        variants.num_het,
        variants.num_hom_alt,
        variants.num_hemi_ref,
        variants.num_hemi_alt,
        variants.case_id
    FROM variants_smallvariant AS variants
    WHERE NOT EXISTS (SELECT 1 from excluded_case_ids AS e WHERE e.case_id = variants.case_id)
) AS variants_per_case
GROUP BY (release, chromosome, start, "end", bin, reference, alternative)
"""


def create_variants_smallvariantsummary():
    """Create the ``SmallVariantSummary`` materialized view."""

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(SQL_OUTER % SQL_INNER)

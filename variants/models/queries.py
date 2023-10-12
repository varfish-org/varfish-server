"""Models for small variant queries."""

import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from varfish.utils import JSONField
from variants.models import Case
from variants.models.projectroles import CaseAwareProject, Project

User = get_user_model()


class SmallVariantQueryBase(models.Model):
    """Base class for models storing queries to the ``SmallVariant`` model.

    Saving the query settings is implemented as a JSON plus a version field.  This design was chosen to allow for
    less rigid upgrade paths of the form schema itself.  Further, we will need a mechanism for upgrading the form
    "schemas" automatically and then storing the user settings.
    """

    class QueryState(models.TextChoices):
        INITIAL = "initial", "initial"
        RUNNING = "running", "running"
        DONE = "done", "done"
        CANCELLED = "cancelled", "cancelled"
        FAILED = "failed", "failed"
        TIMEOUT = "timeout", "timeout"

    #: DateTime of query.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: Query UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: User who created the query.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
        help_text="User who created the query",
    )

    #: The query settings as JSON.
    query_settings = JSONField(null=False, help_text="The query settings")

    #: Many-to-Many relationship with SmallVariant to store query results for faster future retrieval
    query_results = models.ManyToManyField("SmallVariant")

    #: The current query state.
    query_state = models.CharField(
        max_length=64,
        choices=QueryState.choices,
        default=QueryState.INITIAL,
        help_text="The current query state",
    )

    #: A message related to the query state.
    query_state_msg = models.TextField(
        null=True, blank=True, help_text="Message related to the query state"
    )

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

    def query_type(self):
        raise NotImplementedError("Implement me!")


class SmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of single-case queries to the ``SmallVariant`` model."""

    # TODO: rename to reflect single-case

    #: The related case.
    case = models.ForeignKey(
        "Case",
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_queries",
        help_text="The case that the query relates to",
    )

    def query_type(self):
        return "smallvariantquery"

    def get_project(self):
        return self.case.project


class SmallVariantQueryResultSet(models.Model):
    """Store SmallVariant query results set"""

    #: Query UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")
    #: DateTime of record creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of record modification.
    date_modified = models.DateTimeField(auto_now_add=True, help_text="DateTime of modification")

    #: The query that this result is for.
    smallvariantquery = models.ForeignKey(
        SmallVariantQuery,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The query that this result is for",
    )

    #: The number of rows in the result.
    result_row_count = models.IntegerField(
        null=False, blank=False, help_text="Number of rows in the result"
    )

    #: The start time.
    start_time = models.DateTimeField(help_text="Date time of query start")

    #: The end time.
    end_time = models.DateTimeField(help_text="Date time of query end")

    #: The elapsed seconds.
    elapsed_seconds = models.FloatField(help_text="Elapsed seconds")

    #: The case that this result is for, in case smallvariantquery is null.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The case that this result is for",
    )

    def get_project(self):
        if self.case:
            return self.case.project
        return self.smallvariantquery.case.project

    class Meta:
        ordering = ("-date_created",)


class SmallVariantQueryResultRow(models.Model):
    """A row in ``SmallVariantQueryResultSet``.

    Some basic information is stored directly as record properties, e.g., for sorting.  A full JSON dump of the
    resulting record with all annotation information is stored in the JSON field ``payload``.
    """

    #: Row UUID
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")

    #: Foreign key to the owning SvQueryResultSet
    smallvariantqueryresultset = models.ForeignKey(
        SmallVariantQueryResultSet,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="The owning SmallVariantQueryResultSet",
    )

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: The bin for indexing
    bin = models.IntegerField()
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: The query result rows.
    payload = JSONField(null=False, help_text="The query result rows")

    class Meta:
        ordering = ("chromosome_no", "start", "end")


class ProjectCasesSmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of whole-project queries to the ``SmallVariant`` model."""

    #: The related case.
    project = models.ForeignKey(
        CaseAwareProject,
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_queries",
        help_text="The project that the query relates to",
    )

    def query_type(self):
        return "projectcasessmallvariantquery"


class FilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing single case filter query and storing query results in table
    SmallVariantQueryBase.
    """

    #: Task description for logging.
    task_desc = "Single case filter query and store results"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="filter_bg_job",
        help_text="Background job for filtering and storing query results",
        on_delete=models.CASCADE,
    )

    case = models.ForeignKey(
        "Case", on_delete=models.CASCADE, null=False, help_text="The case to filter"
    )

    #: Link to the smallvariantquery object. Holds query arguments and results
    smallvariantquery = models.ForeignKey(
        SmallVariantQuery, on_delete=models.CASCADE, null=False, help_text="Query that is executed."
    )

    def get_human_readable_type(self):
        return "Single-case query results"

    def get_absolute_url(self):
        return reverse(
            "variants:filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ProjectCasesFilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing joint project filter query and storing query results in table
    SmallVariantQueryBase.
    """

    #: Task description for logging.
    task_desc = "Joint project filter query and store results."

    #: String identifying model in BackgroundJob.
    spec_name = "variants.project_cases_filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="project_cases_filter_bg_job",
        help_text="Background job for filtering joint project and storing query results.",
        on_delete=models.CASCADE,
    )

    #: Link to the ProjectCaseSmallVariantQuery object. Holds query arguments and results.
    projectcasessmallvariantquery = models.ForeignKey(
        ProjectCasesSmallVariantQuery,
        on_delete=models.CASCADE,
        null=False,
        help_text="Query that is executed.",
    )

    cohort = models.ForeignKey(
        "cohorts.Cohort",
        on_delete=models.CASCADE,
        null=True,
        related_name="project_cases_filter_bg_job",
    )

    def get_human_readable_type(self):
        return "Joint project query results"

    def get_absolute_url(self):
        return reverse(
            "variants:project-cases-filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )

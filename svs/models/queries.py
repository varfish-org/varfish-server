"""Models and supporting codes for storing SV queries."""

import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.db import models

from svs.models.records import SV_SUB_TYPE_CHOICES, SV_TYPE_CHOICES
from varfish.utils import JSONField
from variants.models import Case

User = get_user_model()


class SvQuery(models.Model):
    """Store SV query"""

    class QueryState(models.TextChoices):
        INITIAL = "initial", "initial"
        RUNNING = "running", "running"
        DONE = "done", "done"
        CANCELLED = "cancelled", "cancelled"
        FAILED = "failed", "failed"
        TIMEOUT = "timeout", "timeout"

    #: Query UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")
    #: DateTime of record creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of record modification.
    date_modified = models.DateTimeField(auto_now_add=True, help_text="DateTime of modification")

    #: User who created the query.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
        help_text="User who created the query",
    )

    #: The case that this query refers to.
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case that this query refers to"
    )

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

    #: The query settings as JSON.
    query_settings = JSONField(null=False, help_text="The query settings")

    def get_project(self):
        return self.case.project

    class Meta:
        ordering = ("-date_created",)


class SvQueryResultSet(models.Model):
    """Store SV query results set"""

    #: Query UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")
    #: DateTime of record creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of record modification.
    date_modified = models.DateTimeField(auto_now_add=True, help_text="DateTime of modification")

    #: The query that this result is for.
    svquery = models.ForeignKey(
        SvQuery,
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
        return self.svquery.case.project

    class Meta:
        ordering = ("-date_created",)


class SvQueryResultRow(models.Model):
    """A row in ``SvQueryResultSet``.

    Some basic information is stored directly as record properties, e.g., for sorting.  A full JSON dump of the
    resulting record with all annotation information is stored in the JSON field ``payload``.
    """

    #: Row UUID
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")

    #: Foreign key to the owning SvQueryResultSet
    svqueryresultset = models.ForeignKey(
        SvQueryResultSet,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="The owning SvQueryResultSet",
    )

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: The bin for indexing in case of linear SVs, in case of non-linear SVs the bin of pos.
    bin = models.IntegerField()
    #: Variant coordinates - chromosome of end position (equal to ``chromosome`` for linear variants)
    chromosome2 = models.CharField(max_length=32, null=True)
    #: Chromosome as number - of end position (equal to ``chromosome_no`` for linear variants)
    chromosome_no2 = models.IntegerField(null=True)
    #: In case of non-linear variants, the bin of end, otherwise equal to ``bin``.
    bin2 = models.IntegerField(null=True)

    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Paired-end orientation of SV, one of "3to3", "3to5", "5to3", or "5to5", or None.
    pe_orientation = models.CharField(max_length=32, null=True, blank=True)

    #: Type of structural variant
    sv_type = models.CharField(max_length=32, choices=SV_TYPE_CHOICES)
    #: Sub type of structural variant
    sv_sub_type = models.CharField(max_length=32, choices=SV_SUB_TYPE_CHOICES)

    #: The query result rows.
    payload = JSONField(null=False, help_text="The query result rows")

    class Meta:
        ordering = ("chromosome_no", "start", "end")

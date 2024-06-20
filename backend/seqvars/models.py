import typing
import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django_pydantic_field import SchemaField
import pydantic

from cases.models import CaseAnalysisSession
from seqmeta.models import EnrichmentKit
from variants.models import Case
from variants.models.projectroles import Project

#: User model.
User = get_user_model()


class BaseModel(models.Model):
    """Base model with sodar_uuid and creation/update time."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SeqvarQueryPresetsSet(BaseModel):
    """Configured presets for a given project."""

    #: The project that this preset set is for.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: Title of the presets.
    title = models.CharField(max_length=128)
    #: Description of the presets.
    description = models.TextField(null=True)


class SeqvarPresetsBase(BaseModel):
    """Base presets."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: Title of the presets.
    title = models.CharField(max_length=128)
    #: Description of the presets.
    description = models.TextField(null=True)

    class Meta:
        abstract = True


class SeqvarPresetsFrequency(SeqvarPresetsBase):
    """Presets for frequency settings within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsConsequence(SeqvarPresetsBase):
    """Presets for consequence-related settings within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsLocus(SeqvarPresetsBase):
    """Presets for locus-related settings within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsPhenotypePrio(SeqvarPresetsBase):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsVariantPrio(SeqvarPresetsBase):
    """Presets for variant pathogenicity--related settings within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsColumns(SeqvarPresetsBase):
    """Presets for columns presets within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarPresetsMisc(SeqvarPresetsBase):
    """Presets for miscellaneous presets within a ``QueryPresetsSet``."""

    # TODO: JSON field with pydantic model


class SeqvarQuerySettings(BaseModel):
    """The query settings for a given query."""

    # TODO: JSON field with pydantic model


class SeqvarQuery(BaseModel):
    """Allows users to prepare seqvar queries for execution and execute them."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: The title of the query.
    title = models.CharField(max_length=128)

    #: Owning/containing session.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)
    #: Buffer with settings to be edited in the next query execution.
    settings_buffer = models.ForeignKey(SeqvarQuerySettings, on_delete=models.CASCADE)


class SeqvarQueryExecution(BaseModel):
    """Hold the state, query settings, and results for running one seqvar query."""

    #: Initial status.
    STATE_INITIAL = "initial"
    #: Queued and waiting for execution.
    STATE_QUEUED = "queued"
    #: Currently being executed.
    STATE_RUNNING = "running"
    #: Completed with failure.
    STATE_FAILED = "failed"
    #: Completed after being canceled by user.
    STATE_CANCELED = "canceled"
    #: Completed with success.
    STATE_DONE = "done"
    #: Choices for the ``state`` field.
    STATE_CHOICES = (
        (STATE_INITIAL, STATE_INITIAL),
        (STATE_QUEUED, STATE_QUEUED),
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FAILED, STATE_FAILED),
        (STATE_CANCELED, STATE_CANCELED),
        (STATE_DONE, STATE_DONE),
    )

    #: State of the query execution.
    state = models.CharField(max_length=64, choices=STATE_CHOICES)
    #: Estimate for completion, if given.
    complete_percent = models.IntegerField(null=True)
    #: The start time.
    start_time = models.DateTimeField(null=True)
    #: The end time.
    end_time = models.DateTimeField(null=True)
    #: The elapsed seconds.
    elapsed_seconds = models.FloatField(null=True)

    #: The owning/containing query.
    query = models.ForeignKey(SeqvarQuery, on_delete=models.CASCADE)
    #: Effective query settings of execution.
    querysettings = models.ForeignKey(SeqvarQuerySettings, on_delete=models.CASCADE)


class DataSourceInfo(pydantic.BaseModel):
    """Describes the version version of a given datasource."""

    #: The name.
    name: str
    #: The version.
    version: str


class DataSourceInfos(pydantic.BaseModel):
    """Container for ``DataSourceInfo`` records."""

    #: Information about the used datasources.
    infos: list[DataSourceInfo]


class SeqvarResultSet(BaseModel):
    """Store result rows and version information about the query."""

    #: The owning query execution.
    queryexecution = models.ForeignKey(SeqvarQueryExecution, on_delete=models.CASCADE)
    #: The number of rows in the result.
    result_row_count = models.IntegerField(null=False, blank=False)
    #: Information about the data sources and versions used in the query, backed by
    #: pydantic model ``DataSourceInfos``.
    datasource_infos = SchemaField(schema=typing.Optional[DataSourceInfos])


class SeqvarResultRowPayload(pydantic.BaseModel):
    """Payload for one result row of a seqvar query."""

    # TODO: implement me / infer from protobuf schema
    foo: int


class SeqvarResultRow(models.Model):
    """One entry in the result set."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)

    #: The owning result set.
    resultset = models.ForeignKey(SeqvarResultSet, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    stop = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: The payload of the result row, backed by pydantic model
    #: ``SeqvarResultRowPayload``.
    payload = SchemaField(schema=typing.Optional[SeqvarResultRowPayload])

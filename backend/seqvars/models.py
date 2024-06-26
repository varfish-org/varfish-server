from enum import Enum
import typing
import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.db import models
from django_pydantic_field import SchemaField
import pydantic

from cases_analysis.models import CaseAnalysisSession
from variants.models.case import Case
from variants.models.projectroles import Project

#: User model.
User = get_user_model()


class GenotypeChoice(str, Enum):
    """Store genotype choice of a ``SampleGenotype``."""

    #: Reference (wild type, homozygous/hemizygous reference) genotype.
    REF = "ref"
    #: Heterozygous genotype.
    HET = "het"
    #: Homozygous alternative genotype (or hemizygous alt for chrX / male).
    HOM = "hom"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SampleGenotypeChoice(pydantic.BaseModel):
    """Store the genotype of a sample."""

    #: The sample identifier.
    sample: str
    #: The genotype.
    genotypes: list[GenotypeChoice]

    @pydantic.field_validator("genotypes")
    @classmethod
    def genotypes_sort_and_make_unique(cls, v: list[GenotypeChoice]) -> list[GenotypeChoice]:
        """Convert ``genotypes`` value to sorted list with unique elements."""
        return list(sorted(set(v)))


class SampleGenotypeSettingsBase(models.Model):
    """Abstract model for storing genotype-related settings."""

    #: Per-sample genotypes for the pedigree.
    sample_genotypes = SchemaField(schema=list[SampleGenotypeChoice])

    class Meta:
        abstract = True


class FrequencySettingsBase(models.Model):
    """Abstract model for storing frequency-related settings."""

    gnomad_exomes_enabled = models.BooleanField(default=False, null=False, blank=False)
    gnomad_exomes_frequency = models.FloatField(null=True, blank=True)
    gnomad_exomes_homozygous = models.BooleanField(null=True, blank=True)
    gnomad_exomes_heterozygous = models.BooleanField(null=True, blank=True)
    gnomad_exomes_hemizygous = models.BooleanField(null=True, blank=True)

    gnomad_genomes_enabled = models.BooleanField(default=False, null=False, blank=False)
    gnomad_genomes_frequency = models.FloatField(null=True, blank=True)
    gnomad_genomes_homozygous = models.BooleanField(null=True, blank=True)
    gnomad_genomes_heterozygous = models.BooleanField(null=True, blank=True)
    gnomad_genomes_hemizygous = models.BooleanField(null=True, blank=True)

    helixmtdb_enabled = models.BooleanField(default=False, null=False, blank=False)
    helixmtdb_heteroplasmic = models.IntegerField(null=True, blank=True)
    helixmtdb_homoplasmic = models.IntegerField(null=True, blank=True)
    helixmtdb_frequency = models.FloatField(null=True, blank=True)

    inhouse_enabled = models.BooleanField(default=False, null=False, blank=False)
    inhouse_carriers = models.IntegerField(null=True, blank=True)
    inhouse_homozygous = models.BooleanField(null=True, blank=True)
    inhouse_heterozygous = models.BooleanField(null=True, blank=True)
    inhouse_hemizygous = models.BooleanField(null=True, blank=True)

    class Meta:
        abstract = True


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


class LabeledSortableBase(BaseModel):
    """Base class for models with a rank, label, and description."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: Label of the presets.
    label = models.CharField(max_length=128)
    #: Description of the presets.
    description = models.TextField(null=True)

    class Meta:
        ordering = ["rank"]
        abstract = True


class SeqvarQueryPresetsSet(LabeledSortableBase):
    """Configured presets for a given project."""

    #: The owning ``Project``.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"SeqvarQueryPresetsSet '{self.sodar_uuid}'"


class SeqvarPresetsBase(LabeledSortableBase):
    """Base presets."""

    #: The owning ``SeqvarQueryPresetsSet``.
    presetsset = models.ForeignKey(SeqvarQueryPresetsSet, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SeqvarPresetsFrequency(FrequencySettingsBase, SeqvarPresetsBase):
    """Presets for frequency settings within a ``QueryPresetsSet``."""

    def __str__(self):
        return f"SeqvarPresetsFrequency '{self.sodar_uuid}'"


# class SeqvarPresetsConsequence(SeqvarPresetsBase):
#     """Presets for consequence-related settings within a ``QueryPresetsSet``."""


# class SeqvarPresetsLocus(SeqvarPresetsBase):
#     """Presets for locus-related settings within a ``QueryPresetsSet``."""


# class SeqvarPresetsPhenotypePrio(SeqvarPresetsBase):
#     """Presets for phenotype priorization--related settings within a ``QueryPresetsSet``."""


# class SeqvarPresetsVariantPrio(SeqvarPresetsBase):
#     """Presets for variant pathogenicity--related settings within a ``QueryPresetsSet``."""


# class SeqvarPresetsColumns(SeqvarPresetsBase):
#     """Presets for columns presets within a ``QueryPresetsSet``."""


# class SeqvarPresetsMisc(SeqvarPresetsBase):
#     """Presets for miscellaneous presets within a ``QueryPresetsSet``."""


class SeqvarQuerySettings(BaseModel):
    """The query settings for a case."""

    #: The owning ``Case``.
    case = models.ForeignKey(Case, on_delete=models.CASCADE)

    def __str__(self):
        return f"SeqvarQuerySettings '{self.sodar_uuid}'"


class SeqvarQuerySettingsCategoryBase(BaseModel):
    """Base class for concrete category query settings."""

    #: The owning ``SeqvarQuerySettings``.
    querysettings = models.OneToOneField(SeqvarQuerySettings, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SeqvarQuerySettingsFrequency(FrequencySettingsBase, SeqvarQuerySettingsCategoryBase):
    """Query settings in the frequency category."""

    def __str__(self):
        return f"SeqvarQuerySettingsFrequency '{self.sodar_uuid}'"


class SeqvarQuery(BaseModel):
    """Allows users to prepare seqvar queries for execution and execute them."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: The label of the query.
    label = models.CharField(max_length=128)

    #: Owning/containing session.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)
    #: Buffer with settings to be edited in the next query execution.
    settings_buffer = models.ForeignKey(SeqvarQuerySettings, on_delete=models.CASCADE)

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"SeqvarQuery '{self.sodar_uuid}'"


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

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.query.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"SeqvarQueryExecution '{self.sodar_uuid}'"


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

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.queryexecution.case
        except AttributeError:
            return None

    def get_absolute_url(self) -> str:
        return f"/seqvars/api/seqvarresultset/{self.case.sodar_uuid}/{self.sodar_uuid}/"

    def __str__(self):
        return f"SeqvarResultSet '{self.sodar_uuid}'"


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

    def __str__(self):
        return (
            f"SeqvarResultRow '{self.sodar_uuid}' '{self.release}-{self.chromosome}-"
            f"{self.start}-{self.reference}-{self.alternative}'"
        )

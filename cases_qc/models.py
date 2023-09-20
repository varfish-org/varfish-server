import uuid as uuid_object

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_pydantic_field import SchemaField
import pydantic

from cases.models import Case

#: Maximal array length for Postgres array fields
MAX_ARRAY_LENGTH = 10_000
#: Maximal length of metrics to read
MAX_METRIC_COUNT = 1000


class DragenStyleMetric(pydantic.BaseModel):
    """Pydantic model for Dragen-style quality control metric entries"""

    #: The section of the value
    section: str
    #: The "entry" in the section can be empty or the read group / sample
    entry: str | None
    #: The name of the metric
    name: str
    #: The count / ratio / time / etc. value
    value: int | float | str | None
    #: The count as percentage / seconds
    value_float: float | None = None


class DragenStyleCoverage(pydantic.BaseModel):
    """Pydantic model for Dragen-style coverage metric entries"""

    #: The contig name
    contig_name: str
    #: The contig length
    contig_len: int
    #: The mean coverage
    cov: float


class CaseQc(models.Model):
    """Quality control metrics set for one case."""

    #: Draft - is currently being built.
    STATE_DRAFT = "DRAFT"
    #: Active - is currently not active.
    STATE_ACTIVE = "ACTIVE"

    STATE_CHOICES = (
        (STATE_DRAFT, STATE_DRAFT),
        (STATE_ACTIVE, STATE_ACTIVE),
    )

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: State of the QC set
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default=STATE_DRAFT)
    #: The case this QC set belong to
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        #: Order by creation date
        ordering = ["-date_created"]


class CaseQcBaseModel(models.Model):
    """Base class for statistics associated with ``CaseQc``."""

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The QC metric set this histogram belongs to
    caseqc = models.ForeignKey(CaseQc, on_delete=models.CASCADE, null=False, blank=False)
    #: The sample this histogram belongs to
    sample = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        abstract = True


class DragenBaseHistogram(CaseQcBaseModel):
    """Base model for Dragen-style histograms


    The histogram is stored in a sparse fashion, storing values and their counts.  In the case of
    more than ``MAX_ARRAY_LENGTH`` entries, the histogram must be truncated which is done in the
    import code and which will truncate reading the lines.
    """

    #: The histogram keys
    keys = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)
    # The histogram values
    values = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)

    class Meta:
        abstract = True


class DragenBaseMetrics(CaseQcBaseModel):
    """Abstract metrics model for one sample in a case"""

    #: Metrics as JSON following the ``DragenStyleMetric`` schema
    metrics = SchemaField(schema=list[DragenStyleMetric], blank=False, null=False)

    class Meta:
        abstract = True


class DragenCnvMetrics(DragenBaseMetrics):
    """CNV metrics for one sample in a case"""


class DragenVcHethomRatioMetrics(DragenBaseMetrics):
    """Per-contig het./hom. metrics for one sample in the case"""


class DragenFragmentLengthHistogram(DragenBaseHistogram):
    """Histogram of fragment lengths for one sample in a case."""


class DragenMappingMetrics(DragenBaseMetrics):
    """Metrics for the read mapping for one sample in the case"""


class DragenPloidyEstimationMetrics(DragenBaseMetrics):
    """Ploidy estimation metrics for one sample in the case"""


class DragenRohMetrics(DragenBaseMetrics):
    """ROH metrics for one sample in the case"""


class DragenVcMetrics(DragenBaseMetrics):
    """Variant calling metrics for one sample in the case"""


class DragenSvMetrics(DragenBaseMetrics):
    """SV calling metrics for one sample in the case"""


class DragenTimeMetrics(DragenBaseMetrics):
    """Time metrics for one sample in the case"""


class DragenTrimmerMetrics(DragenBaseMetrics):
    """Trimmer metrics for one sample in the case"""


class DragenWgsCoverageMetrics(DragenBaseMetrics):
    """WGS coverage summary metrics for one sample in the case"""


class DragenWgsContigMeanCovMetrics(CaseQcBaseModel):
    """Contig-wise WGS coverage metrics for one sample in the case"""

    #: Metrics as JSON following the ``DragenStyleCoverage`` schema
    metrics = SchemaField(schema=list[DragenStyleCoverage], blank=False, null=False)


class DragenWgsOverallMeanCov(DragenBaseMetrics):
    """Overall mean WGS coverage metrics for one sample in the case"""


class DragenWgsFineHist(DragenBaseHistogram):
    """Fine histogram of WGS coverage for one sample in the case"""


class DragenWgsHistMetrics(CaseQcBaseModel):
    """WGS coarse coverage metrics for one sample in the case"""

    #: The histogram keys
    keys = ArrayField(
        models.CharField(max_length=200), null=False, blank=False, max_length=MAX_ARRAY_LENGTH
    )
    # The histogram values
    values = ArrayField(models.FloatField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)


class DragenRegionMixin(models.Model):
    """Mixin that adds ``region_name`` to Dragen models"""

    #: The name of the region.
    region_name = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        abstract = True


class DragenRegionCoverageMetrics(DragenRegionMixin, DragenBaseMetrics):
    """Region based overall coverage."""


class DragenRegionFineHist(DragenRegionMixin, DragenBaseHistogram):
    """Region coarse coverage histogram."""


class DragenRegionHist(DragenRegionMixin, DragenBaseMetrics):
    """Region coarse coverage histogram."""


class DragenRegionOverallMeanCov(DragenRegionMixin, DragenBaseMetrics):
    """Region based overall coverage."""

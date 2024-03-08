from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_pydantic_field import SchemaField
import pydantic

from cases_qc.models import MAX_ARRAY_LENGTH, CaseQcBaseModel, CaseQcForSampleBaseModel


class DragenStyleMetric(pydantic.BaseModel):
    """Pydantic model for Dragen-style quality control metric entries"""

    #: The section of the value
    section: str | None
    #: The "entry" in the section can be empty or the read group / sample
    entry: str | None
    #: The name of the metric
    name: str | None
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


class DragenBaseHistogram(CaseQcForSampleBaseModel):
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
    """Abstract metrics model not specific to one sample"""

    #: Metrics as JSON following the ``DragenStyleMetric`` schema
    metrics = SchemaField(schema=list[DragenStyleMetric], blank=False, null=False)

    class Meta:
        abstract = True


class DragenBaseMetricsForSample(CaseQcForSampleBaseModel):
    """Abstract metrics model for one sample in a case"""

    #: Metrics as JSON following the ``DragenStyleMetric`` schema
    metrics = SchemaField(schema=list[DragenStyleMetric], blank=False, null=False)

    class Meta:
        abstract = True


class DragenCnvMetrics(DragenBaseMetrics):
    """CNV metrics for one sample in a case"""


class DragenFragmentLengthHistogram(DragenBaseHistogram):
    """Histogram of fragment lengths for one sample in a case."""


class DragenMappingMetrics(DragenBaseMetricsForSample):
    """Metrics for the read mapping for one sample in the case"""


class DragenPloidyEstimationMetrics(DragenBaseMetricsForSample):
    """Ploidy estimation metrics for one sample in the case"""


class DragenRohMetrics(DragenBaseMetricsForSample):
    """ROH metrics for one sample in the case"""


class DragenVcHethomRatioMetrics(DragenBaseMetrics):
    """Per-contig het./hom. metrics for one sample in the case"""


class DragenVcMetrics(DragenBaseMetrics):
    """Variant calling metrics for one sample in the case"""


class DragenSvMetrics(DragenBaseMetrics):
    """SV calling metrics for one sample in the case"""


class DragenTimeMetrics(DragenBaseMetricsForSample):
    """Time metrics for one sample in the case"""


class DragenTrimmerMetrics(DragenBaseMetricsForSample):
    """Trimmer metrics for one sample in the case"""


class DragenWgsCoverageMetrics(DragenBaseMetricsForSample):
    """WGS coverage summary metrics for one sample in the case"""


class DragenWgsContigMeanCovMetrics(CaseQcForSampleBaseModel):
    """Contig-wise WGS coverage metrics for one sample in the case"""

    #: Metrics as JSON following the ``DragenStyleCoverage`` schema
    metrics = SchemaField(schema=list[DragenStyleCoverage], blank=False, null=False)


class DragenWgsOverallMeanCov(DragenBaseMetricsForSample):
    """Overall mean WGS coverage metrics for one sample in the case"""


class DragenWgsFineHist(DragenBaseHistogram):
    """Fine histogram of WGS coverage for one sample in the case"""


class DragenWgsHist(CaseQcForSampleBaseModel):
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


class DragenRegionCoverageMetrics(DragenRegionMixin, DragenBaseMetricsForSample):
    """Region based overall coverage."""


class DragenRegionFineHist(DragenRegionMixin, DragenBaseHistogram):
    """Region coarse coverage histogram."""


class DragenRegionHist(DragenRegionMixin, DragenBaseMetricsForSample):
    """Region coarse coverage histogram."""


class DragenRegionOverallMeanCov(DragenRegionMixin, DragenBaseMetricsForSample):
    """Region based overall coverage."""

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

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The case this QC set belong to
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False, blank=False, unique=True)


class BaseHistogram(models.Model):
    """Base model for Dragen-style histograms


    The histogram is stored in a sparse fashion, storing values and their counts.  In the case of
    more than ``MAX_ARRAY_LENGTH`` entries, the histogram must be truncated which is done in the
    import code and which will truncate reading the lines.
    """

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
    #: The histogram keys
    keys = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)
    # The histogram values
    values = ArrayField(models.IntegerField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)

    class Meta:
        abstract = True


class BaseMetrics(models.Model):
    """Abstract metrics model for one sample in a case"""

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
    #: Metrics as JSON following the ``DragenStyleMetric`` schema
    metrics = SchemaField(schema=list[DragenStyleMetric], blank=False, null=False)

    class Meta:
        abstract = True


class CnvMetrics(BaseMetrics):
    """CNV metrics for one sample in a case"""


class ContigHetHomMetrics(BaseMetrics):
    """Per-contig het./hom. metrics for one sample in the case"""


class FragmentLengthHistogram(BaseHistogram):
    """Histogram of fragment lengths for one sample in a case."""


class MappingMetrics(BaseMetrics):
    """Metrics for the read mapping for one sample in the case"""


class PloidyEstimationMetrics(BaseMetrics):
    """Ploidy estimation metrics for one sample in the case"""


class RohMetrics(BaseMetrics):
    """ROH metrics for one sample in the case"""


class SeqvarMetrics(BaseMetrics):
    """Variant calling metrics for one sample in the case"""


class StrucvarMetrics(BaseMetrics):
    """SV calling metrics for one sample in the case"""


class TimeMetrics(BaseMetrics):
    """Time metrics for one sample in the case"""


class TrimmerMetrics(BaseMetrics):
    """Trimmer metrics for one sample in the case"""


class WgsCoverageMetrics(BaseMetrics):
    """WGS coverage summary metrics for one sample in the case"""


class WgsContigMeanCovMetrics(models.Model):
    """Overall mean WGS coverage metrics for one sample in the case"""

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
    #: Metrics as JSON following the ``DragenStyleCoverage`` schema
    metrics = SchemaField(schema=list[DragenStyleCoverage], blank=False, null=False)


class WgsHistMetrics(models.Model):
    """WGS coarse coverage metrics for one sample in the case"""

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
    #: The histogram keys
    keys = ArrayField(
        models.CharField(max_length=200), null=False, blank=False, max_length=MAX_ARRAY_LENGTH
    )
    # The histogram values
    values = ArrayField(models.FloatField(), null=False, blank=False, max_length=MAX_ARRAY_LENGTH)


class WgsFineHist(BaseHistogram):
    """Fine histogram of WGS coverage for one sample in the case"""

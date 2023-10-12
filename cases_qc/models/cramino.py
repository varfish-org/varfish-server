"""Django and Pydantic models for cramino QC."""

from django_pydantic_field import SchemaField
import pydantic

from cases_qc.models import CaseQcForSampleBaseModel


class CraminoChromNormalizedCountsRecord(pydantic.BaseModel):
    """Store one chrom/normalized read counts record from Cramino output."""

    #: chromosome name
    chrom_name: str
    #: fraction of reads
    normalized_counts: float


class CraminoSummaryRecord(pydantic.BaseModel):
    """Store a summary record from the cramino output file."""

    #: key
    key: str
    #: value
    value: int | float | str

    class Config:
        smart_union = True  # prevent "int | float" from float to int conversion


class CraminoMetrics(CaseQcForSampleBaseModel):
    """Metrics obtained from cramino."""

    #: summary metric records
    summary = SchemaField(schema=list[CraminoSummaryRecord], blank=False, null=False)
    #: per-chromosome normalized read counts
    chrom_counts = SchemaField(
        schema=list[CraminoChromNormalizedCountsRecord], blank=False, null=False
    )

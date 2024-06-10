"""Django and Pydantic models for ngs-bits QC."""

from django.db import models
from django_pydantic_field import SchemaField
import pydantic

from cases_qc.models import CaseQcForSampleBaseModel


class NgsbitsMappingqcRecord(pydantic.BaseModel):
    """One entry in the output of ngs-bits' MappingQC."""

    #: key
    key: str
    #: value
    value: int | float | str | None


class NgsbitsMappingqcMetrics(CaseQcForSampleBaseModel):
    """Metrics obtained from ngs-bits' MappingQC."""

    #: the name of the region.
    region_name = models.CharField(max_length=200, null=False, blank=False)
    #: records
    records = SchemaField(schema=list[NgsbitsMappingqcRecord], blank=False, null=False)

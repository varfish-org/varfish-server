from django_pydantic_field.rest_framework import SchemaField
from projectroles.serializers import SODARModelSerializer
from rest_framework import serializers
import rest_framework.serializers

from cases_qc.models import CaseQc
from cases_qc.models.cramino import (
    CraminoChromNormalizedCountsRecord,
    CraminoMetrics,
    CraminoSummaryRecord,
)
from cases_qc.models.dragen import (
    DragenCnvMetrics,
    DragenFragmentLengthHistogram,
    DragenMappingMetrics,
    DragenPloidyEstimationMetrics,
    DragenRegionCoverageMetrics,
    DragenRegionFineHist,
    DragenRegionHist,
    DragenRegionOverallMeanCov,
    DragenRohMetrics,
    DragenStyleCoverage,
    DragenStyleMetric,
    DragenSvMetrics,
    DragenTimeMetrics,
    DragenTrimmerMetrics,
    DragenVcHethomRatioMetrics,
    DragenVcMetrics,
    DragenWgsContigMeanCovMetrics,
    DragenWgsCoverageMetrics,
    DragenWgsFineHist,
    DragenWgsHist,
    DragenWgsOverallMeanCov,
)
from cases_qc.models.ngsbits import NgsbitsMappingqcMetrics, NgsbitsMappingqcRecord
from cases_qc.models.samtools import (
    BcftoolsStatsAfRecord,
    BcftoolsStatsDpRecord,
    BcfToolsStatsIddRecord,
    BcftoolsStatsMetrics,
    BcftoolsStatsQualRecord,
    BcftoolsStatsSisRecord,
    BcftoolsStatsSnRecord,
    BcftoolsStatsStRecord,
    BcftoolsStatsTstvRecord,
    SamtoolsFlagstatMetrics,
    SamtoolsFlagstatRecord,
    SamtoolsIdxstatsMetrics,
    SamtoolsIdxstatsRecord,
    SamtoolsStatsBasePercentagesRecord,
    SamtoolsStatsChkRecord,
    SamtoolsStatsFqRecord,
    SamtoolsStatsGcdRecord,
    SamtoolsStatsGcRecord,
    SamtoolsStatsHistoRecord,
    SamtoolsStatsIcRecord,
    SamtoolsStatsIdRecord,
    SamtoolsStatsIsRecord,
    SamtoolsStatsMainMetrics,
    SamtoolsStatsSnRecord,
    SamtoolsStatsSupplementaryMetrics,
)
from cases_qc.models.varfish import (
    RegionVariantStats,
    SampleAlignmentStats,
    SampleReadStats,
    SampleSeqvarStats,
    SampleStrucvarStats,
)


class QcSerializerBase(SODARModelSerializer):
    caseqc = serializers.ReadOnlyField(source="caseqc.sodar_uuid")

    class Meta:
        abstract = True
        exclude = ("id",)


class DragenBaseMetricsSerializer(QcSerializerBase):
    metrics = SchemaField(schema=list[DragenStyleMetric])

    class Meta:
        abstract = True
        exclude = ("id",)


class DragenCnvMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenCnvMetrics
        exclude = ("id",)


class DragenFragmentLengthHistogramSerializer(QcSerializerBase):
    class Meta:
        model = DragenFragmentLengthHistogram
        exclude = ("id",)


class DragenMappingMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenMappingMetrics
        exclude = ("id",)


class DragenPloidyEstimationMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenPloidyEstimationMetrics
        exclude = ("id",)


class DragenRohMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenRohMetrics
        exclude = ("id",)


class DragenVcHethomRatioMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenVcHethomRatioMetrics
        exclude = ("id",)


class DragenVcMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenVcMetrics
        exclude = ("id",)


class DragenSvMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenSvMetrics
        exclude = ("id",)


class DragenTimeMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenTimeMetrics
        exclude = ("id",)


class DragenTrimmerMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenTrimmerMetrics
        exclude = ("id",)


class DragenWgsCoverageMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenWgsCoverageMetrics
        exclude = ("id",)


class DragenWgsContigMeanCovMetricsSerializer(QcSerializerBase):
    metrics = SchemaField(schema=list[DragenStyleCoverage])

    class Meta:
        model = DragenWgsContigMeanCovMetrics
        exclude = ("id",)


class DragenWgsOverallMeanCovSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenWgsOverallMeanCov
        exclude = ("id",)


class DragenWgsFineHistSerializer(QcSerializerBase):
    class Meta:
        model = DragenWgsFineHist
        exclude = ("id",)


class DragenWgsHistSerializer(QcSerializerBase):
    class Meta:
        model = DragenWgsHist
        exclude = ("id",)


class DragenRegionCoverageMetricsSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenRegionCoverageMetrics
        exclude = ("id",)


class DragenRegionFineHistSerializer(QcSerializerBase):
    class Meta:
        model = DragenRegionFineHist
        exclude = ("id",)


class DragenRegionHistSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenRegionHist
        exclude = ("id",)


class DragenRegionOverallMeanCovSerializer(DragenBaseMetricsSerializer):
    class Meta:
        model = DragenRegionOverallMeanCov
        exclude = ("id",)


class BcftoolsStatsMetricsSerializer(QcSerializerBase):
    sn = SchemaField(schema=list[BcftoolsStatsSnRecord])
    tstv = SchemaField(schema=list[BcftoolsStatsTstvRecord])
    sis = SchemaField(schema=list[BcftoolsStatsSisRecord])
    af = SchemaField(schema=list[BcftoolsStatsAfRecord])
    qual = SchemaField(schema=list[BcftoolsStatsQualRecord])
    idd = SchemaField(schema=list[BcfToolsStatsIddRecord])
    st = SchemaField(schema=list[BcftoolsStatsStRecord])
    dp = SchemaField(schema=list[BcftoolsStatsDpRecord])

    class Meta:
        model = BcftoolsStatsMetrics
        exclude = ("id",)


class SamtoolsStatsMainMetricsSerializer(QcSerializerBase):
    sn = SchemaField(schema=list[SamtoolsStatsSnRecord])
    chk = SchemaField(schema=list[SamtoolsStatsChkRecord])
    isize = SchemaField(schema=list[SamtoolsStatsIsRecord])
    cov = SchemaField(schema=list[SamtoolsStatsHistoRecord])
    gcd = SchemaField(schema=list[SamtoolsStatsGcdRecord])
    frl = SchemaField(schema=list[SamtoolsStatsHistoRecord])
    lrl = SchemaField(schema=list[SamtoolsStatsHistoRecord])
    idd = SchemaField(schema=list[SamtoolsStatsIdRecord])
    ffq = SchemaField(schema=list[SamtoolsStatsFqRecord])
    lfq = SchemaField(schema=list[SamtoolsStatsFqRecord])
    fbc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord])
    lbc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord])

    class Meta:
        model = SamtoolsStatsMainMetrics
        exclude = ("id",)


class SamtoolsStatsSupplementaryMetricsSerializer(QcSerializerBase):
    gcf = SchemaField(schema=list[SamtoolsStatsGcRecord])
    gcl = SchemaField(schema=list[SamtoolsStatsGcRecord])
    gcc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord])
    gct = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord])
    rl = SchemaField(schema=list[SamtoolsStatsHistoRecord])
    mapq = SchemaField(schema=list[SamtoolsStatsHistoRecord])
    ic = SchemaField(schema=list[SamtoolsStatsIcRecord])

    class Meta:
        model = SamtoolsStatsSupplementaryMetrics
        exclude = ("id",)


class SamtoolsFlagstatMetricsSerializer(QcSerializerBase):
    qc_pass = SchemaField(schema=SamtoolsFlagstatRecord)
    qc_fail = SchemaField(schema=SamtoolsFlagstatRecord)

    class Meta:
        model = SamtoolsFlagstatMetrics
        exclude = ("id",)


class SamtoolsIdxstatsMetricsSerializer(QcSerializerBase):
    records = SchemaField(schema=list[SamtoolsIdxstatsRecord])

    class Meta:
        model = SamtoolsIdxstatsMetrics
        exclude = ("id",)


class CraminoMetricsSerializer(QcSerializerBase):
    summary = SchemaField(schema=list[CraminoSummaryRecord])
    chrom_counts = SchemaField(schema=list[CraminoChromNormalizedCountsRecord])

    class Meta:
        model = CraminoMetrics
        exclude = ("id",)


class NgsbitsMappingqcMetricsSerializer(QcSerializerBase):
    records = SchemaField(schema=list[NgsbitsMappingqcRecord])

    class Meta:
        model = NgsbitsMappingqcMetrics
        exclude = ("id",)


class CaseQcSerializer(SODARModelSerializer):
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    dragen_cnvmetrics = DragenCnvMetricsSerializer(
        many=True, read_only=True, source="dragencnvmetrics_set"
    )
    dragen_fragmentlengthhistograms = DragenFragmentLengthHistogramSerializer(
        many=True, read_only=True, source="dragenfragmentlengthhistogram_set"
    )
    dragen_mappingmetrics = DragenMappingMetricsSerializer(
        many=True, read_only=True, source="dragenmappingmetrics_set"
    )
    dragen_ploidyestimationmetrics = DragenPloidyEstimationMetricsSerializer(
        many=True, read_only=True, source="dragenploidyestimationmetrics_set"
    )
    dragen_rohmetrics = DragenRohMetricsSerializer(
        many=True, read_only=True, source="dragenrohmetrics_set"
    )
    dragen_vchethomratiometrics = DragenVcHethomRatioMetricsSerializer(
        many=True, read_only=True, source="dragenvchethomratiometrics_set"
    )
    dragen_vcmetrics = DragenVcMetricsSerializer(
        many=True, read_only=True, source="dragenvcmetrics_set"
    )
    dragen_svmetrics = DragenSvMetricsSerializer(
        many=True, read_only=True, source="dragensvmetrics_set"
    )
    dragen_timemetrics = DragenTimeMetricsSerializer(
        many=True, read_only=True, source="dragentimemetrics_set"
    )
    dragen_trimmermetrics = DragenTrimmerMetricsSerializer(
        many=True, read_only=True, source="dragentrimmermetrics_set"
    )
    dragen_wgscoveragemetrics = DragenWgsCoverageMetricsSerializer(
        many=True, read_only=True, source="dragenwgscoveragemetrics_set"
    )
    dragen_wgscontigmeancovmetrics = DragenWgsContigMeanCovMetricsSerializer(
        many=True, read_only=True, source="dragenwgscontigmeancovmetrics_set"
    )
    dragen_wgsoverallmeancov = DragenWgsOverallMeanCovSerializer(
        many=True, read_only=True, source="dragenwgsoverallmeancov_set"
    )
    dragen_wgsfinehist = DragenWgsFineHistSerializer(
        many=True, read_only=True, source="dragenwgsfinehist_set"
    )
    dragen_wgshist = DragenWgsHistSerializer(many=True, read_only=True, source="dragenwgshist_set")
    dragen_regioncoveragemetrics = DragenRegionCoverageMetricsSerializer(
        many=True, read_only=True, source="dragenregioncoveragemetrics_set"
    )
    dragen_regionfinehist = DragenRegionFineHistSerializer(
        many=True, read_only=True, source="dragenregionfinehist_set"
    )
    dragen_regionhist = DragenRegionHistSerializer(
        many=True, read_only=True, source="dragenregionhist_set"
    )
    dragen_regionoverallmeancov = DragenRegionOverallMeanCovSerializer(
        many=True, read_only=True, source="dragenregionoverallmeancov_set"
    )
    bcftools_statsmetrics = BcftoolsStatsMetricsSerializer(
        many=True, read_only=True, source="bcftoolsstatsmetrics_set"
    )
    samtools_statsmainmetrics = SamtoolsStatsMainMetricsSerializer(
        many=True, read_only=True, source="samtoolsstatsmainmetrics_set"
    )
    samtools_statssupplementarymetrics = SamtoolsStatsSupplementaryMetricsSerializer(
        many=True, read_only=True, source="samtoolsstatssupplementarymetrics_set"
    )
    samtools_flagstatmetrics = SamtoolsFlagstatMetricsSerializer(
        many=True, read_only=True, source="samtoolsflagstatmetrics_set"
    )
    samtools_idxstatsmetrics = SamtoolsIdxstatsMetricsSerializer(
        many=True, read_only=True, source="samtoolsidxstatsmetrics_set"
    )
    cramino_metrics = CraminoMetricsSerializer(
        many=True, read_only=True, source="craminometrics_set"
    )
    ngsbits_mappingqcmetrics = NgsbitsMappingqcMetricsSerializer(
        many=True, read_only=True, source="ngsbitsmappingqcmetrics_set"
    )

    class Meta:
        model = CaseQc
        exclude = ("id",)


class VarFishStatsSerializer(rest_framework.serializers.Serializer):
    """Serializer for common-denominator stats objects"""

    readstats = SchemaField(schema=list[SampleReadStats])
    alignmentstats = SchemaField(schema=list[SampleAlignmentStats])
    seqvarsstats = SchemaField(schema=list[SampleSeqvarStats])
    strucvarstats = SchemaField(schema=list[SampleStrucvarStats])

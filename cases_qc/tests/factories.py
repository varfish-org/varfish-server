import datetime

import factory

from cases.tests.factories import CaseFactory
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
    BcftoolsStatsSnRecord,
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
    SamtoolsStatsSupplementaryMetrics,
)
from cases_qc.models.varfish import (
    DetailedAlignmentCounts,
    InsertSizeStats,
    RegionCoverageStats,
    RegionVariantStats,
    SampleAlignmentStats,
    SampleReadStats,
    SampleSeqvarStats,
    SampleStrucvarStats,
    VarfishStats,
)


class DragenStyleMetricFactory(factory.Factory):
    class Meta:
        model = DragenStyleMetric

    section = factory.Faker("word")
    entry = factory.Faker("word")
    value = factory.Faker("word")
    name = factory.Faker("word")
    value = 42
    value_float = 3.14


class DragenStyleCoverageFactory(factory.Factory):
    class Meta:
        model = DragenStyleCoverage

    contig_name = factory.Faker("word")
    contig_len = 12345
    cov = 3.0


class CaseQcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseQc

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case = factory.SubFactory(CaseFactory)
    state = CaseQc.STATE_ACTIVE


class DragenMetricsFactoryBase(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def metrics(self):
        return [DragenStyleMetricFactory()]


class DragenMetricsWithSampleFactoryBase(DragenMetricsFactoryBase):
    class Meta:
        abstract = True

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]


class DragenFineHistFactoryBase(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    keys = [37, 40, 41]
    values = [1, 100, 101]


class RegionMetricsFactoryBase(DragenMetricsWithSampleFactoryBase):
    class Meta:
        abstract = True

    region_name = factory.Faker("word")


class DragenFragmentLengthHistogramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DragenFragmentLengthHistogram

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    keys = [37, 40, 41]
    values = [1, 100, 101]


class DragenCnvMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenCnvMetrics


class DragenMappingMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenMappingMetrics


class DragenPloidyEstimationMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenPloidyEstimationMetrics


class DragenRegionCoverageMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenRegionCoverageMetrics


class DragenRegionFineHistFactory(DragenFineHistFactoryBase):
    class Meta:
        model = DragenRegionFineHist

    region_name = factory.Faker("word")


class DragenRegionHistFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenRegionHist


class DragenRegionOverallMeanCovFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenRegionOverallMeanCov


class DragenRohMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenRohMetrics


class DragenVcMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenVcMetrics


class DragenSvMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenSvMetrics


class DragenTimeMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenTimeMetrics


class DragenTrimmerMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenTrimmerMetrics


class DragenVcHethomRatioMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenVcHethomRatioMetrics


class DragenWgsContigMeanCovMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenWgsContigMeanCovMetrics

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    @factory.lazy_attribute
    def metrics(self):
        return [DragenStyleCoverageFactory(sample=self.sample)]


class DragenWgsCoverageMetricsFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenWgsCoverageMetrics


class DragenWgsFineHistFactory(DragenFineHistFactoryBase):
    class Meta:
        model = DragenWgsFineHist


class DragenWgsHistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DragenWgsHist

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    keys = [
        "PCT of bases in wgs with coverage [100x:inf)",
        "PCT of bases in wgs with coverage [50x:100x)",
    ]
    values = [0.21, 26.83]


class DragenWgsOverallMeanCovFactory(DragenMetricsWithSampleFactoryBase):
    class Meta:
        model = DragenWgsOverallMeanCov


class SamtoolsStatsChkRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsChkRecord

    read_names_crc32 = factory.Faker("word")
    sequences_crc32 = factory.Faker("word")
    qualities_crc32 = factory.Faker("word")


class SamtoolsStatsSnRecordFactory(factory.Factory):
    class Meta:
        model = BcftoolsStatsSnRecord

    key = factory.Faker("word")
    value = factory.Sequence(lambda n: n)


class SamtoolsStatsFqRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsFqRecord

    cycle = factory.Sequence(lambda n: n)
    counts = factory.Sequence(lambda n: [n])


class SamtoolsStatsGcRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsGcRecord

    gc_content = factory.Sequence(lambda n: 0.1 * n)
    count = factory.Sequence(lambda n: n)


class SamtoolsStatsBasePercentagesRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsBasePercentagesRecord

    cycle = factory.Sequence(lambda n: n)
    percentages = factory.Sequence(lambda n: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])


class SamtoolsStatsIsRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsIsRecord

    insert_size = factory.Sequence(lambda n: n)
    pairs_total = factory.Sequence(lambda n: n)
    pairs_inward = factory.Sequence(lambda n: n)
    pairs_outward = factory.Sequence(lambda n: n)
    pairs_other = factory.Sequence(lambda n: n)


class SamtoolsStatsHistoRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsHistoRecord

    value = factory.Sequence(lambda n: n)
    count = factory.Sequence(lambda n: n)


class SamtoolsStatsIdRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsIdRecord

    length = factory.Sequence(lambda n: n)
    ins = factory.Sequence(lambda n: n)
    dels = factory.Sequence(lambda n: n)


class SamtoolsStatsIcRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsIcRecord

    cycle = factory.Sequence(lambda n: n)
    ins_fwd = factory.Sequence(lambda n: n)
    dels_fwd = factory.Sequence(lambda n: n)
    ins_rev = factory.Sequence(lambda n: n)
    dels_rev = factory.Sequence(lambda n: n)


class SamtoolsStatsGcdRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsStatsGcdRecord

    gc_content = factory.Sequence(lambda n: 0.1 * n)
    unique_seq_percentiles = factory.Sequence(lambda n: 0.1 * n)
    dp_percentile_10 = factory.Sequence(lambda n: 0.1 * n)
    dp_percentile_25 = factory.Sequence(lambda n: 0.1 * n)
    dp_percentile_50 = factory.Sequence(lambda n: 0.1 * n)
    dp_percentile_75 = factory.Sequence(lambda n: 0.1 * n)
    dp_percentile_90 = factory.Sequence(lambda n: 0.1 * n)


class SamtoolsStatsMainMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SamtoolsStatsMainMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    sn = factory.LazyAttribute(lambda _o: [SamtoolsStatsSnRecordFactory()])
    chk = factory.LazyAttribute(lambda _o: [SamtoolsStatsChkRecordFactory()])
    isize = factory.LazyAttribute(lambda _o: [SamtoolsStatsIsRecordFactory()])
    cov = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecordFactory()])
    gcd = factory.LazyAttribute(lambda _o: [SamtoolsStatsGcdRecordFactory()])
    frl = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecordFactory()])
    lrl = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecordFactory()])
    idd = factory.LazyAttribute(lambda _o: [SamtoolsStatsIdRecordFactory()])
    ffq = factory.LazyAttribute(lambda _o: [SamtoolsStatsFqRecordFactory()])
    lfq = factory.LazyAttribute(lambda _o: [SamtoolsStatsFqRecordFactory()])
    fbc = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecordFactory()])
    lbc = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecordFactory()])


class SamtoolsStatsSupplementaryMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SamtoolsStatsSupplementaryMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    gcf = factory.LazyAttribute(lambda _o: [SamtoolsStatsGcRecordFactory()])
    gcl = factory.LazyAttribute(lambda _o: [SamtoolsStatsGcRecordFactory()])
    gcc = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecordFactory()])
    gct = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecordFactory()])
    rl = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecordFactory()])
    mapq = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecordFactory()])
    ic = factory.LazyAttribute(lambda _o: [SamtoolsStatsIcRecordFactory()])


class SamtoolsFlagstatRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsFlagstatRecord

    total = factory.Sequence(lambda n: n)
    primary = factory.Sequence(lambda n: n)
    secondary = factory.Sequence(lambda n: n)
    supplementary = factory.Sequence(lambda n: n)
    duplicates = factory.Sequence(lambda n: n)
    duplicates_primary = factory.Sequence(lambda n: n)
    mapped = factory.Sequence(lambda n: n)
    mapped_primary = factory.Sequence(lambda n: n)
    paired = factory.Sequence(lambda n: n)
    fragment_first = factory.Sequence(lambda n: n)
    fragment_last = factory.Sequence(lambda n: n)
    properly_paired = factory.Sequence(lambda n: n)
    with_itself_and_mate_mapped = factory.Sequence(lambda n: n)
    singletons = factory.Sequence(lambda n: n)
    with_mate_mapped_to_different_chr = factory.Sequence(lambda n: n)
    with_mate_mapped_to_different_chr_mapq5 = factory.Sequence(lambda n: n)


class SamtoolsFlagstatMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SamtoolsFlagstatMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    qc_pass = factory.SubFactory(SamtoolsFlagstatRecordFactory)
    qc_fail = factory.SubFactory(SamtoolsFlagstatRecordFactory)


class SamtoolsIdxstatsRecordFactory(factory.Factory):
    class Meta:
        model = SamtoolsIdxstatsRecord

    contig_name = factory.Faker("word")
    contig_len = factory.Sequence(lambda n: n)
    mapped = factory.Sequence(lambda n: n)
    unmapped = factory.Sequence(lambda n: n)


class SamtoolsIdxstatsMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SamtoolsIdxstatsMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    records = factory.LazyAttribute(lambda _o: [SamtoolsIdxstatsRecordFactory()])


class CraminoSummaryRecordFactory(factory.Factory):
    class Meta:
        model = CraminoSummaryRecord

    key = factory.Faker("word")
    value = factory.Sequence(lambda n: n)


class CraminoChromNormalizedCountsRecordFactory(factory.Factory):
    class Meta:
        model = CraminoChromNormalizedCountsRecord

    chrom_name = factory.Faker("word")
    normalized_counts = factory.Sequence(lambda n: 0.1 * n)


class CraminoMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CraminoMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)
    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    summary = factory.LazyAttribute(lambda _o: [CraminoSummaryRecordFactory()])
    chrom_counts = factory.LazyAttribute(lambda _o: [CraminoChromNormalizedCountsRecordFactory()])


class NgsbitsMappingqcRecordFactory(factory.Factory):
    class Meta:
        model = NgsbitsMappingqcRecord

    key = factory.Faker("word")
    value = factory.Sequence(lambda n: 0.1 * n)


class NgsbitsMappingqcMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NgsbitsMappingqcMetrics

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)
    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    region_name = "WGS"
    records = factory.LazyAttribute(lambda _o: [NgsbitsMappingqcRecordFactory()])


class SampleReadStatsFactory(factory.Factory):
    class Meta:
        model = SampleReadStats

    sample = factory.Faker("word")
    read_length_n50 = 42
    read_length_histogram = [[1, 2], [10, 4]]
    total_reads = 42
    total_yield = 42_000
    fragment_first = 21
    fragment_last = 21


class RegionCoverageStatsFactory(factory.Factory):
    class Meta:
        model = RegionCoverageStats

    region_name = factory.Faker("word")
    mean_rd = 42.0
    min_rd_fraction = [[1, 0.01], [10, 0.1]]


class InsertSizeStatsFactory(factory.Factory):
    class Meta:
        model = InsertSizeStats

    insert_size_mean = 42.0
    insert_size_median = 42.0
    insert_size_stddev = 42.0
    insert_size_histogram = [[1, 2], [10, 4]]


class DetailedAlignmentCountsFactory(factory.Factory):
    class Meta:
        model = DetailedAlignmentCounts

    primary = 42
    secondary = 0
    supplementary = 10
    duplicates = 2
    mapped = 32
    properly_paired = 16
    with_itself_and_mate_mapped = 5
    singletons = 1
    with_mate_mapped_to_different_chr = 0
    with_mate_mapped_to_different_chr_mapq = 0
    mismatch_rate = 0.01
    mapq = [[-1, 10], [0, 10], [10, 20]]


class SampleAlignmentStatsFactory(factory.Factory):
    class Meta:
        model = SampleAlignmentStats

    sample = factory.Faker("word")
    detailed_counts = factory.SubFactory(DetailedAlignmentCountsFactory)
    per_chromosome_counts = [["chr1", 10], ["chr2", 20]]
    insert_size_stats = factory.SubFactory(InsertSizeStatsFactory)
    region_coverage_stats = factory.lazy_attribute(lambda _o: [RegionCoverageStatsFactory()])


class RegionVariantStatsFactory(factory.Factory):
    class Meta:
        model = RegionVariantStats

    region_name = factory.Faker("word")
    snv_count = 42
    indel_count = 42
    multiallelic_count = 0
    transition_count = 10
    transversion_count = 20
    tstv_ratio = 0.5


class SampleSeqvarStatsFactory(factory.Factory):
    class Meta:
        model = SampleSeqvarStats

    sample = factory.Faker("word")
    genome_wide = factory.SubFactory(RegionVariantStatsFactory)
    per_region = []


class SampleStrucvarStatsFactory(factory.Factory):
    class Meta:
        model = SampleStrucvarStats

    sample = factory.Faker("word")
    deletion_count = 10
    duplication_count = 20
    insertion_count = 0
    inversion_count = 30
    breakend_count = 5


class VarfishStatsFactory(factory.Factory):
    class Meta:
        model = VarfishStats

    samples = factory.lazy_attribute(lambda _o: ["sample"])
    readstats = factory.lazy_attribute(lambda _o: [SampleReadStatsFactory()])
    alignmentstats = factory.lazy_attribute(lambda _o: [SampleAlignmentStatsFactory()])
    seqvarstats = factory.lazy_attribute(lambda _o: [SampleSeqvarStatsFactory()])
    strucvarstats = factory.lazy_attribute(lambda _o: [SampleStrucvarStatsFactory()])

import datetime

import factory
import factory.fuzzy

from cases.tests.factories import CaseFactory
from cases_qc.models import (
    BcftoolsStatsSnRecord,
    CaseQc,
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


class DragenStyleMetricFactory(factory.Factory):
    class Meta:
        model = DragenStyleMetric

    section = factory.Faker("word")
    entry = factory.Faker("word")
    value = factory.Faker("word")
    name = factory.Faker("word")
    value = factory.fuzzy.FuzzyChoice([None, 42, 3.14, "foo"])
    value_float = factory.fuzzy.FuzzyChoice([None, 42, 3.14])


class DragenStyleCoverageFactory(factory.Factory):
    class Meta:
        model = DragenStyleCoverage

    contig_name = factory.fuzzy.FuzzyText(length=2, prefix="chr")
    contig_len = factory.fuzzy.FuzzyInteger(1, 1000000)
    cov = factory.fuzzy.FuzzyFloat(0.0, 60.0)


class CaseQcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseQc

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case = factory.SubFactory(CaseFactory)


class DragenMetricsFactoryBase(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    @factory.lazy_attribute
    def metrics(self):
        return [DragenStyleMetricFactory(sample=self.sample)]


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


class RegionMetricsFactoryBase(DragenMetricsFactoryBase):
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


class DragenMappingMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenMappingMetrics


class DragenPloidyEstimationMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenPloidyEstimationMetrics


class DragenRegionCoverageMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenRegionCoverageMetrics


class DragenRegionFineHistFactory(DragenFineHistFactoryBase):
    class Meta:
        model = DragenRegionFineHist

    region_name = factory.Faker("word")


class DragenRegionHistFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenRegionHist


class DragenRegionOverallMeanCovFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenRegionOverallMeanCov


class DragenRohMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenRohMetrics


class DragenVcMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenVcMetrics


class StrucvarMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenSvMetrics


class DragenTimeMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenTimeMetrics


class DragenTrimmerMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenTrimmerMetrics


class DragenVcHethomRatioMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenVcHethomRatioMetrics


class DragenWgsContigMeanCovMetricsFactory(DragenMetricsFactoryBase):
    class Meta:
        model = DragenWgsContigMeanCovMetrics

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    @factory.lazy_attribute
    def metrics(self):
        return [DragenStyleCoverageFactory(sample=self.sample)]


class DragenWgsCoverageMetricsFactory(DragenMetricsFactoryBase):
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


class DragenWgsOverallMeanCovFactory(DragenMetricsFactoryBase):
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

    sn = factory.LazyAttribute(lambda _o: SamtoolsStatsSnRecordFactory())
    chk = factory.LazyAttribute(lambda _o: SamtoolsStatsChkRecordFactory())
    isize = factory.LazyAttribute(lambda _o: SamtoolsStatsIsRecordFactory())
    cov = factory.LazyAttribute(lambda _o: SamtoolsStatsHistoRecordFactory())
    gcd = factory.LazyAttribute(lambda _o: SamtoolsStatsGcdRecordFactory())
    frl = factory.LazyAttribute(lambda _o: SamtoolsStatsHistoRecordFactory())
    lrl = factory.LazyAttribute(lambda _o: SamtoolsStatsHistoRecordFactory())
    idd = factory.LazyAttribute(lambda _o: SamtoolsStatsIdRecordFactory())
    ffq = factory.LazyAttribute(lambda _o: SamtoolsStatsFqRecordFactory())
    lfq = factory.LazyAttribute(lambda _o: SamtoolsStatsFqRecordFactory())
    fbc = factory.LazyAttribute(lambda _o: SamtoolsStatsBasePercentagesRecordFactory())
    lbc = factory.LazyAttribute(lambda _o: SamtoolsStatsBasePercentagesRecordFactory())


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

    gcf = factory.LazyAttribute(lambda _o: [SamtoolsStatsGcRecord()])
    gcl = factory.LazyAttribute(lambda _o: [SamtoolsStatsGcRecord()])
    gcc = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecord()])
    gct = factory.LazyAttribute(lambda _o: [SamtoolsStatsBasePercentagesRecord()])
    rl = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecord()])
    mapq = factory.LazyAttribute(lambda _o: [SamtoolsStatsHistoRecord()])
    ic = factory.LazyAttribute(lambda _o: [SamtoolsStatsIdRecord()])


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

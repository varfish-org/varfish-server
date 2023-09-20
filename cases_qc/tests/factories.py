import datetime

import factory
import factory.fuzzy

from cases.tests.factories import CaseFactory
from cases_qc.models import (
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


class DragenCaseQcFactory(factory.django.DjangoModelFactory):
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

    caseqc = factory.SubFactory(DragenCaseQcFactory)

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

    caseqc = factory.SubFactory(DragenCaseQcFactory)

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

    caseqc = factory.SubFactory(DragenCaseQcFactory)

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

    caseqc = factory.SubFactory(DragenCaseQcFactory)

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

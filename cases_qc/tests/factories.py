import datetime

import factory
import factory.fuzzy
import yaml

from cases.tests.factories import CaseFactory
from cases_qc.models import (
    CaseQc,
    DragenCnvMetrics,
    DragenFragmentLengthHistogram,
    DragenMappingMetrics,
    DragenPloidyEstimationMetrics,
    DragenRohMetrics,
    DragenStyleCoverage,
    DragenStyleMetric,
    DragenSvMetrics,
    DragenTimeMetrics,
    DragenTrimmerMetrics,
    DragenWgsContigMeanCovMetrics,
    DragenWgsCoverageMetrics,
    DragenWgsFineHist,
    DragenWgsHistMetrics,
    SeqvarMetrics,
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


class FragmentLengthHistogramFactory(factory.django.DjangoModelFactory):
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


class MetricsFactoryBase(factory.django.DjangoModelFactory):
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


class CnvMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenCnvMetrics


class MappingMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenMappingMetrics


class PloidyEstimationMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenPloidyEstimationMetrics


class RohMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenRohMetrics


class SeqvarMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = SeqvarMetrics


class StrucvarMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenSvMetrics


class TimeMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenTimeMetrics


class TrimmerMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenTrimmerMetrics


class WgsCoverageMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenWgsCoverageMetrics


class WgsContigMeanCovMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenWgsContigMeanCovMetrics

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    @factory.lazy_attribute
    def metrics(self):
        return [DragenStyleCoverageFactory(sample=self.sample)]


class WgsHistMetricsFactory(MetricsFactoryBase):
    class Meta:
        model = DragenWgsHistMetrics


class WgsFineHistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DragenWgsFineHist

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    caseqc = factory.SubFactory(CaseQcFactory)

    @factory.lazy_attribute
    def sample(self):
        return self.caseqc.case.pedigree[0]["patient"]

    keys = [37, 40, 41]
    values = [1, 100, 101]

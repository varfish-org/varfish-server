from freezegun import freeze_time
from test_plus import TestCase

from cases_qc.models import (
    Case,
    CaseQc,
    DragenCnvMetrics,
    DragenFragmentLengthHistogram,
    DragenMappingMetrics,
    DragenPloidyEstimationMetrics,
    DragenRohMetrics,
    DragenSvMetrics,
    DragenTimeMetrics,
    DragenTrimmerMetrics,
    DragenWgsContigMeanCovMetrics,
    DragenWgsFineHist,
    SeqvarMetrics,
)
from cases_qc.tests.factories import (
    CaseQcFactory,
    CnvMetricsFactory,
    DragenStyleCoverageFactory,
    DragenStyleMetricFactory,
    FragmentLengthHistogramFactory,
    MappingMetricsFactory,
    PloidyEstimationMetricsFactory,
    RohMetricsFactory,
    SeqvarMetricsFactory,
    StrucvarMetricsFactory,
    TimeMetricsFactory,
    TrimmerMetricsFactory,
    WgsContigMeanCovMetricsFactory,
    WgsFineHistFactory,
)


class PydanticTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_metric(self):
        _metric = DragenStyleMetricFactory()

    def test_coverage(self):
        _coverage = DragenStyleCoverageFactory()


@freeze_time("2012-01-14 12:00:01")
class CaseQcTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        _obj = CaseQcFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class FragmentLengthHistogramTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 0)
        _obj = FragmentLengthHistogramFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class CnvMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenCnvMetrics.objects.count(), 0)
        _obj = CnvMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenCnvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class MappingMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenMappingMetrics.objects.count(), 0)
        _obj = MappingMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenMappingMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class PloidyEstimationMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 0)
        _obj = PloidyEstimationMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class RohMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRohMetrics.objects.count(), 0)
        _obj = RohMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRohMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class StrucvarMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenSvMetrics.objects.count(), 0)
        _obj = StrucvarMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenSvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class TrimmerMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 0)
        _obj = TrimmerMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class SeqvarMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(SeqvarMetrics.objects.count(), 0)
        _obj = SeqvarMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SeqvarMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class TimeMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTimeMetrics.objects.count(), 0)
        _obj = TimeMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTimeMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class WgsContigMeanCovMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 0)
        _obj = WgsContigMeanCovMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class WgsFineHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsFineHist.objects.count(), 0)
        _obj = WgsFineHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsFineHist.objects.count(), 1)

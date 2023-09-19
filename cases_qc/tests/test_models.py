from freezegun import freeze_time
from test_plus import TestCase

from cases_qc.models import (
    Case,
    CaseQc,
    CnvMetrics,
    FragmentLengthHistogram,
    MappingMetrics,
    PloidyEstimationMetrics,
    RohMetrics,
    SeqvarMetrics,
    StrucvarMetrics,
    TimeMetrics,
    TrimmerMetrics,
    WgsContigMeanCovMetrics,
    WgsFineHist,
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
        self.assertEqual(FragmentLengthHistogram.objects.count(), 0)
        _obj = FragmentLengthHistogramFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(FragmentLengthHistogram.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class CnvMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(CnvMetrics.objects.count(), 0)
        _obj = CnvMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CnvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class MappingMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(MappingMetrics.objects.count(), 0)
        _obj = MappingMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(MappingMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class PloidyEstimationMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(PloidyEstimationMetrics.objects.count(), 0)
        _obj = PloidyEstimationMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(PloidyEstimationMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class RohMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(RohMetrics.objects.count(), 0)
        _obj = RohMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(RohMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class StrucvarMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(StrucvarMetrics.objects.count(), 0)
        _obj = StrucvarMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(StrucvarMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class TrimmerMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(TrimmerMetrics.objects.count(), 0)
        _obj = TrimmerMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(TrimmerMetrics.objects.count(), 1)


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
        self.assertEqual(TimeMetrics.objects.count(), 0)
        _obj = TimeMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(TimeMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class WgsContigMeanCovMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(WgsContigMeanCovMetrics.objects.count(), 0)
        _obj = WgsContigMeanCovMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(WgsContigMeanCovMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class WgsFineHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(WgsFineHist.objects.count(), 0)
        _obj = WgsFineHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(WgsFineHist.objects.count(), 1)

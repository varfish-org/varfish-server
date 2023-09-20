from freezegun import freeze_time
from test_plus import TestCase

from cases_qc.models import (
    Case,
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
from cases_qc.tests.factories import (
    DragenCaseQcFactory,
    DragenCnvMetricsFactory,
    DragenFragmentLengthHistogramFactory,
    DragenMappingMetricsFactory,
    DragenPloidyEstimationMetricsFactory,
    DragenRegionCoverageMetricsFactory,
    DragenRegionFineHistFactory,
    DragenRegionHistFactory,
    DragenRegionOverallMeanCovFactory,
    DragenRohMetricsFactory,
    DragenStyleCoverageFactory,
    DragenStyleMetricFactory,
    DragenTimeMetricsFactory,
    DragenTrimmerMetricsFactory,
    DragenVcHethomRatioMetricsFactory,
    DragenVcMetricsFactory,
    DragenWgsContigMeanCovMetricsFactory,
    DragenWgsCoverageMetricsFactory,
    DragenWgsFineHistFactory,
    DragenWgsHistFactory,
    DragenWgsOverallMeanCovFactory,
    StrucvarMetricsFactory,
)


class DragenPydanticTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_metric(self):
        _metric = DragenStyleMetricFactory()

    def test_coverage(self):
        _coverage = DragenStyleCoverageFactory()


@freeze_time("2012-01-14 12:00:01")
class DragenCaseQcTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        _obj = DragenCaseQcFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenFragmentLengthHistogramTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 0)
        _obj = DragenFragmentLengthHistogramFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenCnvMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenCnvMetrics.objects.count(), 0)
        _obj = DragenCnvMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenCnvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenMappingMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenMappingMetrics.objects.count(), 0)
        _obj = DragenMappingMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenMappingMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenPloidyEstimationMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 0)
        _obj = DragenPloidyEstimationMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionCoverageMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 0)
        _obj = DragenRegionCoverageMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionFineHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionFineHist.objects.count(), 0)
        _obj = DragenRegionFineHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionFineHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionHist.objects.count(), 0)
        _obj = DragenRegionHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionOverallMeanCovTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 0)
        _obj = DragenRegionOverallMeanCovFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRohMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRohMetrics.objects.count(), 0)
        _obj = DragenRohMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRohMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenStrucvarMetricsTest(TestCase):
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
class DragenTrimmerMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 0)
        _obj = DragenTrimmerMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenVcHethomRatioMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 0)
        _obj = DragenVcHethomRatioMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenVcMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenVcMetrics.objects.count(), 0)
        _obj = DragenVcMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenVcMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenTimeMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTimeMetrics.objects.count(), 0)
        _obj = DragenTimeMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTimeMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsContigMeanCovMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 0)
        _obj = DragenWgsContigMeanCovMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsCoverageMetricsTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 0)
        _obj = DragenWgsCoverageMetricsFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsFineHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsFineHist.objects.count(), 0)
        _obj = DragenWgsFineHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsFineHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsHistTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsHist.objects.count(), 0)
        _obj = DragenWgsHistFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsOverallMeanCovTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 0)
        _obj = DragenWgsOverallMeanCovFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 1)

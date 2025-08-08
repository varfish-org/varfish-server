from freezegun import freeze_time
from test_plus import TestCase

from cases_qc.models import Case, CaseQc
from cases_qc.models.cramino import CraminoMetrics
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
from cases_qc.models.samtools import (
    SamtoolsFlagstatMetrics,
    SamtoolsIdxstatsMetrics,
    SamtoolsStatsMainMetrics,
    SamtoolsStatsSupplementaryMetrics,
)
from cases_qc.tests.factories import (
    CaseQcFactory,
    CraminoMetricsFactory,
    DetailedAlignmentCountsFactory,
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
    DragenSvMetricsFactory,
    DragenTimeMetricsFactory,
    DragenTrimmerMetricsFactory,
    DragenVcHethomRatioMetricsFactory,
    DragenVcMetricsFactory,
    DragenWgsContigMeanCovMetricsFactory,
    DragenWgsCoverageMetricsFactory,
    DragenWgsFineHistFactory,
    DragenWgsHistFactory,
    DragenWgsOverallMeanCovFactory,
    InsertSizeStatsFactory,
    RegionCoverageStatsFactory,
    RegionVariantStatsFactory,
    SampleAlignmentStatsFactory,
    SampleReadStatsFactory,
    SampleSeqvarStatsFactory,
    SampleStrucvarStatsFactory,
    SamtoolsFlagstatMetricsFactory,
    SamtoolsIdxstatsMetricsFactory,
    SamtoolsStatsMainMetricsFactory,
    SamtoolsStatsSupplementaryMetricsFactory,
    VarfishStatsFactory,
)


class DragenPydanticTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_metric(self):
        _metric = DragenStyleMetricFactory()  # noqa: F841

    def test_coverage(self):
        _coverage = DragenStyleCoverageFactory()  # noqa: F841


@freeze_time("2012-01-14 12:00:01")
class DragenCaseQcTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        _obj = CaseQcFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenFragmentLengthHistogramTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 0)
        _obj = DragenFragmentLengthHistogramFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenCnvMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenCnvMetrics.objects.count(), 0)
        _obj = DragenCnvMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenCnvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenMappingMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenMappingMetrics.objects.count(), 0)
        _obj = DragenMappingMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenMappingMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenPloidyEstimationMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 0)
        _obj = DragenPloidyEstimationMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionCoverageMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 0)
        _obj = DragenRegionCoverageMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionFineHistTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionFineHist.objects.count(), 0)
        _obj = DragenRegionFineHistFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionFineHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionHistTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionHist.objects.count(), 0)
        _obj = DragenRegionHistFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRegionOverallMeanCovTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 0)
        _obj = DragenRegionOverallMeanCovFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenRohMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenRohMetrics.objects.count(), 0)
        _obj = DragenRohMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenRohMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenStrucvarMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenSvMetrics.objects.count(), 0)
        _obj = DragenSvMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenSvMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenTrimmerMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 0)
        _obj = DragenTrimmerMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenVcHethomRatioMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 0)
        _obj = DragenVcHethomRatioMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenVcMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenVcMetrics.objects.count(), 0)
        _obj = DragenVcMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenVcMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenTimeMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenTimeMetrics.objects.count(), 0)
        _obj = DragenTimeMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenTimeMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsContigMeanCovMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 0)
        _obj = DragenWgsContigMeanCovMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsCoverageMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 0)
        _obj = DragenWgsCoverageMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsFineHistTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsFineHist.objects.count(), 0)
        _obj = DragenWgsFineHistFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsFineHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsHistTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsHist.objects.count(), 0)
        _obj = DragenWgsHistFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsHist.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class DragenWgsOverallMeanCovTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 0)
        _obj = DragenWgsOverallMeanCovFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class SamtoolsStatsMainMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(SamtoolsStatsMainMetrics.objects.count(), 0)
        _obj = SamtoolsStatsMainMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SamtoolsStatsMainMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class SamtoolsStatsSupplementaryMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(SamtoolsStatsSupplementaryMetrics.objects.count(), 0)
        _obj = SamtoolsStatsSupplementaryMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SamtoolsStatsSupplementaryMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class SamtoolsFlagstatMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(SamtoolsFlagstatMetrics.objects.count(), 0)
        _obj = SamtoolsFlagstatMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SamtoolsFlagstatMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class SamtoolsIdxstatsMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(SamtoolsIdxstatsMetrics.objects.count(), 0)
        _obj = SamtoolsIdxstatsMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(SamtoolsIdxstatsMetrics.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class CraminoMetricsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(CraminoMetrics.objects.count(), 0)
        _obj = CraminoMetricsFactory()  # noqa: F841
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CraminoMetrics.objects.count(), 1)


class VarfishPydanticTest(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_smoke(self):
        SampleReadStatsFactory()
        RegionCoverageStatsFactory()
        InsertSizeStatsFactory()
        DetailedAlignmentCountsFactory()
        SampleAlignmentStatsFactory()
        RegionVariantStatsFactory()
        SampleSeqvarStatsFactory()
        SampleStrucvarStatsFactory()
        VarfishStatsFactory()

from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import dragen as io_dragen
import cases_qc.io.utils
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
from cases_qc.tests.factories import CaseQcFactory
from cases_qc.tests.helpers import extract_from_dict


@freeze_time("2012-01-14 12:00:01")
class TryCastTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_try_cast_empty_string_none(self):
        self.assertIsNone(cases_qc.io.utils.try_cast("", [int, None]))
        self.assertIsNone(cases_qc.io.utils.try_cast("", [str, None]))
        self.assertIsNone(cases_qc.io.utils.try_cast("", [None]))
        with self.assertRaises(ValueError):
            cases_qc.io.utils.try_cast("", [int, float])

    def test_try_cast_int_float_str(self):
        self.assertEqual(cases_qc.io.utils.try_cast("42", [int, float, str]), 42)
        self.assertEqual(cases_qc.io.utils.try_cast("42", [float, int, str]), 42.0)
        self.assertEqual(cases_qc.io.utils.try_cast("42.0", [int, float, str]), 42.0)
        self.assertEqual(cases_qc.io.utils.try_cast("x", [int, float, str]), "x")


@freeze_time("2012-01-14 12:00:01")
class DragenLoadCnvMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenCnvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.cnv_metrics.csv") as inputf:
            io_dragen.load_cnv_metrics(input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenCnvMetrics.objects.count(), 1)
        metrics = DragenCnvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenLoadVcHethomRatioMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_hethom_ratio_metrics.csv") as inputf:
            io_dragen.load_vc_hethom_ratio_metrics(input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 1)
        metrics = DragenVcHethomRatioMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenLoadFragmentLengthHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 0)
        with open("cases_qc/tests/data/sample.fragment_length_hist.csv") as inputf:
            io_dragen.load_fragment_length_hist(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenFragmentLengthHistogram.objects.count(), 1)
        hist = DragenFragmentLengthHistogram.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "keys", "values")))


@freeze_time("2012-01-14 12:00:01")
class DragenMappingMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenMappingMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.mapping_metrics.csv") as inputf:
            io_dragen.load_mapping_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenMappingMetrics.objects.count(), 1)
        hist = DragenMappingMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenPloidyEstimationMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.ploidy_estimation_metrics.csv") as inputf:
            io_dragen.load_ploidy_estimation_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenPloidyEstimationMetrics.objects.count(), 1)
        hist = DragenPloidyEstimationMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenRohMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenRohMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.roh_metrics.csv") as inputf:
            io_dragen.load_roh_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenRohMetrics.objects.count(), 1)
        hist = DragenRohMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenVcMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenVcMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenVcMetrics.objects.count(), 1)
        hist = DragenVcMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenSvMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenSvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.sv_metrics.csv") as inputf:
            io_dragen.load_sv_metrics(input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenSvMetrics.objects.count(), 1)
        hist = DragenSvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenTimeMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenTimeMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.time_metrics.csv") as inputf:
            io_dragen.load_time_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenTimeMetrics.objects.count(), 1)
        hist = DragenTimeMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenTrimmerMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenTrimmerMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.trimmer_metrics.csv") as inputf:
            io_dragen.load_trimmer_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenTrimmerMetrics.objects.count(), 1)
        hist = DragenTrimmerMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenVcMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenVcMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenVcMetrics.objects.count(), 1)
        hist = DragenVcMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenWgsContigMeanCovMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_contig_mean_cov.csv") as inputf:
            io_dragen.load_wgs_contig_mean_cov(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 1)
        hist = DragenWgsContigMeanCovMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenWgsCoverageMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_coverage_metrics.csv") as inputf:
            io_dragen.load_wgs_coverage_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenWgsCoverageMetrics.objects.count(), 1)
        hist = DragenWgsCoverageMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenWgsFineHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsFineHist.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_fine_hist.csv") as inputf:
            io_dragen.load_wgs_fine_hist(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenWgsFineHist.objects.count(), 1)
        hist = DragenWgsFineHist.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "keys", "values")))


@freeze_time("2012-01-14 12:00:01")
class DragenWgsHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsHist.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_hist.csv") as inputf:
            io_dragen.load_wgs_hist(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenWgsHist.objects.count(), 1)
        hist = DragenWgsHist.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "keys", "values")))


@freeze_time("2012-01-14 12:00:01")
class DragenWgsOverallMeanCovTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_overall_mean_cov.csv") as inputf:
            io_dragen.load_wgs_overall_mean_cov(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenWgsOverallMeanCov.objects.count(), 1)
        hist = DragenWgsOverallMeanCov.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenRegionCoverageMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.qc-coverage-region-3_coverage_metrics.csv") as inputf:
            io_dragen.load_region_coverage_metrics(
                sample="NA12878", region_name="region-3", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenRegionCoverageMetrics.objects.count(), 1)
        hist = DragenRegionCoverageMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "region_name", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenRegionFineHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenRegionFineHist.objects.count(), 0)
        with open("cases_qc/tests/data/sample.qc-coverage-region-3_fine_hist.csv") as inputf:
            io_dragen.load_region_fine_hist(
                sample="NA12878", region_name="region-3", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenRegionFineHist.objects.count(), 1)
        hist = DragenRegionFineHist.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "region_name", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenRegionHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenRegionHist.objects.count(), 0)
        with open("cases_qc/tests/data/sample.qc-coverage-region-3_hist.csv") as inputf:
            io_dragen.load_region_hist(
                sample="NA12878", region_name="region-3", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenRegionHist.objects.count(), 1)
        hist = DragenRegionHist.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "region_name", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class DragenRegionOverallMeanCovTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 0)
        with open("cases_qc/tests/data/sample.qc-coverage-region-3_overall_mean_cov.csv") as inputf:
            io_dragen.load_region_overall_mean_cov(
                sample="NA12878", region_name="region-3", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenRegionOverallMeanCov.objects.count(), 1)
        hist = DragenRegionOverallMeanCov.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "region_name", "metrics")))

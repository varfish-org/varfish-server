import typing

from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import dragen as io_dragen
from cases_qc.models import (
    DragenCnvMetrics,
    DragenFragmentLengthHistogram,
    DragenMappingMetrics,
    DragenPloidyEstimationMetrics,
    DragenRohMetrics,
    DragenSvMetrics,
    DragenTimeMetrics,
    DragenTrimmerMetrics,
    DragenVcHethomRatioMetrics,
    DragenWgsContigMeanCovMetrics,
    DragenWgsCoverageMetrics,
    DragenWgsFineHist,
    DragenWgsHistMetrics,
    SeqvarMetrics,
)
from cases_qc.tests.factories import CaseQcFactory


def extract_from_dict(vals: typing.Any, keys: typing.Iterable[str]) -> dict[str, typing.Any]:
    """Helper to extract certain values from the dictionary."""
    return {key: value for key, value in vars(vals).items() if key in keys}


@freeze_time("2012-01-14 12:00:01")
class TryCastTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_try_cast_empty_string_none(self):
        self.assertIsNone(io_dragen.try_cast("", [int, None]))
        self.assertIsNone(io_dragen.try_cast("", [str, None]))
        self.assertIsNone(io_dragen.try_cast("", [None]))
        with self.assertRaises(ValueError):
            io_dragen.try_cast("", [int, float])

    def test_try_cast_int_float_str(self):
        self.assertEqual(io_dragen.try_cast("42", [int, float, str]), 42)
        self.assertEqual(io_dragen.try_cast("42", [float, int, str]), 42.0)
        self.assertEqual(io_dragen.try_cast("42.0", [int, float, str]), 42.0)
        self.assertEqual(io_dragen.try_cast("x", [int, float, str]), "x")


@freeze_time("2012-01-14 12:00:01")
class LoadCnvMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenCnvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.cnv_metrics.csv") as inputf:
            io_dragen.load_cnv_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenCnvMetrics.objects.count(), 1)
        metrics = DragenCnvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class LoadVcHethomRatioMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_hethom_ratio_metrics.csv") as inputf:
            io_dragen.load_vc_hethom_ratio_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenVcHethomRatioMetrics.objects.count(), 1)
        metrics = DragenVcHethomRatioMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class LoadFragmentLengthHistTest(TestCaseSnapshot, TestCase):
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
class MappingMetricsTest(TestCaseSnapshot, TestCase):
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
class PloidyEstimationMetricsTest(TestCaseSnapshot, TestCase):
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
class RohMetricsTest(TestCaseSnapshot, TestCase):
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
class VcMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(SeqvarMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(SeqvarMetrics.objects.count(), 1)
        hist = SeqvarMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class StrucvarMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenSvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.sv_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenSvMetrics.objects.count(), 1)
        hist = DragenSvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class TimeMetricsTest(TestCaseSnapshot, TestCase):
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
class TrimmerMetricsTest(TestCaseSnapshot, TestCase):
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
class VcMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(SeqvarMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(SeqvarMetrics.objects.count(), 1)
        hist = SeqvarMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsContigMeanCovMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_contig_mean_cov.csv") as inputf:
            io_dragen.load_wgs_contig_mean_cov_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(DragenWgsContigMeanCovMetrics.objects.count(), 1)
        hist = DragenWgsContigMeanCovMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsCoverageMetricsTest(TestCaseSnapshot, TestCase):
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
class WgsFineHistTest(TestCaseSnapshot, TestCase):
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
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsHistMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(DragenWgsHistMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_hist.csv") as inputf:
            io_dragen.load_wgs_hist(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(DragenWgsHistMetrics.objects.count(), 1)
        hist = DragenWgsHistMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))

import typing

from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import dragen as io_dragen
from cases_qc.models import (
    CnvMetrics,
    FragmentLengthHistogram,
    MappingMetrics,
    PloidyEstimationMetrics,
    RohMetrics,
    SeqvarMetrics,
    SvMetrics,
    TimeMetrics,
    TrimmerMetrics,
    VcHethomRatioMetrics,
    WgsContigMeanCovMetrics,
    WgsCoverageMetrics,
    WgsFineHist,
    WgsHistMetrics,
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
        self.assertEqual(CnvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.cnv_metrics.csv") as inputf:
            io_dragen.load_cnv_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(CnvMetrics.objects.count(), 1)
        metrics = CnvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class LoadVcHethomRatioMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(VcHethomRatioMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.vc_hethom_ratio_metrics.csv") as inputf:
            io_dragen.load_vc_hethom_ratio_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(VcHethomRatioMetrics.objects.count(), 1)
        metrics = VcHethomRatioMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(extract_from_dict(metrics, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class LoadFragmentLengthHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(FragmentLengthHistogram.objects.count(), 0)
        with open("cases_qc/tests/data/sample.fragment_length_hist.csv") as inputf:
            io_dragen.load_fragment_length_hist(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(FragmentLengthHistogram.objects.count(), 1)
        hist = FragmentLengthHistogram.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "keys", "values")))


@freeze_time("2012-01-14 12:00:01")
class MappingMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(MappingMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.mapping_metrics.csv") as inputf:
            io_dragen.load_mapping_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(MappingMetrics.objects.count(), 1)
        hist = MappingMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class PloidyEstimationMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(PloidyEstimationMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.ploidy_estimation_metrics.csv") as inputf:
            io_dragen.load_ploidy_estimation_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(PloidyEstimationMetrics.objects.count(), 1)
        hist = PloidyEstimationMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class RohMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(RohMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.roh_metrics.csv") as inputf:
            io_dragen.load_roh_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(RohMetrics.objects.count(), 1)
        hist = RohMetrics.objects.first()

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
        self.assertEqual(SvMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.sv_metrics.csv") as inputf:
            io_dragen.load_vc_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(SvMetrics.objects.count(), 1)
        hist = SvMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class TimeMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(TimeMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.time_metrics.csv") as inputf:
            io_dragen.load_time_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(TimeMetrics.objects.count(), 1)
        hist = TimeMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class TrimmerMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(TrimmerMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.trimmer_metrics.csv") as inputf:
            io_dragen.load_trimmer_metrics(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(TrimmerMetrics.objects.count(), 1)
        hist = TrimmerMetrics.objects.first()

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
        self.assertEqual(WgsContigMeanCovMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_contig_mean_cov.csv") as inputf:
            io_dragen.load_wgs_contig_mean_cov_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(WgsContigMeanCovMetrics.objects.count(), 1)
        hist = WgsContigMeanCovMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsCoverageMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(WgsCoverageMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_coverage_metrics.csv") as inputf:
            io_dragen.load_wgs_coverage_metrics(
                sample="NA12878", input_file=inputf, caseqc=self.caseqc
            )

        self.assertEqual(WgsCoverageMetrics.objects.count(), 1)
        hist = WgsCoverageMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsFineHistTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(WgsFineHist.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_fine_hist.csv") as inputf:
            io_dragen.load_wgs_fine_hist(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(WgsFineHist.objects.count(), 1)
        hist = WgsFineHist.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))


@freeze_time("2012-01-14 12:00:01")
class WgsHistMetricsTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(WgsHistMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.wgs_hist.csv") as inputf:
            io_dragen.load_wgs_hist(sample="NA12878", input_file=inputf, caseqc=self.caseqc)

        self.assertEqual(WgsHistMetrics.objects.count(), 1)
        hist = WgsHistMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(hist).keys()))
        self.assertMatchSnapshot(extract_from_dict(hist, ("sample", "metrics")))

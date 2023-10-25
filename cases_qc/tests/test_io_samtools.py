from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import samtools as io_samtools
from cases_qc.models.samtools import (
    BcftoolsStatsMetrics,
    SamtoolsFlagstatMetrics,
    SamtoolsIdxstatsMetrics,
    SamtoolsStatsMainMetrics,
    SamtoolsStatsSupplementaryMetrics,
)
from cases_qc.tests import helpers
from cases_qc.tests.factories import CaseQcFactory


@freeze_time("2012-01-14 12:00:01")
class SamtoolsLoadBcftoolsStatsTest(
    helpers.FixRandomSeedMixin, helpers.ResetFactoryCountersMixin, TestCase, TestCaseSnapshot
):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(BcftoolsStatsMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.bcftools-stats.txt") as inputf:
            io_samtools.load_bcftools_stats(
                input_file=inputf, caseqc=self.caseqc, file_identifier_to_individual={}
            )

        self.assertEqual(BcftoolsStatsMetrics.objects.count(), 1)
        metrics = BcftoolsStatsMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(
            helpers.extract_from_dict(
                metrics,
                (
                    "sample",
                    "caseqc",
                    "sample",
                    "sn",
                    "tstv",
                    "sis",
                    "af",
                    "qual",
                    "idd",
                    "st",
                    "dp",
                ),
            )
        )


@freeze_time("2012-01-14 12:00:01")
class SamtoolsLoadSamtoolsFlagstatTest(
    helpers.FixRandomSeedMixin, helpers.ResetFactoryCountersMixin, TestCase, TestCaseSnapshot
):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(SamtoolsFlagstatMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.samtools-flagstat.txt") as inputf:
            io_samtools.load_samtools_flagstat(
                sample="NA12878-PCRF450-1",
                input_file=inputf,
                caseqc=self.caseqc,
                file_identifier_to_individual={},
            )

        self.assertEqual(SamtoolsFlagstatMetrics.objects.count(), 1)
        metrics = SamtoolsFlagstatMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(
            helpers.extract_from_dict(metrics, ("sample", "qc_pass", "qc_fail"))
        )


@freeze_time("2012-01-14 12:00:01")
class SamtoolsLoadSamtoolsStatsTest(
    helpers.FixRandomSeedMixin, helpers.ResetFactoryCountersMixin, TestCase, TestCaseSnapshot
):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(SamtoolsStatsMainMetrics.objects.count(), 0)
        self.assertEqual(SamtoolsStatsSupplementaryMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.samtools-stats.txt") as inputf:
            io_samtools.load_samtools_stats(
                sample="NA12878-PCRF450-1",
                input_file=inputf,
                caseqc=self.caseqc,
                file_identifier_to_individual={},
            )

        self.assertEqual(SamtoolsStatsMainMetrics.objects.count(), 1)
        self.assertEqual(SamtoolsStatsSupplementaryMetrics.objects.count(), 1)

        main_metrics = SamtoolsStatsMainMetrics.objects.first()
        self.assertMatchSnapshot(list(vars(main_metrics).keys()))
        self.assertMatchSnapshot(
            helpers.extract_from_dict(
                main_metrics,
                (
                    "sample",
                    "isize",
                    "cov",
                    "gcd",
                    "frl",
                    "lrl",
                    "idd",
                    "ffq",
                    "lfq",
                    "fbc",
                ),
            )
        )

        supp_metrics = SamtoolsStatsMainMetrics.objects.first()
        self.assertMatchSnapshot(list(vars(supp_metrics).keys()))
        self.assertMatchSnapshot(
            helpers.extract_from_dict(
                supp_metrics,
                (
                    "sample",
                    "gcf",
                    "gcl",
                    "gcc",
                    "gct",
                    "rl",
                    "mapq",
                    "ic",
                ),
            )
        )


@freeze_time("2012-01-14 12:00:01")
class SamtoolsLoadSamtoolsIdxstatsTest(
    helpers.FixRandomSeedMixin, helpers.ResetFactoryCountersMixin, TestCase, TestCaseSnapshot
):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(SamtoolsIdxstatsMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.samtools-idxstats.txt") as inputf:
            io_samtools.load_samtools_idxstats(
                sample="NA12878-PCRF450-1",
                input_file=inputf,
                caseqc=self.caseqc,
                file_identifier_to_individual={},
            )

        self.assertEqual(SamtoolsIdxstatsMetrics.objects.count(), 1)
        metrics = SamtoolsIdxstatsMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(helpers.extract_from_dict(metrics, ("sample", "records")))

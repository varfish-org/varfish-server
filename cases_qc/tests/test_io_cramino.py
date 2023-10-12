from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import cramino as io_cramino
from cases_qc.models.cramino import CraminoMetrics
from cases_qc.tests.factories import CaseQcFactory
from cases_qc.tests.helpers import extract_from_dict


@freeze_time("2012-01-14 12:00:01")
class CraminoLoadTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(CraminoMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.cramino.txt") as inputf:
            io_cramino.load_cramino(
                sample="sample",
                input_file=inputf,
                caseqc=self.caseqc,
                file_identifier_to_individual={},
            )

        self.assertEqual(CraminoMetrics.objects.count(), 1)
        metrics = CraminoMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(
            extract_from_dict(
                metrics,
                (
                    "sample",
                    "caseqc",
                    "summary",
                    "chrom_counts",
                ),
            )
        )

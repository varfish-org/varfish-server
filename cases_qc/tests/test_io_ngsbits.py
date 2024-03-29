from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases_qc.io import ngsbits as io_ngsbits
from cases_qc.models.ngsbits import NgsbitsMappingqcMetrics
from cases_qc.tests import helpers
from cases_qc.tests.factories import CaseQcFactory


@freeze_time("2012-01-14 12:00:01")
class NgsbitsMappingqcLoadTest(
    helpers.FixRandomSeedMixin, helpers.ResetFactoryCountersMixin, TestCase, TestCaseSnapshot
):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

        self.caseqc = CaseQcFactory()

    def test_load(self):
        self.assertEqual(NgsbitsMappingqcMetrics.objects.count(), 0)
        with open("cases_qc/tests/data/sample.ngsbits-mappingqc.txt") as inputf:
            io_ngsbits.load_mappingqc(
                sample="sample",
                region_name="WGS",
                input_file=inputf,
                caseqc=self.caseqc,
                file_identifier_to_individual={},
            )

        self.assertEqual(NgsbitsMappingqcMetrics.objects.count(), 1)
        metrics = NgsbitsMappingqcMetrics.objects.first()

        self.assertMatchSnapshot(list(vars(metrics).keys()))
        self.assertMatchSnapshot(
            helpers.extract_from_dict(
                metrics,
                (
                    "sample",
                    "caseqc",
                    "records",
                ),
            )
        )

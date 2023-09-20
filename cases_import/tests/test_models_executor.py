"""Tests for the ``CaseImportBackgroundJobExecutor`` and related code.

This has been broken away from ``test_models.py`` for better structure.
"""
import os
from unittest import mock
from projectroles.app_settings import AppSettingAPI
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases.models import Case
from cases.tests.factories import IndividualFactory, PedigreeFactory
from cases_import.models import CaseImportAction, CaseImportBackgroundJobExecutor
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory
from cases_qc.models import CaseQc, CnvMetrics
from seqmeta.tests.factories import TargetBedFileFactory
from variants.tests.factories import CaseFactory


class ExecutorTestMixin:
    def _setUpExecutor(self, action, fac_kwargs=None):
        super().setUp()
        self.user = self.make_user()
        self.caseimportaction = CaseImportActionFactory(
            action=action,
            state=CaseImportAction.STATE_SUBMITTED,
            overwrite_terms=True,
            **(fac_kwargs or {}),
        )
        self.caseimportbackgroundjob = CaseImportBackgroundJobFactory(
            caseimportaction=self.caseimportaction,
            user=self.user,
        )
        self.project = self.caseimportbackgroundjob.project
        self.executor = CaseImportBackgroundJobExecutor(self.caseimportbackgroundjob.pk)
        self.targetbedfile = TargetBedFileFactory(
            file_uri=self.caseimportaction.payload["proband"]["files"][0]["uri"]
        )

        app_settings = AppSettingAPI()
        app_settings.set(
            app_name="cases_import",
            setting_name="import_data_protocol",
            value="file",
            project=self.project,
        )


class ImportCreateTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create

    This will only create the external files objects but not perform an import of quality
    control data etc because the ``family.yaml`` file does not contain actionable files.
    """

    def setUp(self):
        self._setUpExecutor(CaseImportAction.ACTION_CREATE)

    def test_run(self):
        self.assertEqual(Case.objects.count(), 0)
        self.executor.run()
        self.assertEqual(Case.objects.count(), 1)


class ImportCreateWithDragenQcTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create and external files for Dragen QC.

    This will actually run the import of the Dragen QC files.
    """

    def setUp(self):
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_dragen_qc.yaml"
            },
        )

    @mock.patch("cases_qc.io.dragen.load_cnv_metrics")
    def test_run(self, mock_load_cnv_metrics):
        """Test import of a case with full set of Dragen QC files.

        This test is pretty long because there are a lot of files to import ;-).
        """
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        caseqc = CaseQc.objects.first()

        mock_load_cnv_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
        )
        self.assertEqual(
            mock_load_cnv_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.cnv_metrics.csv"),
        )


class ImportUpdateTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=update"""

    def setUp(self):
        super().setUp()
        self._setUpExecutor(CaseImportAction.ACTION_UPDATE)
        self.case = CaseFactory(
            project=self.project,
            name=self.caseimportaction.payload["pedigree"]["persons"][0]["familyId"],
        )
        self.pedigree = PedigreeFactory(case=self.case)
        self.keep_invidual = IndividualFactory(
            pedigree=self.pedigree,
            name=self.caseimportaction.payload["proband"]["id"],
        )
        self.abundant_individual = IndividualFactory(
            pedigree=self.pedigree,
        )

    def test_run(self):
        self.assertEqual(Case.objects.count(), 1)
        self.executor.run()
        self.assertEqual(Case.objects.count(), 1)


class ImportDeleteTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=delete"""

    def setUp(self):
        super().setUp()
        self._setUpExecutor(CaseImportAction.ACTION_DELETE)
        self.case = CaseFactory(
            project=self.project,
            name=self.caseimportaction.payload["pedigree"]["persons"][0]["familyId"],
        )

    def test_run(self):
        self.assertEqual(Case.objects.count(), 1)
        self.executor.run()
        self.assertEqual(Case.objects.count(), 0)

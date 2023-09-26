import random
import unittest.mock

from django.urls import reverse
from freezegun import freeze_time
from projectroles.app_settings import AppSettingAPI
from snapshottest.unittest import TestCase as TestCaseSnapshot

from cases_import.models import CaseImportAction, CaseImportBackgroundJobExecutor
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory
from cases_import.tests.test_models_executor import ExecutorTestMixin
from cases_qc.tests import helpers
from cases_qc.tests.factories import CaseQcFactory, DragenWgsOverallMeanCovFactory
from seqmeta.tests.factories import TargetBedFileFactory
from variants.models import Case
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class CaseQcRetrieveApiViewTest(helpers.FixRandomSeedMixin, ApiViewTestBase, TestCaseSnapshot):
    """Test retrieval of ``CaseQc`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_retrieve_existing(self):
        """GET on existing case"""
        caseqc = CaseQcFactory(case__project=self.project)
        _entry = DragenWgsOverallMeanCovFactory(caseqc=caseqc)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_qc:api-caseqc-retrieve",
                    kwargs={"case": caseqc.case.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 200)
        self.assertMatchSnapshot(response.json())

    def test_retrieve_nonexisting(self):
        """GET on non-existing case"""
        case = CaseFactory(project=self.project)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_qc:api-caseqc-retrieve",
                    kwargs={"case": case.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 404)


@freeze_time("2012-01-14 12:00:01")
class VarfishStatsRetrieveApiView(helpers.FixRandomSeedMixin, ApiViewTestBase, ExecutorTestMixin, TestCaseSnapshot):
    """Test retrieval / building of ``VarfishStats`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def _setUpExecutor(self, fac_kwargs: dict[str, str]):
        self.caseimportaction = CaseImportActionFactory(
            action=CaseImportAction.ACTION_CREATE,
            state=CaseImportAction.STATE_SUBMITTED,
            overwrite_terms=True,
            **(fac_kwargs or {}),
        )
        self.caseimportbackgroundjob = CaseImportBackgroundJobFactory(
            project=self.project,
            caseimportaction=self.caseimportaction,
            user=self.superuser,
        )
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

    def test_retrieve(self):
        """Import the case files and retrieve the ``VarfishStats`` object"""
        self._setUpExecutor(
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_dragen_qc.yaml"
            },
        )
        self.assertEqual(Case.objects.count(), 0)
        self.executor.run()
        self.assertEqual(Case.objects.count(), 1)
        case = Case.objects.first()

        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_qc:api-varfishstats-retrieve",
                    kwargs={"case": case.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 200)
        self.assertMatchSnapshot(response.json())

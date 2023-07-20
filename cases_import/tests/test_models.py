from freezegun import freeze_time
from google.protobuf.json_format import ParseDict
from phenopackets import Family
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase
import yaml

from cases_import.models import CaseImportAction, CaseImportBackgroundJob, build_legacy_pedigree
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(CaseImportAction.objects.count(), 0)
        _action = CaseImportActionFactory()
        self.assertEqual(CaseImportAction.objects.count(), 1)

    def test_update(self):
        action = CaseImportActionFactory()
        self.assertEqual(action.state, CaseImportAction.STATE_DRAFT)
        action.state = CaseImportAction.STATE_SUBMITTED
        action.save()
        action.refresh_from_db()
        self.assertEqual(action.state, CaseImportAction.STATE_SUBMITTED)


class CaseImportBackgroundJobTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff
        self.user = self.make_user("test_user")

    def test_create_and_exercise(self):
        self.assertEqual(CaseImportBackgroundJob.objects.count(), 0)
        self.assertEqual(CaseImportAction.objects.count(), 0)
        job = CaseImportBackgroundJobFactory(user=self.user)
        self.assertEqual(CaseImportBackgroundJob.objects.count(), 1)
        self.assertEqual(CaseImportAction.objects.count(), 1)

        self.assertEqual(job.get_human_readable_type(), "Import a case into VarFish")
        self.assertEqual(
            job.get_absolute_url(), f"/cases-import/import-case-bg-job/{job.sodar_uuid}/"
        )


class BuildLegacyModelTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)
        self.family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())

    def test_asevalidate_ok(self):
        result = build_legacy_pedigree(self.family)
        self.assertMatchSnapshot(result, "legacy pedigree for family.yaml")

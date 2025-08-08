from freezegun import freeze_time
from test_plus import TestCase

from cases_import.models.base import CaseImportAction, CaseImportBackgroundJob
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(CaseImportAction.objects.count(), 0)
        _action = CaseImportActionFactory()  # noqa: F841
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
        super().setUp()
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

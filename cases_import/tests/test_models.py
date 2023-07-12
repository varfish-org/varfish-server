from freezegun import freeze_time
from test_plus import TestCase

from cases_import.models import CaseImportAction
from cases_import.tests.factories import CaseImportActionFactory


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionTest(TestCase):
    """Tests for the ``CaseImportAction`` model class."""

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

"""Tests for the tasks module.

We do glass-box-tests here and mock out the called functions only.  The functionality itself must then be tested
separately but that's fine.
"""
from unittest import mock
from unittest.mock import Mock, call
from unittest.mock import patch

from test_plus.test import TestCase

from variants.tests.factories import CaseWithVariantSetFactory
from .. import tasks
from ..models import ExportFileBgJob
from bgjobs.models import BackgroundJob
from projectroles.models import Project


class ExportFileTaskTest(TestCase):
    def setUp(self):
        self.user = self.make_user("superuser")
        case, variant_set, _ = CaseWithVariantSetFactory.get("small")
        self.bg_job = BackgroundJob.objects.create(
            name="job name",
            project=Project.objects.first(),
            job_type="variants.export_file_bg_job",
            user=self.user,
        )
        self.export_job = ExportFileBgJob.objects.create(
            project=self.bg_job.project,
            bg_job=self.bg_job,
            case=case,
            query_args={"some": "args"},
            file_type="xlsx",
        )

    @patch("variants.file_export.export_case")
    def test_correct_function_call(self, mock_export_case):
        tasks.export_file_task(self.export_job.pk)
        mock_export_case.assert_called_once_with(self.export_job)


class ClearExpiredExportedFilesTest(TestCase):
    @patch("variants.file_export.clear_expired_exported_files")
    def test_calls_correct_function(self, mock_clear_expired_exported_files):
        tasks.clear_expired_exported_files()
        mock_clear_expired_exported_files.assert_called_once_with()


class ClearInactiveVariantSetsTest(TestCase):
    @patch("variants.models.cleanup_variant_sets")
    def test_calls_correct_function(self, mock_clear_inactive_variant_sets):
        tasks.clear_inactive_variant_sets()
        mock_clear_inactive_variant_sets.assert_called_once_with()


class RefreshVariantsSmallVariantSummaryTest(TestCase):
    @patch("variants.models.refresh_variants_smallvariantsummary")
    def test_calls_correct_function(self, mock_refresh_variants_smallvariantsummary):
        tasks.refresh_variants_smallvariantsummary()
        mock_refresh_variants_smallvariantsummary.assert_called_once_with()


class ClearOldKioskCasesTest(TestCase):
    @patch("variants.models.clear_old_kiosk_cases")
    def test_calls_correct_function(self, mock_clear_old_kiosk_cases):
        tasks.clear_old_kiosk_cases()
        mock_clear_old_kiosk_cases.assert_called_once_with()


class SetupPeriodicTasksTest(TestCase):
    def test_calls_correct_function(self):
        sender = Mock()
        tasks.setup_periodic_tasks(sender)
        sender.add_periodic_task.assert_has_calls(
            [call(schedule=mock.ANY, sig=mock.ANY), call(schedule=mock.ANY, sig=mock.ANY),]
        )

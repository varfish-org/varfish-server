"""Tests for the tasks module.

We do glass-box-tests here and mock out the called functions only.  The functionality itself must then be tested
separately but that's fine.
"""

from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch

from test_plus.test import TestCase

from . import test_views
from .. import tasks
from ..models import ExportFileBgJob, Case
from bgjobs.models import BackgroundJob
from projectroles.models import Project


class ExportFileTaskTest(TestCase):
    def setUp(self):
        self.user = self.make_user("superuser")
        test_views.fixture_setup_case(self.user)
        self.bg_job = BackgroundJob.objects.create(
            name="job name",
            project=Project.objects.first(),
            job_type="variants.export_file_bg_job",
            user=self.user,
        )
        self.export_job = ExportFileBgJob.objects.create(
            project=self.bg_job.project,
            bg_job=self.bg_job,
            case=Case.objects.first(),
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


class SetupPeriodicTasksTest(TestCase):
    def test_calls_correct_function(self):
        sender = Mock()
        tasks.setup_periodic_tasks(sender)
        sender.add_periodic_task.assert_called_once_with(schedule=mock.ANY, signature=mock.ANY)

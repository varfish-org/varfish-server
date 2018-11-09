"""Tests for the ``file_export`` module."""

import gzip
import io
from datetime import timedelta
import tempfile
from unittest.mock import MagicMock, Mock, patch, sentinel

from django.utils import timezone
import openpyxl
from test_plus.test import TestCase
from timeline.models import ProjectEvent

from . import test_views
from .. import file_export, forms
from ..models import ExportFileBgJob, Case
from bgjobs.models import BackgroundJob
from projectroles.models import Project


class ExportTestBase(TestCase):
    """Base class for testing exports.

    Sets up the database fixtures for project, case, and small variants.
    """

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
            query_args={},
            file_type="xlsx",
        )


class CaseExporterTest(ExportTestBase):
    def setUp(self):
        super().setUp()
        # Here, the query arguments actually matter
        self.export_job.query_args = test_views.DEFAULT_FILTER_FORM_SETTING
        self.export_job.query_args["effects"] = [
            effect
            for name, effect in forms.FILTER_FORM_TRANSLATE_EFFECTS.items()
            if test_views.DEFAULT_FILTER_FORM_SETTING[name]
        ]
        self.export_job.query_args["A_export"] = True
        self.export_job.save()

    def test_export_tsv(self):
        with file_export.CaseExporterTsv(self.export_job) as exporter:
            result = str(exporter.generate(), "utf-8")
        arrs = [line.split("\t") for line in result.split("\n")]
        self._test_tabular(arrs, True)

    def _test_tabular(self, arrs, has_trailing):
        self.assertEquals(len(arrs), 4 + int(has_trailing))
        self.assertEquals(len(arrs[0]), 29)
        self.assertSequenceEqual(arrs[0][:3], ["Chromosome", "Position", "Reference bases"])
        self.assertSequenceEqual(
            arrs[0][-5:],
            [
                "A Genotype",
                "A Gt. Quality",
                "A Alternative depth",
                "A Total depth",
                "A Alternate allele fraction",
            ],
        )
        self.assertSequenceEqual(arrs[1][:3], ["chr1", "100", "A"])
        self.assertSequenceEqual(arrs[1][-5:], ["0/1", "99", "15", "30", "0.5"])
        self.assertSequenceEqual(arrs[2][:3], ["chr1", "200", "A"])
        self.assertSequenceEqual(arrs[2][-5:], ["0/1", "99", "15", "30", "0.5"])
        self.assertSequenceEqual(arrs[3][:3], ["chr1", "300", "A"])
        self.assertSequenceEqual(arrs[3][-5:], ["0/1", "99", "15", "30", "0.5"])
        if has_trailing:
            self.assertSequenceEqual(arrs[4], [""])

    def test_export_vcf(self):
        with file_export.CaseExporterVcf(self.export_job) as exporter:
            result = exporter.generate()
        unzipped = gzip.GzipFile(fileobj=io.BytesIO(result), mode="rb").read()
        lines = str(unzipped, "utf-8").split("\n")
        header = [l for l in lines if l.startswith("#")]
        content = [l for l in lines if not l.startswith("#")]
        self.assertEquals(len(header), 31)
        self.assertEquals(header[0], "##fileformat=VCFv4.2")
        self.assertEquals(header[-1], "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tA")
        self.assertEquals(len(content), 4)
        self.assertEquals(
            content[0].split("\t"),
            ["1", "100", ".", "A", "G", ".", ".", ".", "GT:GQ:AD:DP", "0/1:99:15:30"],
        )
        self.assertEquals(
            content[1].split("\t"),
            ["1", "200", ".", "A", "G", ".", ".", ".", "GT:GQ:AD:DP", "0/1:99:15:30"],
        )
        self.assertEquals(
            content[2].split("\t"),
            ["1", "300", ".", "A", "G", ".", ".", ".", "GT:GQ:AD:DP", "0/1:99:15:30"],
        )
        self.assertEquals(content[3], "")

    def test_export_xlsx(self):
        with file_export.CaseExporterXlsx(self.export_job) as exporter:
            result = exporter.generate()
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            temp_file.write(result)
            temp_file.flush()
            workbook = openpyxl.load_workbook(temp_file.name)
            self.assertEquals(workbook.sheetnames, ["Variants", "Metadata"])
            variants_sheet = workbook["Variants"]
            arrs = [[cell.value for cell in row] for row in variants_sheet.rows]
            self._test_tabular(arrs, False)


def _fake_generate(_self):
    """Helper used for patching away ``CaseExporter*.generate``."""
    return bytes("test bytes", "utf-8")


class ExportCaseTest(ExportTestBase):
    """Test the ``export_case()`` function.

    We mock out the ``CaseExporter*`` class in the spirit of testing just the export driver code unit in
    ``export_case()``.
    """

    def _run_test(self, file_type):
        # Set the file type that we want to test into the export file job
        self.export_job.file_type = file_type
        self.export_job.save()
        # Run code under test
        file_export.export_case(self.export_job)
        # Check immediate result
        self.assertIsNotNone(self.export_job.export_result)
        self.assertEquals(self.export_job.export_result.payload, _fake_generate(self))
        # Check side effects
        self.assertEquals(ProjectEvent.objects.count(), 2)

    @patch.object(file_export.CaseExporterTsv, "generate", new=_fake_generate, create=True)
    def test_export_tsv(self):
        self._run_test("tsv")

    @patch.object(file_export.CaseExporterXlsx, "generate", new=_fake_generate, create=True)
    def test_export_xlsx(self):
        self._run_test("xlsx")

    @patch.object(file_export.CaseExporterVcf, "generate", new=_fake_generate, create=True)
    def test_export_vcf(self):
        self._run_test("vcf")


class ClearExpiredExportedFilesTest(ExportTestBase):
    """Test the ``clear_expired_exported_files()`` function."""

    def testWithExpired(self):
        file_export.ExportFileJobResult.objects.create(
            job=self.export_job, expiry_time=timezone.now() - timedelta(days=1)
        )
        self.assertEquals(file_export.ExportFileJobResult.objects.count(), 1)
        file_export.clear_expired_exported_files()
        self.assertEquals(file_export.ExportFileJobResult.objects.count(), 0)

    def testWithNonExpired(self):
        file_export.ExportFileJobResult.objects.create(
            job=self.export_job, expiry_time=timezone.now() + timedelta(days=1)
        )
        self.assertEquals(file_export.ExportFileJobResult.objects.count(), 1)
        file_export.clear_expired_exported_files()
        self.assertEquals(file_export.ExportFileJobResult.objects.count(), 1)

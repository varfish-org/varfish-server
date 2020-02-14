"""Tests for the ``file_export`` module."""

import gzip
import io
from datetime import timedelta
import tempfile
from unittest.mock import patch

from django.utils import timezone
import openpyxl
from test_plus.test import TestCase
from timeline.models import ProjectEvent

from variants.tests.factories import (
    SmallVariantSetFactory,
    SmallVariantFactory,
    FormDataFactory,
    ProcessedFormDataFactory,
    ResubmitFormDataFactory,
)
from . import test_views
from .. import file_export, forms
from ..models import ExportFileBgJob
from bgjobs.models import BackgroundJob
from projectroles.models import Project


class ExportTestBase(TestCase):
    """Base class for testing exports.

    Sets up the database fixtures for project, case, and small variants.
    """

    def setUp(self):
        self.user = self.make_user("superuser")
        self.variant_set = SmallVariantSetFactory()
        self.small_vars = SmallVariantFactory.create_batch(3, variant_set=self.variant_set)
        self.case = self.variant_set.case
        self.bg_job = BackgroundJob.objects.create(
            name="job name",
            project=Project.objects.first(),
            job_type="variants.export_file_bg_job",
            user=self.user,
        )
        self.export_job = ExportFileBgJob.objects.create(
            project=self.bg_job.project,
            bg_job=self.bg_job,
            case=self.case,
            query_args={"export_flags": True, "export_comments": True},
            file_type="xlsx",
        )


class CaseExporterTest(ExportTestBase):
    def setUp(self):
        super().setUp()
        # Here, the query arguments actually matter
        self.export_job.query_args = vars(
            ResubmitFormDataFactory(submit="download", names=self.case.get_members())
        )

    def test_export_tsv(self):
        with file_export.CaseExporterTsv(self.export_job, self.export_job.case) as exporter:
            result = str(exporter.generate(), "utf-8")
        arrs = [line.split("\t") for line in result.split("\n")]
        self._test_tabular(arrs, True)

    def _test_tabular(self, arrs, has_trailing):
        self.assertEquals(len(arrs), 4 + int(has_trailing))
        # TODO: also test without flags and comments
        self.assertEquals(len(arrs[0]), 46)
        self.assertSequenceEqual(arrs[0][:3], ["Chromosome", "Position", "Reference bases"])
        self.assertSequenceEqual(
            arrs[0][-5:],
            [
                "%s Genotype" % self.case.pedigree[0]["patient"],
                "%s Gt. Quality" % self.case.pedigree[0]["patient"],
                "%s Alternative depth" % self.case.pedigree[0]["patient"],
                "%s Total depth" % self.case.pedigree[0]["patient"],
                "%s Alternate allele fraction" % self.case.pedigree[0]["patient"],
            ],
        )
        for i, small_var in enumerate(self.small_vars):
            self.assertSequenceEqual(
                arrs[i + 1][:3],
                ["chr" + small_var.chromosome, str(small_var.start), small_var.reference],
            )
            self.assertSequenceEqual(
                arrs[i + 1][-5:],
                list(
                    map(
                        str,
                        [
                            small_var.genotype[self.case.pedigree[-1]["patient"]]["gt"],
                            small_var.genotype[self.case.pedigree[-1]["patient"]]["gq"],
                            small_var.genotype[self.case.pedigree[-1]["patient"]]["ad"],
                            small_var.genotype[self.case.pedigree[-1]["patient"]]["dp"],
                            small_var.genotype[self.case.pedigree[-1]["patient"]]["ad"]
                            / small_var.genotype[self.case.pedigree[-1]["patient"]]["dp"],
                        ],
                    )
                ),
            )
        if has_trailing:
            self.assertSequenceEqual(arrs[4], [""])

    def test_export_vcf(self):
        with file_export.CaseExporterVcf(self.export_job, self.export_job.case) as exporter:
            result = exporter.generate()
        unzipped = gzip.GzipFile(fileobj=io.BytesIO(result), mode="rb").read()
        lines = str(unzipped, "utf-8").split("\n")
        header = [l for l in lines if l.startswith("#")]
        content = [l for l in lines if not l.startswith("#")]
        self.assertEquals(len(header), 31)
        self.assertEquals(header[0], "##fileformat=VCFv4.2")
        self.assertEquals(
            header[-1],
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t%s"
            % self.case.pedigree[0]["patient"],
        )
        self.assertEquals(len(content), 4)
        for i, small_var in enumerate(self.small_vars):
            genotype = small_var.genotype[self.case.pedigree[0]["patient"]]
            self.assertEquals(
                content[i].split("\t"),
                list(
                    map(
                        str,
                        [
                            small_var.chromosome,
                            small_var.start,
                            ".",
                            small_var.reference,
                            small_var.alternative,
                            ".",
                            ".",
                            ".",
                            "GT:GQ:AD:DP",
                            "%s:%s:%s:%s"
                            % (genotype["gt"], genotype["gq"], genotype["ad"], genotype["dp"]),
                        ],
                    )
                ),
            )
        self.assertEquals(content[3], "")

    def test_export_xlsx(self):
        with file_export.CaseExporterXlsx(self.export_job, self.export_job.case) as exporter:
            result = exporter.generate()
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            temp_file.write(result)
            temp_file.flush()
            workbook = openpyxl.load_workbook(temp_file.name)
            # TODO: also test without commments
            self.assertEquals(workbook.sheetnames, ["Variants", "Comments", "Metadata"])
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
        self.assertEquals(ProjectEvent.objects.count(), 1)

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

"""Tests for the ``CaseImportBackgroundJobExecutor`` and related code.

This has been broken away from ``test_models.py`` for better structure.
"""

import itertools
import os
from unittest import mock

from google.protobuf.json_format import ParseDict
from phenopackets import Family
from projectroles.app_settings import AppSettingAPI
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase
import yaml

from cases.models import Case
from cases.tests.factories import IndividualFactory, PedigreeFactory
from cases_files.models import AbstractFile, PedigreeExternalFile, PedigreeInternalFile
from cases_import.models.base import CaseImportAction
from cases_import.models.executors import (
    CaseImportBackgroundJobExecutor,
    build_legacy_pedigree,
    release_from_family,
)
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory
from cases_qc.models import CaseQc
from cases_qc.tests import helpers
from seqmeta.tests.factories import TargetBedFileFactory
from variants.tests.factories import CaseFactory


class ExecutorTestMixin:
    def _setUpExecutor(self, action, fac_kwargs=None):
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


class ImportCreateTest(ExecutorTestMixin, TestCase):
    """Test the executor with action=create

    This will only create the external files objects but not perform an import of quality
    control data etc because the ``family.yaml`` file does not contain actionable files.
    """

    def setUp(self):
        super().setUp()
        self._setUpExecutor(CaseImportAction.ACTION_CREATE)

    def test_run(self):
        self.assertEqual(Case.objects.count(), 0)
        self.executor.run()
        self.assertEqual(Case.objects.count(), 1)


# Cannot use freeze time here as real S3 access is used here and the server
# refuses connection otherwise.
# @freeze_time("2012-01-14 12:00:01")
class ImportCreateWithSeqvarsVcfTest(
    helpers.FixRandomSeedMixin, ExecutorTestMixin, TestCaseSnapshot, TestCase
):
    """Test the executor with action=create and external files for seqvar VCF."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={"path_phenopacket_yaml": "cases_import/tests/data/singleton_seqvars.yaml"},
        )

    @mock.patch("cases_import.models.executors.VariantImportExecutorBase.run_worker")
    def test_run(self, mock_seqvarsimprotexecutor_run_worker):
        """Test import of a case with a seqvars VCF file."""
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(PedigreeExternalFile.objects.count(), 0)
        self.assertEqual(PedigreeInternalFile.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(PedigreeExternalFile.objects.count(), 2)
        self.assertEqual(PedigreeInternalFile.objects.count(), 3)

        call_list = mock_seqvarsimprotexecutor_run_worker.call_args_list
        self.assertEqual(len(call_list), 2)
        call_1_args = call_list[0].kwargs["args"]
        self.assertEqual(call_1_args[0:3], ["seqvars", "ingest", "--file-date"])
        self.assertEqual(len(call_1_args), 18)
        call_2_args = call_list[1].kwargs["args"]
        self.assertEqual(call_2_args[0:3], ["seqvars", "prefilter", "--params"])
        self.assertEqual(len(call_2_args), 6)

        keys_shared = (
            # cannot freeze time
            # "date_created",
            # "date_modified",
            "designation",
            "file_attributes",
            "genombuild",
            "identifier_map",
            "mimetype",
            "path",
        )
        keys_ext = tuple(
            itertools.chain(
                keys_shared,
                (
                    "available",
                    # cannot freeze time
                    # "last_checked",
                ),
            )
        )
        dicts_ext = [
            helpers.extract_from_dict(obj, keys=keys_ext)
            for obj in PedigreeExternalFile.objects.all()
        ]
        self.assertMatchSnapshot(dicts_ext, "external files")

        keys_int = tuple(itertools.chain(keys_shared, ("checksum",)))
        dicts_int = [
            helpers.extract_from_dict(obj, keys=keys_int)
            for obj in PedigreeInternalFile.objects.all().order_by("id")
        ]
        self.assertMatchSnapshot(dicts_int, "internal files")


# Cannot use freeze time here as real S3 access is used here and the server
# refuses connection otherwise.
# @freeze_time("2012-01-14 12:00:01")
class ImportCreateWithStrucvarsVcfTest(
    helpers.FixRandomSeedMixin, ExecutorTestMixin, TestCaseSnapshot, TestCase
):
    """Test the executor with action=create and external files for seqvar VCF."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_strucvars.yaml"
            },
        )

    @mock.patch("cases_import.models.executors.VariantImportExecutorBase.run_worker")
    def test_run(self, mock_strucvarsimprotexecutor_run_worker):
        """Test import of a case with a strucvars VCF file."""
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(PedigreeExternalFile.objects.count(), 0)
        self.assertEqual(PedigreeInternalFile.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(PedigreeExternalFile.objects.count(), 2)
        self.assertEqual(PedigreeInternalFile.objects.count(), 3)

        call_list = mock_strucvarsimprotexecutor_run_worker.call_args_list
        self.assertEqual(len(call_list), 1)
        call_1_args = call_list[0].kwargs["args"]
        self.assertEqual(call_1_args[0:3], ["strucvars", "ingest", "--file-date"])
        self.assertEqual(len(call_1_args), 16)

        keys_shared = (
            # cannot freeze time
            # "date_created",
            # "date_modified",
            "designation",
            "file_attributes",
            "genombuild",
            "identifier_map",
            "mimetype",
            "path",
        )
        keys_ext = tuple(
            itertools.chain(
                keys_shared,
                (
                    "available",
                    # cannot freeze time
                    # "last_checked",
                ),
            )
        )
        dicts_ext = [
            helpers.extract_from_dict(obj, keys=keys_ext)
            for obj in PedigreeExternalFile.objects.all()
        ]
        self.assertMatchSnapshot(dicts_ext, "external files")

        keys_int = tuple(itertools.chain(keys_shared, ("checksum",)))
        dicts_int = [
            helpers.extract_from_dict(obj, keys=keys_int)
            for obj in PedigreeInternalFile.objects.all().order_by("id")
        ]
        self.assertMatchSnapshot(dicts_int, "internal files")


class ImportCreateWithDragenQcTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create and external files for Dragen QC.

    This will actually run the import of the Dragen QC files.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_dragen_qc.yaml"
            },
        )

    @mock.patch("cases_qc.io.dragen.load_cnv_metrics")
    @mock.patch("cases_qc.io.dragen.load_fragment_length_hist")
    @mock.patch("cases_qc.io.dragen.load_mapping_metrics")
    @mock.patch("cases_qc.io.dragen.load_ploidy_estimation_metrics")
    @mock.patch("cases_qc.io.dragen.load_roh_metrics")
    @mock.patch("cases_qc.io.dragen.load_sv_metrics")
    @mock.patch("cases_qc.io.dragen.load_time_metrics")
    @mock.patch("cases_qc.io.dragen.load_trimmer_metrics")
    @mock.patch("cases_qc.io.dragen.load_vc_hethom_ratio_metrics")
    @mock.patch("cases_qc.io.dragen.load_vc_metrics")
    @mock.patch("cases_qc.io.dragen.load_wgs_contig_mean_cov")
    @mock.patch("cases_qc.io.dragen.load_wgs_coverage_metrics")
    @mock.patch("cases_qc.io.dragen.load_wgs_fine_hist")
    @mock.patch("cases_qc.io.dragen.load_wgs_hist")
    @mock.patch("cases_qc.io.dragen.load_wgs_overall_mean_cov")
    @mock.patch("cases_qc.io.dragen.load_region_coverage_metrics")
    @mock.patch("cases_qc.io.dragen.load_region_fine_hist")
    @mock.patch("cases_qc.io.dragen.load_region_hist")
    @mock.patch("cases_qc.io.dragen.load_region_overall_mean_cov")
    def test_run(
        self,
        mock_load_region_overall_mean_cov,
        mock_load_region_hist,
        mock_load_region_fine_hist,
        mock_load_region_coverage_metrics,
        mock_load_wgs_overall_mean_cov,
        mock_load_wgs_hist_metrics,
        mock_load_wgs_fine_hist,
        mock_load_wgs_coverage_metrics,
        mock_load_wgs_contig_mean_cov,
        mock_load_vc_metrics,
        mock_load_vc_hethom_ratio_metrics,
        mock_load_trimmer_metrics,
        mock_load_time_metrics,
        mock_load_sv_metrics,
        mock_load_roh_metrics,
        mock_load_ploidy_estimation_metrics,
        mock_load_mapping_metrics,
        mock_load_fragment_length_hist,
        mock_load_cnv_metrics,
    ):
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
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_cnv_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.cnv_metrics.csv"),
        )

        mock_load_fragment_length_hist.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_fragment_length_hist.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.fragment_length_hist.csv"),
        )

        mock_load_mapping_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_mapping_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.mapping_metrics.csv"),
        )

        mock_load_ploidy_estimation_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_ploidy_estimation_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.ploidy_estimation_metrics.csv"),
        )

        mock_load_roh_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_roh_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.roh_metrics.csv"),
        )

        mock_load_sv_metrics.assert_called_once_with(
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_sv_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.sv_metrics.csv"),
        )

        mock_load_time_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_time_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.time_metrics.csv"),
        )

        mock_load_trimmer_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_trimmer_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.trimmer_metrics.csv"),
        )

        mock_load_vc_hethom_ratio_metrics.assert_called_once_with(
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_vc_hethom_ratio_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.vc_hethom_ratio_metrics.csv"),
        )

        mock_load_vc_metrics.assert_called_once_with(
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_vc_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.vc_metrics.csv"),
        )

        mock_load_wgs_contig_mean_cov.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_wgs_contig_mean_cov.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.wgs_contig_mean_cov.csv"),
        )

        mock_load_wgs_coverage_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_wgs_coverage_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.wgs_coverage_metrics.csv"),
        )

        mock_load_wgs_fine_hist.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_wgs_fine_hist.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.wgs_fine_hist.csv"),
        )

        mock_load_wgs_hist_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_wgs_hist_metrics.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.wgs_hist.csv"),
        )

        mock_load_wgs_overall_mean_cov.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_wgs_overall_mean_cov.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.wgs_overall_mean_cov.csv"),
        )

        mock_load_region_overall_mean_cov.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            region_name="region-3",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_region_overall_mean_cov.call_args[1]["input_file"].name,
            os.path.realpath(
                "cases_qc/tests/data/sample.qc-coverage-region-3_overall_mean_cov.csv"
            ),
        )

        mock_load_region_hist.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            region_name="region-3",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_region_hist.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.qc-coverage-region-3_hist.csv"),
        )

        mock_load_region_fine_hist.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            region_name="region-3",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_region_fine_hist.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.qc-coverage-region-3_fine_hist.csv"),
        )

        mock_load_region_coverage_metrics.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            region_name="region-3",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_region_coverage_metrics.call_args[1]["input_file"].name,
            os.path.realpath(
                "cases_qc/tests/data/sample.qc-coverage-region-3_coverage_metrics.csv"
            ),
        )


class ImportCreateWithSamtoolsQcTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create and external files for Samtools QC.

    This will actually run the import of the Samtools QC files.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_samtools_qc.yaml"
            },
        )

    @mock.patch("cases_qc.io.samtools.load_bcftools_stats")
    @mock.patch("cases_qc.io.samtools.load_samtools_flagstat")
    @mock.patch("cases_qc.io.samtools.load_samtools_stats")
    def test_run(
        self,
        mock_load_samtools_stats,
        mock_load_samtools_flagstat,
        mock_load_bcftools_stats,
    ):
        """Test import of a case with full set of Samtools QC files."""
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        caseqc = CaseQc.objects.first()

        mock_load_samtools_stats.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_samtools_stats.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.samtools-stats.txt"),
        )

        mock_load_samtools_flagstat.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_samtools_flagstat.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.samtools-flagstat.txt"),
        )

        mock_load_bcftools_stats.assert_called_once_with(
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_bcftools_stats.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.bcftools-stats.txt"),
        )


class ImportCreateWithCraminoQcTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create and external files for cramino QC.

    This will actually run the import of the cramino QC file.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_cramino_qc.yaml"
            },
        )

    @mock.patch("cases_qc.io.cramino.load_cramino")
    def test_run(
        self,
        mock_load_cramino,
    ):
        """Test import of a case with full set of Samtools QC files."""
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        caseqc = CaseQc.objects.first()

        mock_load_cramino.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_cramino.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.cramino.txt"),
        )


class ImportCreateWithNgsbitsQcTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create and external files for ngs-bits QC.

    This will actually run the import of the ngs-bits QC files.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self._setUpExecutor(
            CaseImportAction.ACTION_CREATE,
            fac_kwargs={
                "path_phenopacket_yaml": "cases_import/tests/data/singleton_ngsbits_qc.yaml"
            },
        )

    @mock.patch("cases_qc.io.ngsbits.load_mappingqc")
    def test_run(
        self,
        mock_load_mappingqc,
    ):
        """Test import of a case with full set of Samtools QC files."""
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)

        self.executor.run()

        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(CaseQc.objects.count(), 1)
        caseqc = CaseQc.objects.first()

        mock_load_mappingqc.assert_called_once_with(
            sample="NA12878-PCRF450-1",
            input_file=mock.ANY,
            region_name="WGS",
            caseqc=caseqc,
            file_identifier_to_individual={"NA12878-PCRF450-1": "index"},
        )
        self.assertEqual(
            mock_load_mappingqc.call_args[1]["input_file"].name,
            os.path.realpath("cases_qc/tests/data/sample.ngsbits-mappingqc.txt"),
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


class BuildLegacyModelTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)
        self.family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())

    def test_build_legacy_pedigree(self):
        result = build_legacy_pedigree(self.family)
        self.assertMatchSnapshot(result, "legacy pedigree for family.yaml")


class BuildReleaseFromFamilyTest(TestCaseSnapshot, TestCase):
    def setUp(self):
        with open("cases_import/tests/data/family.yaml", "rt") as inputf:
            self.fam_dict = yaml.safe_load(inputf)

    def test_release_from_family_grch37(self):
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        family.proband.files[0].file_attributes["genomebuild"] = "GRCh37"
        result = release_from_family(family)
        self.assertEqual(AbstractFile.GENOMEBUILD_GRCH37, result)

    def test_release_from_family_grch38(self):
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        family.proband.files[0].file_attributes["genomebuild"] = "GRCh38"
        result = release_from_family(family)
        self.assertEqual(AbstractFile.GENOMEBUILD_GRCH38, result)

    def test_release_from_family_none(self):
        family: Family = ParseDict(js_dict=self.fam_dict["family"], message=Family())
        family.proband.files[0].file_attributes["genomebuild"] = "xxx"
        result = release_from_family(family)
        self.assertEqual(None, result)

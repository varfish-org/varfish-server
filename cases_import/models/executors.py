import json
import os
import shutil
import subprocess
import tempfile
import typing
import uuid

from bgjobs.models import LOG_LEVEL_ERROR, LOG_LEVEL_INFO, LOG_LEVEL_WARNING
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import fsspec
from google.protobuf.json_format import ParseDict, ParseError
import phenopackets
from phenopackets import Family
from projectroles.app_settings import AppSettingAPI
from projectroles.models import Project
import pydantic

from cases.models import Disease, Individual, Pedigree, PhenotypicFeature, write_pedigree_as_plink
from cases_files.models import (
    AbstractFile,
    IndividualExternalFile,
    IndividualInternalFile,
    PedigreeExternalFile,
    PedigreeInternalFile,
)
from cases_import.models.base import CaseImportAction, CaseImportBackgroundJob
from cases_import.proto import Assay, ExternalFileDesignation
from cases_qc.io import cramino as io_cramino
from cases_qc.io import dragen as io_dragen
from cases_qc.io import ngsbits as io_ngsbits
from cases_qc.io import samtools as io_samtools
from cases_qc.models import CaseQc
from config.common import PrefilterConfig
from seqmeta.models import TargetBedFile
from variants.models import Case


class FileSystemOptions(pydantic.BaseModel):
    protocol: str
    host: str | None
    path: str | None
    port: str | None
    user: str | None
    password: str | None
    use_https: bool = False


def uuid_frag(uuid: uuid.UUID | str) -> str:
    """Create path fragment from UUID by splitting off the first two characters."""
    uuid_str = str(uuid)
    return f"{uuid_str[:2]}/{uuid_str[2:]}"


class FileSystemWrapper:
    """Wrapper around ``fsspec.AbstractFileSystem`` that checks paths for local files."""

    def __init__(self, options: FileSystemOptions):
        self.options = options
        self.external_fs = self._build_fs(options)

    def open(self, path: str, *args, **kwargs) -> typing.IO:
        """Wrapper around ``fsspec.AbstractFileSystem.open`` that checks paths for local
        files.
        """
        if self.options.protocol == "file":
            path = self._normalized_local_path(path)
        return self.external_fs.open(path, *args, **kwargs)

    def _normalized_local_path(self, path: str) -> str:
        """Check that the given local path does not try to escape out of the prefix."""
        if self.options.protocol == "file" and settings.VARFISH_CASE_IMPORT_FILE_PREFIX:
            tmp = os.path.join(settings.VARFISH_CASE_IMPORT_FILE_PREFIX, path)
            tmp = os.path.normpath(tmp)
            if not tmp.startswith(settings.VARFISH_CASE_IMPORT_FILE_PREFIX):
                raise ValueError("path is not within forced prefix")
            return tmp
        else:
            return path

    def _build_fs(self, options: FileSystemOptions) -> fsspec.AbstractFileSystem:
        if options.protocol == "file":
            if not settings.VARFISH_CASE_IMPORT_ALLOW_FILE:
                raise ValueError(  # pragma: no cover
                    "file protocol must be enabled with VARFISH_CASE_IMPORT_ALLOW_FILE"
                )
            return fsspec.filesystem("file")
        elif options.protocol in ("http", "https"):
            return fsspec.filesystem(
                options.protocol,
                host=options.host,
                port=int(options.port) if options.port else None,
                username=options.user,
                password=options.password,
            )
        elif options.protocol == "s3":
            kwargs = {}
            kwargs = {}
            if options.user:
                kwargs["key"] = options.user
            if options.password:
                kwargs["secret"] = options.password
            if options.host:
                port = f":{options.port}" if options.port else ""
                http = "https" if options.use_https else "http"
                kwargs["client_kwargs"] = {"endpoint_url": f"{http}://{options.host}{port}"}
            return fsspec.filesystem("s3", **kwargs)
        else:
            raise ValueError(f"invalid protocol {options.protocol}")


class FileImportExecutorBase:
    """Base class for file improter classes.

    Import is done in the context of a specific project with the storage information.
    """

    def __init__(self, project: Project):
        self.project = project

        #: `FileSystemOptions` to use for the file improt
        self.external_fs_options = self._build_fs_options(project=self.project)
        #: `FileSystemWrapper` to use for extenal file system.
        self.external_fs = FileSystemWrapper(self.external_fs_options)

    def _build_fs_options(self, project: Project) -> FileSystemOptions:
        """Build `FileSystemOptions` from project settings."""
        app_settings = AppSettingAPI()
        kwargs = {"app_name": "cases_import", "project": project}

        path = app_settings.get(setting_name="import_data_path", **kwargs) or None
        if not path:
            path = "/"
        elif path and not path.startswith("/"):
            path = f"/{path}"
        while path.endswith("/") and len(path) > 1:
            path = path[:-1]

        return FileSystemOptions(
            protocol=app_settings.get(setting_name="import_data_protocol", **kwargs),
            host=app_settings.get(setting_name="import_data_host", **kwargs) or None,
            path=path,
            port=app_settings.get(setting_name="import_data_port", **kwargs) or None,
            user=app_settings.get(setting_name="import_data_user", **kwargs) or None,
            password=app_settings.get(setting_name="import_data_password", **kwargs) or None,
        )


class DragenQcImportExecutor(FileImportExecutorBase):
    """Helper class for importing Dragen-style QC from external files in a case."""

    def __init__(self, case: Case):
        super().__init__(case.project)
        self.case = case
        #: Map the extended detailed type to the handler function, per-sample.
        self.handlers_individual = {
            "x-dragen-qc-fragment-length-hist": self._import_dragen_qc_fragment_length_hist,
            "x-dragen-qc-mapping-metrics": self._import_dragen_qc_mapping_metrics,
            "x-dragen-qc-ploidy-estimation-metrics": self._import_dragen_qc_ploidy_estimation_metrics,
            "x-dragen-qc-roh-metrics": self._import_dragen_qc_roh_metrics,
            "x-dragen-qc-time-metrics": self._import_dragen_qc_time_metrics,
            "x-dragen-qc-trimmer-metrics": self._import_dragen_qc_trimmer_metrics,
            "x-dragen-qc-wgs-contig-mean-cov": self._import_dragen_qc_wgs_contig_mean_cov,
            "x-dragen-qc-wgs-coverage-metrics": self._import_dragen_qc_wgs_coverage_metrics,
            "x-dragen-qc-wgs-fine-hist": self._import_dragen_qc_wgs_fine_hist,
            "x-dragen-qc-wgs-hist": self._import_dragen_qc_wgs_hist,
            "x-dragen-qc-wgs-overall-mean-cov": self._import_dragen_qc_wgs_overall_mean_cov,
            "x-dragen-qc-region-coverage-metrics": self._import_dragen_qc_region_coverage_metrics,
            "x-dragen-qc-region-coverage-fine-hist": self._import_dragen_qc_region_coverage_fine_hist,
            "x-dragen-qc-region-coverage-hist": self._import_dragen_qc_region_coverage_hist,
            "x-dragen-qc-region-coverage-overall-mean-cov": self._import_dragen_qc_region_coverage_overall_mean_cov,
            "x-samtools-qc-samtools-flagstat": self._import_samtools_qc_samtools_flagstat,
            "x-samtools-qc-samtools-idxstats": self._import_samtools_qc_samtools_idxstats,
            "x-samtools-qc-samtools-stats": self._import_samtools_qc_samtools_stats,
            "x-cramino-qc-cramino": self._import_cramino_qc_cramino,
            "x-ngsbits-qc-mappingqc": self._import_ngsbits_qc_mappingqc,
        }
        #: Map the extended detailed type to the handler function, for pedigree.
        self.handlers_pedigree = {
            "x-dragen-qc-cnv-metrics": self._import_dragen_qc_cnv_metrics,
            "x-dragen-qc-sv-metrics": self._import_dragen_qc_sv_metrics,
            "x-dragen-qc-vc-hethom-ratio-metrics": self._import_dragen_qc_vc_hethom_ratio_metrics,
            "x-dragen-qc-vc-metrics": self._import_dragen_qc_vc_metrics,
            "x-samtools-qc-bcftools-stats": self._import_samtools_qc_bcftools_stats,
        }

    def run(self):
        caseqc = CaseQc.objects.create(case=self.case)
        pedigree = self.case.pedigree_obj
        for external_file in pedigree.pedigreeexternalfile_set.all():
            self._import_externalfile(external_file, caseqc)
        for individual in pedigree.individual_set.all():
            for external_file in IndividualExternalFile.objects.filter(individual=individual):
                self._import_externalfile(external_file, caseqc, individual_name=individual.name)
        with transaction.atomic():
            caseqc.refresh_from_db()
            if caseqc.state == CaseQc.STATE_DRAFT:
                caseqc.state = CaseQc.STATE_ACTIVE
                caseqc.save()

    def _import_externalfile(
        self,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        individual_name: str | None = None,
    ):
        """Import quality metrics from external file, if any.

        To be loaded as QC info, the designation must be "quality_control" and the mimetype
        must be "text/csv+{x_detailed_type}" where ``x_detailed_type`` must be one of the
        known ones.
        """
        fa = external_file.file_attributes
        if fa.get("designation") != "quality_control":
            return  # can only handle QC data here
        file_identifier_to_individual: typing.Dict[str, str] = {
            v: k for k, v in (external_file.identifier_map or {}).items()
        }

        mimetype = str(fa.get("mimetype", ""))
        if mimetype.count("+") != 1:
            return  # no detailed type

        _base_mimetype, x_detailed_type = mimetype.split("+", 1)
        maps = (self.handlers_individual, self.handlers_pedigree)
        if not any(x_detailed_type in map for map in maps):
            return  # no handler configured

        if x_detailed_type in self.handlers_individual:
            self.handlers_individual[x_detailed_type](
                individual_name, external_file, caseqc, file_identifier_to_individual
            )
        else:
            assert x_detailed_type in self.handlers_pedigree
            self.handlers_pedigree[x_detailed_type](
                external_file, caseqc, file_identifier_to_individual
            )

    def _import_dragen_qc_cnv_metrics(
        self,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_cnv_metrics(
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_fragment_length_hist(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_fragment_length_hist(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_mapping_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_mapping_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_ploidy_estimation_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_ploidy_estimation_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_roh_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_roh_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_sv_metrics(
        self,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_sv_metrics(
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_time_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_time_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_trimmer_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_trimmer_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_vc_hethom_ratio_metrics(
        self,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_vc_hethom_ratio_metrics(
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_vc_metrics(
        self,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_vc_metrics(
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_wgs_contig_mean_cov(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_wgs_contig_mean_cov(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_wgs_coverage_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_wgs_coverage_metrics(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_wgs_fine_hist(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_wgs_fine_hist(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_wgs_hist(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_wgs_hist(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_wgs_overall_mean_cov(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_wgs_overall_mean_cov(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_region_coverage_metrics(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        region_name = external_file.file_attributes.get("region_name", "UNKNOWN REGION")
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_region_coverage_metrics(
                sample=sample_name,
                region_name=region_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_region_coverage_fine_hist(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        region_name = external_file.file_attributes.get("region_name", "UNKNOWN REGION")
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_region_fine_hist(
                sample=sample_name,
                region_name=region_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_region_coverage_hist(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        region_name = external_file.file_attributes.get("region_name", "UNKNOWN REGION")
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_region_hist(
                sample=sample_name,
                region_name=region_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_dragen_qc_region_coverage_overall_mean_cov(
        self,
        individual_name: str,
        external_file: IndividualExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        region_name = external_file.file_attributes.get("region_name", "UNKNOWN REGION")
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_dragen.load_region_overall_mean_cov(
                sample=sample_name,
                region_name=region_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_samtools_qc_bcftools_stats(
        self,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_samtools.load_bcftools_stats(
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_samtools_qc_samtools_flagstat(
        self,
        individual_name: str,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_samtools.load_samtools_flagstat(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_samtools_qc_samtools_idxstats(
        self,
        individual_name: str,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_samtools.load_samtools_idxstats(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_samtools_qc_samtools_stats(
        self,
        individual_name: str,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_samtools.load_samtools_stats(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_cramino_qc_cramino(
        self,
        individual_name: str,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_cramino.load_cramino(
                sample=sample_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )

    def _import_ngsbits_qc_mappingqc(
        self,
        individual_name: str,
        external_file: PedigreeExternalFile,
        caseqc: CaseQc,
        file_identifier_to_individual: typing.Dict[str, str] | None = None,
    ):
        sample_name = external_file.identifier_map.get(individual_name, individual_name)
        region_name = external_file.file_attributes.get("region_name", "UNKNOWN REGION")
        with self.external_fs.open(external_file.path, "rt") as inputf:
            io_ngsbits.load_mappingqc(
                sample=sample_name,
                region_name=region_name,
                input_file=inputf,
                caseqc=caseqc,
                file_identifier_to_individual=file_identifier_to_individual or {},
            )


#: Mapping of sex from phenopackets to representation in Individual.
SEX_MAP = {
    phenopackets.Sex.MALE: Individual.SEX_MALE,
    phenopackets.Sex.FEMALE: Individual.SEX_FEMALE,
    phenopackets.Sex.OTHER_SEX: Individual.SEX_OTHER,
}
#: Mapping of karyotypic sex from phenopackets to representation in Individual.
KARYOTYPIC_SEX_MAP = {
    phenopackets.KaryotypicSex.UNKNOWN_KARYOTYPE: Individual.KARYOTYPE_UNKNOWN,
    phenopackets.KaryotypicSex.XX: Individual.KARYOTYPE_XX,
    phenopackets.KaryotypicSex.XY: Individual.KARYOTYPE_XY,
    phenopackets.KaryotypicSex.XO: Individual.KARYOTYPE_XO,
    phenopackets.KaryotypicSex.XXY: Individual.KARYOTYPE_XXY,
    phenopackets.KaryotypicSex.XXX: Individual.KARYOTYPE_XXX,
    phenopackets.KaryotypicSex.XXYY: Individual.KARYOTYPE_XXYY,
    phenopackets.KaryotypicSex.XXXY: Individual.KARYOTYPE_XXXY,
    phenopackets.KaryotypicSex.XXXX: Individual.KARYOTYPE_XXXX,
    phenopackets.KaryotypicSex.XYY: Individual.KARYOTYPE_XYY,
    phenopackets.KaryotypicSex.OTHER_KARYOTYPE: Individual.KARYOTYPE_OTHER,
}
ASSAY_MAP = {
    Assay.PANEL_SEQ.value: Individual.ASSAY_PANEL,
    Assay.WES.value: Individual.ASSAY_WES,
    Assay.WGS.value: Individual.ASSAY_WGS,
}


class VariantImportExecutorBase(FileImportExecutorBase):
    """Base class for variant import."""

    var_type: str

    def __init__(self, case: Case, bgjob: CaseImportBackgroundJob):
        super().__init__(case.project)

        #: The Case to import for
        self.case = case
        #: The background job, used for logging and getting unique internal paths
        self.bgjob = bgjob
        #: The `FileSystemOptions` for the internal storage.
        storage_settings = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE
        self.internal_fs_options = FileSystemOptions(
            protocol="s3",
            host=storage_settings.host,
            port=storage_settings.port,
            user=storage_settings.access_key,
            password=storage_settings.secret_key,
            use_https=storage_settings.use_https,
        )
        #: The `FileSystemWrapper` for the internal storage.
        self.internal_fs = FileSystemWrapper(self.internal_fs_options)

    def run(self) -> typing.List[PedigreeInternalFile]:
        """Perform the import.

        :returns: the `PedigreeInternalFile` objects resulting from the import
        """
        ext_vcf_on_s3 = self.copy_external_internal()
        if ext_vcf_on_s3:
            return self.annotate_outer(ext_vcf_on_s3)
        else:
            return []

    def copy_external_internal(self) -> typing.Optional[PedigreeInternalFile]:
        """Copy the external VCF file to the internal storage.

        :return: the corresponding `PedigreeInternalFile` object
        :raises ValueError: if more than one file is found
        """
        # Find files with the correct designation, variant_type, and mimetype; ensure that there
        # is only one such file and bail out otherwise.
        extfile_qs = PedigreeExternalFile.objects.filter(
            pedigree=self.case.pedigree_obj,
            designation=ExternalFileDesignation.VARIANT_CALLS.value,
            file_attributes__variant_type=self.var_type,
            mimetype="text/plain+x-bgzip+x-variant-call-format",
        )
        if extfile_qs.count() > 1:
            raise ValueError(
                f"expected at most one {self.var_type} VCF file, found {extfile_qs.count()}"
            )
        elif extfile_qs.count() == 0:
            return None
        extfile = extfile_qs.first()

        # Copy the file from the external to the internal storage.
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        path_int = (
            f"case-data/{uuid_frag(self.case.sodar_uuid)}/{self.bgjob.sodar_uuid}/"
            f"{self.var_type}/external-copy.vcf.gz"
        )
        path_int_full = f"s3://{bucket}/{path_int}"
        with (
            self.external_fs.open(extfile.path, "rb") as inputf,
            self.internal_fs.open(path_int_full, "wb") as outputf,
        ):
            shutil.copyfileobj(inputf, outputf)

        # Create the `PedigreeInternalFile` record after copying is complete.
        return PedigreeInternalFile.objects.create(
            case=self.case,
            path=path_int,
            genomebuild=extfile.genomebuild,
            mimetype=extfile.mimetype,
            file_attributes=extfile.file_attributes,
            identifier_map=extfile.identifier_map,
            # is copy of the original VCF file
            designation=f"variant_calls/{self.var_type}/orig-copy",
            # checksum=extfile.checksum,  # TODO
            pedigree=self.case.pedigree_obj,
        )

    def annotate_outer(self, vcf_on_s3: PedigreeExternalFile) -> typing.List[PedigreeExternalFile]:
        """Annotate the VCF file from the internal storage.

        Will write temporary PLINK PED file and then call the actual annotation functin.
        """
        with tempfile.NamedTemporaryFile(mode="w+t") as tmpf:
            write_pedigree_as_plink(self.case.pedigree_obj, tmpf)
            tmpf.flush()
            return self.annotate(vcf_on_s3, path_ped=tmpf.name)

    def annotate(
        self, vcf_on_s3: PedigreeExternalFile, path_ped: str
    ) -> typing.List[PedigreeExternalFile]:
        _ = vcf_on_s3
        _ = path_ped
        raise NotImplementedError

    def run_worker(self, args: list[str], env: typing.Dict[str, str] | None = None):
        """Run the worker with the given arguments.

        The worker will create a new VCF file and a TBI file.
        """
        cmd = [settings.WORKER_EXE_PATH, *args]
        subprocess.check_call(cmd, env=env)


class SeqvarsImportExecutor(VariantImportExecutorBase):
    """Run the import of sequence variant import."""

    var_type = "seqvars"

    def run(self) -> typing.List[PedigreeInternalFile]:
        """Override superclass behaviour to also prefilter the VCF file."""
        int_on_s3 = super().run()
        int_vcf_on_s3 = [
            obj
            for obj in int_on_s3
            if obj.designation == f"variant_calls/{self.var_type}/ingested-vcf"
        ]
        if int_vcf_on_s3:
            self.prefilter_seqvars_outer(int_vcf_on_s3[0])
        return int_on_s3

    def annotate(
        self, vcf_on_s3: PedigreeExternalFile, path_ped: str
    ) -> typing.List[PedigreeExternalFile]:
        """Implementation of sequence variant annotation."""
        # Path create path of the new fiel.
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        path_out = (
            f"case-data/{uuid_frag(self.case.sodar_uuid)}/{self.bgjob.sodar_uuid}/"
            "seqvars/ingested.vcf.gz"
        )
        # Create arguments to use.
        args = [
            "seqvars",
            "ingest",
            "--file-date",
            timezone.now().strftime("%Y%m%d"),
            "--case-uuid",
            str(self.case.sodar_uuid),
            "--genomebuild",
            vcf_on_s3.genomebuild,
            "--path-mehari-db",
            f"{settings.WORKER_DB_PATH}/mehari",
            "--path-ped",
            path_ped,
            "--path-in",
            vcf_on_s3.path,
            "--path-out",
            f"{bucket}/{path_out}",
        ]
        # Setup environment so the worker can access the internal S3 storage.
        endpoint_host = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.host
        endpoint_port = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.port
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            "AWS_ACCESS_KEY_ID": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.access_key,
            "AWS_SECRET_ACCESS_KEY": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.secret_key,
            "AWS_ENDPOINT_URL": f"http://{endpoint_host}:{endpoint_port}",
            # "AWS_REGION": "us-east-1",
        }
        # Actually execute the worker.
        self.run_worker(args=args, env=env)
        # Create the `PedigreeInternalFile` record after ingest is complete.
        return [
            PedigreeInternalFile.objects.create(
                case=self.case,
                path=f"{path_out}{suffix}",
                genomebuild=vcf_on_s3.genomebuild,
                mimetype=mimetype,
                identifier_map=vcf_on_s3.identifier_map,
                designation=designation,
                file_attributes={},
                # checksum=extfile.checksum,  # TODO
                pedigree=self.case.pedigree_obj,
            )
            for mimetype, designation, suffix in (
                (
                    "text/plain+x-bgzip+x-variant-call-format",
                    "variant_calls/seqvars/ingested-vcf",
                    "",
                ),
                (
                    "application/octet-stream+x-tabix-tbi-index",
                    "variant_calls/seqvars/ingested-tbi",
                    ".tbi",
                ),
            )
        ]

    def prefilter_seqvars_outer(self, ingested_on_s3: PedigreeInternalFile):
        """Writes out the prefilter configuration JSON to file and then calls the actual
        prefiltration.
        """
        with tempfile.NamedTemporaryFile(mode="w+t") as tmpf:
            configs: list[PrefilterConfig] = settings.VARFISH_CASE_IMPORT_SEQVARS_PREFILTER_CONFIGS
            out_lst = []
            for idx, config in enumerate(configs):
                dirname = os.path.dirname(ingested_on_s3.path)
                prefilter_path = f"{dirname}/prefiltered-{idx}.vcf.gz"
                out_lst.append(
                    PrefilterConfig(
                        **{
                            **config.dict(),
                            "prefilter_path": prefilter_path,
                        }
                    )
                )
            json.dump([obj.dict() for obj in out_lst], tmpf)
            tmpf.flush()
            self.prefilter_seqvars(
                ingested_on_s3=ingested_on_s3, configs=out_lst, path_config=tmpf.name
            )

    def prefilter_seqvars(
        self, ingested_on_s3: PedigreeInternalFile, configs: list[PrefilterConfig], path_config: str
    ):
        """Run prefiltration of sequence variants."""
        # Create arguments to use.
        args = [
            "seqvars",
            "prefilter",
            "--params",
            f"@{path_config}",
            "--path-in",
            ingested_on_s3.path,
        ]
        # Setup environment so the worker can access the internal S3 storage.
        endpoint_host = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.host
        endpoint_port = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.port
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            "AWS_ACCESS_KEY_ID": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.access_key,
            "AWS_SECRET_ACCESS_KEY": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.secret_key,
            "AWS_ENDPOINT_URL": f"http://{endpoint_host}:{endpoint_port}",
            # "AWS_REGION": "us-east-1",
        }
        # Actually execute the worker.
        self.run_worker(args=args, env=env)
        # Create the `PedigreeInternalFile` records after prefilter is complete.
        return [
            PedigreeInternalFile.objects.create(
                case=self.case,
                path=f"{config.prefilter_path}{suffix}",
                genomebuild=ingested_on_s3.genomebuild,
                mimetype=mimetype,
                identifier_map=ingested_on_s3.identifier_map,
                designation=designation,
                file_attributes={
                    "prefilter_config": json.dumps(config.dict()),
                },
                # checksum=extfile.checksum,  # TODO
                pedigree=self.case.pedigree_obj,
            )
            for mimetype, designation, suffix in (
                (
                    "text/plain+x-bgzip+x-variant-call-format",
                    "variant_calls/seqvars/prefiltered-vcf",
                    "",
                ),
                (
                    "application/octet-stream+x-tabix-tbi-index",
                    "variant_calls/seqvars/prefiltered-tbi",
                    ".tbi",
                ),
            )
            for config in configs
        ]


class StrucvarsImportExecutor(VariantImportExecutorBase):
    """Run the import of structural variant import."""

    var_type = "strucvars"

    def annotate(
        self, vcf_on_s3: PedigreeExternalFile, path_ped: str
    ) -> typing.List[PedigreeExternalFile]:
        """Implementation of structural variant annotation."""
        # Path create path of the new fiel.
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        path_out = (
            f"case-data/{uuid_frag(self.case.sodar_uuid)}/{self.bgjob.sodar_uuid}/"
            "strucvars/ingested.vcf.gz"
        )
        # Create arguments to use.
        args = [
            "strucvars",
            "ingest",
            "--file-date",
            timezone.now().strftime("%Y%m%d"),
            "--case-uuid",
            str(self.case.sodar_uuid),
            "--genomebuild",
            vcf_on_s3.genomebuild,
            "--path-mehari-db",
            f"{settings.WORKER_DB_PATH}/mehari",
            "--path-ped",
            path_ped,
            "--path-in",
            vcf_on_s3.path,
            "--path-out",
            f"{bucket}/{path_out}",
        ]
        # Setup environment so the worker can access the internal S3 storage.
        endpoint_host = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.host
        endpoint_port = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.port
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            "AWS_ACCESS_KEY_ID": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.access_key,
            "AWS_SECRET_ACCESS_KEY": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.secret_key,
            "AWS_ENDPOINT_URL": f"http://{endpoint_host}:{endpoint_port}",
            # "AWS_REGION": "us-east-1",
        }
        # Actually execute the worker.
        self.run_worker(args=args, env=env)
        # Create the `PedigreeInternalFile` record after ingest is complete.
        return [
            PedigreeInternalFile.objects.create(
                case=self.case,
                path=f"{path_out}{suffix}",
                genomebuild=vcf_on_s3.genomebuild,
                mimetype=mimetype,
                identifier_map=vcf_on_s3.identifier_map,
                designation=designation,
                file_attributes={},
                # checksum=extfile.checksum,  # TODO
                pedigree=self.case.pedigree_obj,
            )
            for mimetype, designation, suffix in (
                (
                    "text/plain+x-bgzip+x-variant-call-format",
                    "variant_calls/strucvars/ingested-vcf",
                    "",
                ),
                (
                    "application/octet-stream+x-tabix-tbi-index",
                    "variant_calls/strucvars/ingested-tbi",
                    ".tbi",
                ),
            )
        ]


class CaseImportBackgroundJobExecutor:
    """Implementation of ``CaseImportBackgroundJob`` execution."""

    def __init__(self, job_pk: int):
        #: Job record primary key.
        self.job_pk = job_pk
        #: The ``CaseImportBackgroundJob`` object itself.
        self.caseimportbackgroundjob = CaseImportBackgroundJob.objects.get(pk=self.job_pk)

    def run(self):
        """Execute the case import."""
        with self.caseimportbackgroundjob.marks():
            self._run()

    def _run(self):
        if self.caseimportbackgroundjob.caseimportaction.action == CaseImportAction.ACTION_DELETE:
            self._run_delete()
        else:
            self._run_create_or_update()

    def _get_case(self) -> typing.Optional[Case]:
        """Return the case belonging to the job."""
        project = self.caseimportbackgroundjob.project
        case_name = self.caseimportbackgroundjob.caseimportaction.get_case_name()
        return Case.objects.filter(project=project, name=case_name).first()

    def _run_delete(self) -> Case:
        case = self._get_case()
        if case:
            case.delete()
            self.caseimportbackgroundjob.add_log_entry("Case has been deleted successfully")
        else:
            self.caseimportbackgroundjob.add_log_entry(
                "Case to delete not found, skipping", LOG_LEVEL_WARNING
            )

    def _run_create_or_update(self):
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        try:
            family: Family = ParseDict(js_dict=caseimportaction.payload, message=Family())
        except ParseError as e:
            self.caseimportbackgroundjob.add_log_entry(
                f"Problem loading phenopackets.Family: {e}", LOG_LEVEL_ERROR
            )
            raise

        # Creation of the new, empty case or updating the case state of an existing one is
        # done in a transaction as that's quick and we cannot use in-flight issues.
        with transaction.atomic():
            # Create a new case or update the existing on'es state to "updating".
            case = self._create_or_update_case(family)
        if not case:
            return  # break out, logging happend in ``self._create_or_update_case()``.

        if self.caseimportbackgroundjob.caseimportaction.action == CaseImportAction.ACTION_UPDATE:
            # Clear the external and internal files, will be re-created during import.
            self._clear_files(case)
        # Create the external files entries.
        self._create_external_files(case, family)
        # Import the quality control files.
        self._run_qc_file_import(case)
        # Actually perform the seqvars import and annotation with Mehari.
        self._run_seqvars_import(case)
        # Actually perform the strucvars import and annotation with Mehari.
        self._run_strucvars_import(case)
        # Update the case state to "done".
        self._update_case_state(case)

    def _create_or_update_case(self, family: Family) -> typing.Optional[Case]:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        if caseimportaction.action == CaseImportAction.ACTION_CREATE:
            self.caseimportbackgroundjob.add_log_entry("Creating new case")
            return self._create_case(family)
        else:
            self.caseimportbackgroundjob.add_log_entry("Updating existing case")
            return self._update_case(family)

    def _create_case(self, family: Family) -> Case:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        case = Case.objects.create(
            case_version=2,
            state=Case.STATE_IMPORTING,
            project=self.caseimportbackgroundjob.project,
            release=release_from_family(family),
            name=caseimportaction.get_case_name(),
            index=family.proband.id,
            pedigree=build_legacy_pedigree(family),
        )
        self._create_pedigree(case, family)
        return case

    def _family_helper(
        self, family: Family
    ) -> typing.Tuple[
        typing.Dict[str, str],
        typing.Dict[str, str],
        typing.Dict[str, str],
        typing.Dict[str, typing.List[typing.Any]],
        typing.Dict[str, typing.List[typing.Any]],
    ]:
        assay = {
            family.proband.id: ASSAY_MAP[family.proband.measurements[0].assay.id],
        }
        karyotypic_sex = {
            family.proband.id: KARYOTYPIC_SEX_MAP[family.proband.subject.karyotypic_sex],
        }
        targetbedfile_uris = {
            family.proband.id: family.proband.files[0].uri,
        }
        diseases = {family.proband.id: family.proband.diseases}
        features = {family.proband.id: family.proband.phenotypic_features}
        for relative in family.relatives:
            assay[relative.id] = ASSAY_MAP[relative.measurements[0].assay.id]
            karyotypic_sex[relative.id] = KARYOTYPIC_SEX_MAP[relative.subject.karyotypic_sex]
            targetbedfile_uris[relative.id] = relative.files[0].uri
            diseases[relative.id] = relative.diseases
            features[relative.id] = relative.phenotypic_features
        return assay, karyotypic_sex, targetbedfile_uris, diseases, features

    def _create_pedigree(self, case: Case, family: Family) -> Pedigree:
        assay, karyotypic_sex, targetbedfile_uris, diseases, features = self._family_helper(family)
        pedigree = Pedigree.objects.create(case=case)
        for person in family.pedigree.persons:
            targetbedfile = TargetBedFile.objects.get(
                file_uri=targetbedfile_uris[person.individual_id]
            )
            individual = Individual.objects.create(
                pedigree=pedigree,
                name=person.individual_id,
                sex=SEX_MAP[person.sex],
                karyotypic_sex=karyotypic_sex[person.individual_id],
                assay=assay[person.individual_id],
                enrichmentkit=targetbedfile.enrichmentkit,
            )
            for disease in diseases[individual.name]:
                Disease.objects.create(
                    individual=individual,
                    term_id=disease.term.id,
                    term_label=disease.term.label,
                    excluded=bool(disease.excluded),
                )
            for feature in features[individual.name]:
                PhenotypicFeature.objects.create(
                    individual=individual,
                    term_id=feature.type.id,
                    term_label=feature.type.label,
                    excluded=bool(feature.excluded),
                )
        return pedigree

    def _update_case(self, family: Family) -> typing.Optional[Case]:
        caseimportaction = self.caseimportbackgroundjob.caseimportaction
        case = self._get_case()
        if not case:
            self.caseimportbackgroundjob.add_log_entry(
                "Could not find case to update", LOG_LEVEL_ERROR
            )
            return None

        case.case_version = 2
        case.state = Case.STATE_UPDATING
        case.release = release_from_family(family)
        case.name = caseimportaction.get_case_name()
        case.index = family.proband.id
        case.pedigree = build_legacy_pedigree(family)
        case.save()
        self._update_pedigree(case, family)

        return case

    def _update_pedigree(self, case: Case, family: Family):
        assay, karyotypic_sex, targetbedfile_uris, diseases, features = self._family_helper(family)
        family_names = set(assay.keys())

        pedigree = Pedigree.objects.get(case=case)
        individuals = {
            individual.name: individual
            for individual in Individual.objects.filter(pedigree=pedigree)
        }
        pedigree_names = set(individuals.keys())

        # Get names of missing and abundant individuals and those to keep.
        missing = family_names - pedigree_names
        abundant = pedigree_names - family_names
        keep = family_names & pedigree_names

        # Remove abundant individuals.
        for name in abundant:
            individuals[name].delete()

        # Add missing individuals.
        for person in family.pedigree.persons:
            if person.individual_id not in missing:
                continue
            targetbedfile = TargetBedFile.objects.get(
                file_uri=targetbedfile_uris[person.individual_id]
            )
            individual = Individual.objects.create(
                pedigree=pedigree,
                name=person.individual_id,
                father=person.paternal_id,
                mother=person.maternal_id,
                sex=SEX_MAP[person.sex],
                karyotypic_sex=karyotypic_sex[person.individual_id],
                assay=assay[person.individual_id],
                enrichmentkit=targetbedfile.enrichmentkit,
            )
            for disease in diseases[individual.name]:
                Disease.objects.create(
                    individual=individual,
                    term_id=disease.term.id,
                    term_label=disease.term.label,
                    excluded=bool(disease.excluded),
                )
            for feature in features[individual.name]:
                PhenotypicFeature.objects.create(
                    individual=individual,
                    term_id=feature.type.id,
                    term_label=feature.type.label,
                    excluded=bool(feature.excluded),
                )

        # Update existing individuals.
        for person in family.pedigree.persons:
            if person.individual_id not in keep:
                continue
            targetbedfile = TargetBedFile.objects.get(
                file_uri=targetbedfile_uris[person.individual_id]
            )
            individual = individuals[person.individual_id]
            individual.sex = SEX_MAP[person.sex]
            individual.karyotypic_sex = karyotypic_sex[person.individual_id]
            individual.assay = assay[person.individual_id]
            individual.enrichmentkit = targetbedfile.enrichmentkit
            individual.save()

            if self.caseimportbackgroundjob.caseimportaction.overwrite_terms:
                Disease.objects.filter(individual=individual).delete()
                PhenotypicFeature.objects.filter(individual=individual).delete()
                for disease in diseases[individual.name]:
                    Disease.objects.create(
                        individual=individual,
                        term_id=disease.term.id,
                        term_label=disease.term.label,
                        excluded=bool(disease.excluded),
                    )
                for feature in features[individual.name]:
                    PhenotypicFeature.objects.create(
                        individual=individual,
                        term_id=feature.type.id,
                        term_label=feature.type.label,
                        excluded=bool(feature.excluded),
                    )

    def _clear_files(self, case: Case):
        pedigree = case.pedigree_obj
        internal_files = list(PedigreeInternalFile.objects.filter(pedigree=pedigree))
        external_files = list(PedigreeExternalFile.objects.filter(pedigree=pedigree))
        for individual in pedigree.individual_set.all():
            internal_files += list(IndividualInternalFile.objects.filter(individual=individual))
            external_files += list(IndividualExternalFile.objects.filter(individual=individual))
        self.caseimportbackgroundjob.add_log_entry(
            "Deleting {} internal and {} external file references".format(
                len(internal_files), len(external_files)
            ),
            LOG_LEVEL_INFO,
        )
        for obj in internal_files + external_files:
            obj.delete()

    def _create_external_files(self, case: Case, family: Family):
        self._create_external_files_pedigree(case, case.pedigree_obj, family)
        for individual in case.pedigree_obj.individual_set.all():
            self._create_external_files_individual(case, individual, family)

    def _create_external_files_pedigree(self, case: Case, pedigree: Pedigree, family: Family):
        for file_ in family.files:
            PedigreeExternalFile.objects.create(
                case=case,
                pedigree=pedigree,
                path=file_.uri,
                designation=file_.file_attributes.get(
                    "designation", ExternalFileDesignation.OTHER.value
                ),
                genomebuild=file_.file_attributes.get(
                    "genomebuild", AbstractFile.GENOMEBUILD_OTHER
                ),
                mimetype=file_.file_attributes.get("mimetype", "application/octet-stream"),
                file_attributes={
                    str(key): str(value) for key, value in file_.file_attributes.items()
                },
                identifier_map={
                    str(key): str(value)
                    for key, value in file_.individual_to_file_identifiers.items()
                },
            )

    def _create_external_files_individual(self, case: Case, individual: Individual, family: Family):
        # Fetch appropriate phenopacket from ``family`` for ``individual``.
        if family.proband.id == individual.name:
            pp = family.proband
        else:
            for relative in family.relatives:
                if relative.id == individual.name:
                    pp = relative
                    break
            else:
                raise ValueError(f"Found no phenopacket individual for {individual.name}")

        # Create the external files.
        #
        # NB: the first file for each invidual is skipped as this specifies the kit
        for file_ in list(pp.files)[1:]:
            IndividualExternalFile.objects.create(
                case=case,
                individual=individual,
                path=file_.uri,
                designation=file_.file_attributes.get(
                    "designation", ExternalFileDesignation.OTHER.value
                ),
                genomebuild=file_.file_attributes.get(
                    "genomebuild", AbstractFile.GENOMEBUILD_OTHER
                ),
                mimetype=file_.file_attributes.get("mimetype", "application/octet-stream"),
                file_attributes={
                    str(key): str(value) for key, value in file_.file_attributes.items()
                },
                identifier_map={
                    str(key): str(value)
                    for key, value in file_.individual_to_file_identifiers.items()
                },
            )

    def _run_qc_file_import(self, case: Case):
        """Import QC reports from the external files that are registered for ``case`` already."""
        self.caseimportbackgroundjob.add_log_entry("running qc file import...")

        # perform import of Dragen-style QC files
        dragen_importer = DragenQcImportExecutor(case)
        dragen_importer.run()

        self.caseimportbackgroundjob.add_log_entry("... done with qc file import")

    def _run_seqvars_import(self, case: Case):
        self.caseimportbackgroundjob.add_log_entry("running sequence variant import...")
        SeqvarsImportExecutor(case, bgjob=self.caseimportbackgroundjob).run()
        self.caseimportbackgroundjob.add_log_entry("... done with sequence variant import")
        self.caseimportbackgroundjob.add_log_entry("running structural variant import...")
        StrucvarsImportExecutor(case, bgjob=self.caseimportbackgroundjob).run()
        self.caseimportbackgroundjob.add_log_entry("... done with structural variant import")

    def _run_strucvars_import(self, case: Case):
        self.caseimportbackgroundjob.add_log_entry("strucvars annotation not implemented yet")

    def _update_case_state(self, case):
        case.state = Case.STATE_ACTIVE
        case.save()


def release_from_family(family: Family) -> typing.Optional[str]:
    """Obtain the genome release from the given family (index)'s target file.

    Return ``None`` if the release cannot be determined.
    """
    if (
        family
        and family.proband
        and len(family.proband.files)
        and "genomebuild" in family.proband.files[0].file_attributes
    ):
        val = family.proband.files[0].file_attributes["genomebuild"]
        if val == "GRCh37":
            return AbstractFile.GENOMEBUILD_GRCH37
        elif val == "GRCh38":
            return AbstractFile.GENOMEBUILD_GRCH38
    return None


def build_legacy_pedigree(family: Family) -> typing.List:
    """Build a legacy pedigree from the ``phenopackets.Family``.

    This code will go away once we got rid of the legacy ``pedigree`` member.  We are using
    direct dict access below so we are not robust in phenopackets protobuf updates but that
    should be fair as we will get rid of the legacy ``pedigree`` anyway.
    """
    has_measurements = {
        family.proband.id: bool(len(family.proband.measurements)),
    }
    for relative in family.relatives:
        has_measurements[relative.id] = bool(len(relative.measurements))

    sex_map = {
        phenopackets.Sex.MALE: 1,
        phenopackets.Sex.FEMALE: 2,
        phenopackets.Sex.OTHER_SEX: 0,
        phenopackets.Sex.UNKNOWN_SEX: 0,
    }

    affected_map = {
        2: 2,
        1: 1,
        0: 0,
    }

    result = []
    for person in family.pedigree.persons:
        result.append(
            {
                "sex": sex_map[person.sex],
                "patient": person.individual_id,
                "father": person.paternal_id,
                "mother": person.maternal_id,
                "affected": affected_map[person.affected_status],
                "has_gt_entries": has_measurements[person.individual_id],
            }
        )
    return result

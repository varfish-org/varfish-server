import datetime
import os
import pathlib
import subprocess
import sys
import tempfile
import traceback
import typing

from django.conf import settings
from django.utils import timezone
from google.protobuf.json_format import MessageToJson, Parse
from projectroles.templatetags.projectroles_common_tags import get_app_setting

from cases_files.models import PedigreeInternalFile
from cases_import.models.executors import FileSystemOptions, FileSystemWrapper, uuid_frag
from seqvars.models.base import (
    DataSourceInfoPydantic,
    DataSourceInfosPydantic,
    SeqvarsInhouseDbBuildBackgroundJob,
    SeqvarsQueryExecution,
    SeqvarsQueryExecutionBackgroundJob,
    SeqvarsResultRow,
    SeqvarsResultSet,
)
from seqvars.models.protobufs import (
    outputheader_from_protobuf,
    querysettings_to_protobuf,
    seqvars_output_record_from_protobuf,
)
from seqvars.protos.output_pb2 import OutputHeader, OutputRecord
from variants.models.case import Case


def aws_config_env_internal() -> dict[str, str]:
    """Build AWS config directory fragment for internal storage."""
    return {
        "AWS_ACCESS_KEY_ID": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.access_key,
        "AWS_SECRET_ACCESS_KEY": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.secret_key,
        "AWS_ENDPOINT_URL": (
            f"http://{settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.host}"
            f":{settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.port}"
        ),
        "AWS_REGION": "us-east-1",
    }


def run_worker(*, args: list[str], env: typing.Dict[str, str] | None = None):
    """Run the worker with the given arguments.

    The worker will create a new VCF file and a TBI file.
    """
    cmd = [settings.WORKER_EXE_PATH, *args]
    subprocess.check_call(cmd, env=env)


class SeqvarsQueryExecutionBackgroundJobExecutor:
    """Implementation of ``SeqvarsQueryExecutionBackgroundJob`` execution."""

    def __init__(self, job_pk: int):
        #: Job record primary key.
        self.job_pk = job_pk
        #: The ``SeqvarsQueryExecutionBackgroundJob`` object itself.
        self.bgjob: SeqvarsQueryExecutionBackgroundJob = (
            SeqvarsQueryExecutionBackgroundJob.objects.get(pk=self.job_pk)
        )
        #: The execution.
        self.execution = self.bgjob.seqvarsqueryexecution
        # Shortcut to case.
        self.case = self.bgjob.seqvarsqueryexecution.case
        # Shortcut to storage settings
        storage_settings = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE
        #: The `FileSystemOptions` for the internal storage
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
        #: Base path in internal storage to write files to.
        self.path_internal_base = (
            f"query-results/{uuid_frag(self.case.sodar_uuid)}/seqvars/{self.bgjob.sodar_uuid}"
        )
        #: Path to the results file in internal storage.
        self.path_internal_results = f"{self.path_internal_base}/results.jsonl"

    def run(self):
        """Execute the case import."""
        with self.bgjob.marks():
            self.execution.state = SeqvarsQueryExecution.STATE_RUNNING
            self.execution.start_time = timezone.now()
            self.execution.save()
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    genome_release = self.execute_query(tmpdir)
                self.load_results(genome_release=genome_release)
                self.execution.end_time = timezone.now()
                self.execution.elapsed_seconds = (
                    self.execution.end_time - self.execution.start_time
                ).total_seconds()
                self.execution.state = SeqvarsQueryExecution.STATE_DONE
                self.execution.save()
            except Exception as e:
                print(f"Error while executing worker / importing results: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

                self.execution.end_time = timezone.now()
                self.execution.elapsed_seconds = (
                    self.execution.end_time - self.execution.start_time
                ).total_seconds()
                self.execution.state = SeqvarsQueryExecution.STATE_FAILED
                self.execution.save()

    def execute_query(self, tmpdir: str) -> str:
        """Execute the query, writing it to the internal storage.

        Returns the genome release, one of "grch37" and "grch38".
        """
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        # Obtain ingested VCF internal file object and path.
        seqvars_file = PedigreeInternalFile.objects.filter(
            case=self.case,
            designation="variant_calls/seqvars/ingested-vcf",
        )[0]
        vcf_path_in = seqvars_file.path
        vcf_genome_release = seqvars_file.genomebuild
        # Build query protobuf and conver to JSON.
        case_query = querysettings_to_protobuf(self.bgjob.seqvarsqueryexecution.querysettings)
        case_query_json = MessageToJson(case_query)
        # Write to local file system and also upload to internal storage (S3).
        path_local_query = os.path.join(tmpdir, "query.json")
        with open(path_local_query, "wt") as localf:
            localf.write(case_query_json + "\n")
        path_internal_query = f"{self.path_internal_base}/query.json"
        with self.internal_fs.open(f"s3://{bucket}/{path_internal_query}", "wt") as internalf:
            internalf.write(case_query_json + "\n")
        # Create arguments to use.
        args = [
            "seqvars",
            "query",
            "--case-uuid",
            str(self.case.sodar_uuid),
            "--genome-release",
            vcf_genome_release,
            "--path-db",
            f"{settings.WORKER_DB_PATH}",
            "--path-query-json",
            path_local_query,
            "--path-input",
            f"{bucket}/{vcf_path_in}",
            "--path-output",
            f"{bucket}/{self.path_internal_results}",
        ]
        # Setup environment so the worker can access the internal S3 storage.
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            **aws_config_env_internal(),
        }
        # Actualy execute query execution with worker.
        try:
            run_worker(
                args=args,
                env=env,
            )
        except Exception:
            print("Error while executing worker / importing results", file=sys.stderr)

        return vcf_genome_release

    def load_results(self, *, genome_release: str):
        """Load the results from the internal storage and store in database."""
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        resultset = SeqvarsResultSet(
            queryexecution=self.execution,
            result_row_count=0,
            datasource_infos=None,
            output_header=None,
        )
        with self.internal_fs.open(
            f"s3://{bucket}/{self.path_internal_results}", "rt"
        ) as internalf:
            read_header = False
            for line in internalf:
                if not read_header:
                    read_header = True
                    # Parse out header from first JSONL line, write to result set in
                    # database, extract information, and save result set record.
                    header_pb = Parse(line, OutputHeader())
                    resultset.output_header = outputheader_from_protobuf(header_pb)
                    resultset.result_row_count = header_pb.statistics.count_passed
                    resultset.datasource_infos = DataSourceInfosPydantic(
                        infos=[
                            DataSourceInfoPydantic(name=info.name, version=info.version)
                            for info in header_pb.versions
                        ]
                    )
                    resultset.save()
                else:
                    # Parse out record from JSONL line and write to database.
                    record_pb = Parse(line, OutputRecord())
                    SeqvarsResultRow.objects.create(
                        sodar_uuid=record_pb.uuid,
                        resultset=resultset,
                        genome_release=genome_release,
                        chrom=record_pb.vcf_variant.chrom,
                        chrom_no=record_pb.vcf_variant.chrom_no,
                        pos=record_pb.vcf_variant.pos,
                        ref_allele=record_pb.vcf_variant.ref_allele,
                        alt_allele=record_pb.vcf_variant.alt_allele,
                        payload=seqvars_output_record_from_protobuf(record_pb),
                    )


def run_seqvarsqueryexecutionbackgroundjob(*, pk: int):
    """Execute the work for a ``SeqvarsQueryExecutionBackgroundJob``."""
    executor = SeqvarsQueryExecutionBackgroundJobExecutor(pk)
    executor.run()


class InhouseDbBuildBackgroundJobExecutor:
    """Implementation of ``SeqvarsInhouseDbBuildBackgroundJob`` execution."""

    def __init__(self, job_pk: int):
        #: Job record primary key.
        self.job_pk = job_pk
        #: The ``SeqvarsQueryExecutionBackgroundJob`` object itself.
        self.bgjob: SeqvarsInhouseDbBuildBackgroundJob = (
            SeqvarsInhouseDbBuildBackgroundJob.objects.get(pk=self.job_pk)
        )

    def run(self):
        """Execute building the inhouse database."""
        self.run_for_genome_release(genome_release="grch37")
        self.run_for_genome_release(genome_release="grch38")

    def run_for_genome_release(self, *, genome_release: typing.Literal["grch37", "grch38"]):
        """Execute building the inhouse database for the given genome release."""
        # Ensure the output path is present.
        worker_rw_path = pathlib.Path(settings.WORKER_DB_PATH)
        name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = worker_rw_path / "worker" / "seqvars" / "inhouse" / genome_release / name
        output_path.mkdir(parents=True, exist_ok=True)
        # Prepare the file with paths in S3 for the worker.
        num_cases = self.prepare_paths_for_genome_release(
            genome_release=genome_release, output_path=output_path
        )
        if not num_cases:
            print(f"No cases to process for {genome_release}, skipping inhouse database build.")
            return
        # Create arguments to use.
        args = [
            "seqvars",
            "aggregate",
            "--genomebuild",
            genome_release,
            "--path-out-rocksdb",
            str(output_path / "rocksdb"),
            "--path-input",
            f"@{output_path / 'paths.txt'}",
        ]
        # Setup environment so the worker can access the internal S3 storage.
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            **aws_config_env_internal(),
        }
        # Actualy execute query execution with worker.
        try:
            print(" ".join(args))
            run_worker(
                args=args,
                env=env,
            )
        except Exception:
            print("Error while executing worker / importing results", file=sys.stderr)
            return

        # Atomically update the "active" symlink for the release using Unix `rename(2)`.
        # This will not work on Windows.
        print("Updating symlinks...")
        output_path_with_suffix = output_path.with_suffix(".active")
        print(f"ln -sr {output_path_with_suffix} {output_path}")
        output_path_with_suffix.symlink_to(output_path.relative_to(output_path.parent))
        print(f"rename {output_path_with_suffix} {output_path}")
        output_path_with_suffix.rename(output_path.with_name("active"))

    def prepare_paths_for_genome_release(
        self, *, genome_release: typing.Literal["grch37", "grch38"], output_path: pathlib.Path
    ) -> int:
        """Prepare the paths file for the worker.

        For this, we loop over all V2 cases that have the matching inhouse release.
        """
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        paths = []
        for case in Case.objects.filter(case_version=2).prefetch_related("project").iterator():
            if not get_app_setting("variants", "exclude_from_inhouse_db", project=case.project):
                seqvars_file = PedigreeInternalFile.objects.filter(
                    case=case,
                    designation="variant_calls/seqvars/ingested-vcf",
                )[0]
                if seqvars_file.genomebuild == genome_release:
                    paths.append(f"{bucket}/{seqvars_file.path}")
        paths.sort()

        with open(output_path / "paths.txt", "wt") as f:
            f.write("\n".join(paths) + "\n")

        return len(paths)


def run_seqvarsbuildinhousedbbackgroundjob(*, pk: int):
    """Execute the work for a ``SeqvarsInhouseDbBuildBackgroundJob``."""
    executor = InhouseDbBuildBackgroundJobExecutor(pk)
    executor.run()

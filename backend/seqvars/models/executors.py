import os
import subprocess
import tempfile
import typing

from django.conf import settings
from django.utils import timezone
from google.protobuf.json_format import MessageToJson

from cases_files.models import PedigreeInternalFile
from cases_import.models.executors import FileSystemOptions, FileSystemWrapper, uuid_frag
from seqvars.models.base import SeqvarsQueryExecution, SeqvarsQueryExecutionBackgroundJob
from seqvars.models.protobufs import querysettings_to_protobuf


class CaseImportBackgroundJobExecutor:
    """Implementation of ``CaseImportBackgroundJob`` execution."""

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

    def run(self):
        """Execute the case import."""
        with self.bgjob.marks():
            self.execution.state = SeqvarsQueryExecution.STATE_RUNNING
            self.execution.start_time = timezone.now()
            self.execution.save()
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    self._run(tmpdir)
                self.execution.end_time = timezone.now()
                self.execution.elapsed_seconds = (
                    self.execution.end_time - self.execution.start_time
                ).total_seconds()
                self.execution.state = SeqvarsQueryExecution.STATE_DONE
                self.execution.save()
            except Exception:
                self.execution.end_time = timezone.now()
                self.execution.elapsed_seconds = (
                    self.execution.end_time - self.execution.start_time
                ).total_seconds()
                self.execution.state = SeqvarsQueryExecution.STATE_ERROR
                self.execution.save()

    def _run(self, tmpdir: str):
        """Execute the query."""
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
        path_internal_base = (
            f"{settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket}/query-results/"
            f"{uuid_frag(self.case.sodar_uuid)}/seqvars/{self.bgjob.sodar_uuid}"
        )
        path_internal_query = f"{path_internal_base}/query.json"
        with self.internal_fs.open(f"s3://{path_internal_query}", "wt") as internalf:
            internalf.write(case_query_json + "\n")
        # Path create path of the new file.
        bucket = settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.bucket
        path_internal_results = f"{path_internal_base}/results.jsonl"
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
            f"{bucket}/{path_internal_results}",
        ]
        # Setup environment so the worker can access the internal S3 storage.
        env = {
            **dict(os.environ.items()),
            "LC_ALL": "C",
            "AWS_ACCESS_KEY_ID": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.access_key,
            "AWS_SECRET_ACCESS_KEY": settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.secret_key,
            "AWS_ENDPOINT_URL": (
                f"http://{settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.host}"
                f":{settings.VARFISH_CASE_IMPORT_INTERNAL_STORAGE.port}"
            ),
            "AWS_REGION": "us-east-1",
        }
        # Actualy execute query execution with worker.
        try:
            self.run_worker(
                args=args,
                env=env,
            )
        except Exception:
            pass

    def run_worker(self, *, args: list[str], env: typing.Dict[str, str] | None = None):
        """Run the worker with the given arguments.

        The worker will create a new VCF file and a TBI file.
        """
        cmd = [settings.WORKER_EXE_PATH, *args]
        subprocess.check_call(cmd, env=env)


def run_seqvarsqueryexecutionbackgroundjob(*, pk: int):
    """Execute the work for a ``SeqvarsQueryExecutionBackgroundJob``."""
    executor = CaseImportBackgroundJobExecutor(pk)
    executor.run()

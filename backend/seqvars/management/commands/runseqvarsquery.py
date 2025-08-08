"""Manually (re-)execute a seqvars query (background) job in the foreground."""

import traceback

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from seqvars.models.base import SeqvarsQueryExecution, SeqvarsQueryExecutionBackgroundJob
from seqvars.models.executors import run_seqvarsqueryexecutionbackgroundjob

#: The User model to use.
User = get_user_model()


class Command(BaseCommand):
    #: Help message displayed on the command line.
    help = "Initialize data for a dev environment."

    def add_arguments(self, parser):
        parser.add_argument("id", help="ID or UUID of the job to execute")

    def handle(self, *_args, **options):
        """Entrypoint from command line"""

        try:
            self._handle(options["id"])
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    "A problem occured (see below).\n\n--- BEGIN TRACEBACK ---\n"
                    f"{traceback.format_exc()}--- END TRACEBACK ---\n"
                )
            )
            raise CommandError("Could not initialize the database.") from e

    def _handle(self, job_id: str):
        # Try to find a job with the given ID or UUID
        job = None
        try:
            pk = int(job_id)
            job = SeqvarsQueryExecutionBackgroundJob.objects.get(pk=pk)
        except (ValueError, SeqvarsQueryExecutionBackgroundJob.DoesNotExist):
            try:
                job = SeqvarsQueryExecutionBackgroundJob.objects.get(sodar_uuid=job_id)
            except SeqvarsQueryExecutionBackgroundJob.DoesNotExist:
                pass  # try to find execution below

        if job is None:
            self.stderr.write(
                self.style.SUCCESS(
                    f"Job with ID or UUID {job_id} not found... try to find execution..."
                )
            )
            seqvarsqueryexecution = None
            try:
                pk = int(job_id)
                seqvarsqueryexecution = SeqvarsQueryExecution.objects.get(pk=pk)
            except (ValueError, SeqvarsQueryExecution.DoesNotExist):
                try:
                    seqvarsqueryexecution = SeqvarsQueryExecution.objects.get(sodar_uuid=job_id)
                except SeqvarsQueryExecution.DoesNotExist:
                    raise CommandError(f"Job or execution with ID or UUID {job_id} not found.")
            assert seqvarsqueryexecution is not None
            job = SeqvarsQueryExecutionBackgroundJob.objects.create_full(
                seqvarsqueryexecution=seqvarsqueryexecution,
                user=seqvarsqueryexecution.query.session.user,
            )
            self.stderr.write(
                self.style.SUCCESS(f"... job created with id {job.id} and UUID {job.sodar_uuid}.")
            )
        self.stderr.write(self.style.SUCCESS("Executing seqvars query execution job..."))
        run_seqvarsqueryexecutionbackgroundjob(pk=job.pk)
        self.stderr.write(self.style.SUCCESS("... done executing job"))

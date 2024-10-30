"""Manually (re-)build the seqvars inhouse database."""

import traceback

from django.core.management.base import BaseCommand, CommandError

from seqvars.models.base import SeqvarsInhouseDbBuildBackgroundJob
from seqvars.models.executors import run_seqvarsbuildinhousedbbackgroundjob


class Command(BaseCommand):
    #: Help message displayed on the command line.
    help = "(Re-) build the seqvars inhouse database."

    def handle(self, *_args, **options):
        """Entrypoint from command line"""

        try:
            self._handle()
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    "A problem occured (see below).\n\n--- BEGIN TRACEBACK ---\n"
                    f"{traceback.format_exc()}--- END TRACEBACK ---\n"
                )
            )
            raise CommandError("Could not re-build the seqvars inhouse db.") from e

    def _handle(self):
        # Create a new job to execute.
        job = SeqvarsInhouseDbBuildBackgroundJob.objects.create_full()
        self.stderr.write(self.style.SUCCESS("Executing seqvars inhouse db build job..."))
        run_seqvarsbuildinhousedbbackgroundjob(pk=job.pk)
        self.stderr.write(self.style.SUCCESS("... done executing job"))

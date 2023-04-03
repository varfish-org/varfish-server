"""Django command for clearing expired exported files."""


from django.core.management.base import BaseCommand
from django.db import transaction

from variants.file_export import clear_expired_exported_files
from variants.tasks import clear_expired_exported_files as task_clear_expired_exported_files


class Command(BaseCommand):
    """Implementation of clearing expired exported files."""

    #: Help message displayed on the command line.
    help = "Clear expired exported files."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--async", help="Run the clearing asynchronously.", action="store_false"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""

        if options["async"]:
            clear_expired_exported_files()
            msg = "Done clearing exported files."
        else:
            task_clear_expired_exported_files.delay()
            msg = "Pushed clearing files to background."
        self.stdout.write(self.style.SUCCESS(msg))

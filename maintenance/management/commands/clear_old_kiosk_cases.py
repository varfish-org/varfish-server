"""Django command for clearing old kiosk cases."""

from django.core.management.base import BaseCommand
from django.db import transaction

from variants.models import clear_old_kiosk_cases
from variants.tasks import clear_old_kiosk_cases as task_clear_old_kiosk_cases


class Command(BaseCommand):
    """Implementation of clearing old kiosk cases."""

    #: Help message displayed on the command line.
    help = "Clear old kiosk cases."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--async", help="Run the clearing asynchronously.", action="store_false"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""

        if options["async"]:
            clear_old_kiosk_cases()
            msg = "Done clearing old kiosk cases."
        else:
            task_clear_old_kiosk_cases.delay()
            msg = "Pushed clearing old kiosk cases to background."
        self.stdout.write(self.style.SUCCESS(msg))

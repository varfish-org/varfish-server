"""Django command for clearing inactivate variant sets."""


from django.core.management.base import BaseCommand
from django.db import transaction

from variants.models import cleanup_variant_sets as clear_inactive_variant_sets
from variants.tasks import clear_inactive_variant_sets as task_clear_inactive_variant_sets


class Command(BaseCommand):
    """Implementation of clearing inactive variant sets.
    """

    #: Help message displayed on the command line.
    help = "Clear inactive variant sets."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--async", help="Run the clearing asynchronously.", action="store_false"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""

        if options["async"]:
            clear_inactive_variant_sets()
            msg = "Done clearing inactive variant sets."
        else:
            task_clear_inactive_variant_sets.delay()
            msg = "Pushed clearing inactive variant sets to background."
        self.stdout.write(self.style.SUCCESS(msg))

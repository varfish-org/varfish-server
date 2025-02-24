"""Django command for rebuilding cohort statistics after import."""

from django.core.management.base import BaseCommand
from django.db import transaction

import variants.models as models

from ...tasks import refresh_variants_smallvariantsummary


class Command(BaseCommand):
    """Implementation of rebuilding variant summary."""

    #: Help message displayed on the command line.
    help = "Rebuild the variants summary."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--async", help="Run the rebuild asynchronously.", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""
        if options["async"]:
            refresh_variants_smallvariantsummary.delay()
            msg = "Pushed rebuilding variant summary to background."
        else:
            models.refresh_variants_smallvariantsummary()
            msg = "Done rebuilding variant summary."
        self.stdout.write(self.style.SUCCESS(msg))

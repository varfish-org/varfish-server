"""Django management  for cleaning existing ``BackgroundSvSet`` records."""

from django.conf import settings
from django.core.management import BaseCommand

from svs import tasks


class Command(BaseCommand):
    """Create a cleaning up background sv set records"""

    #: Help message displayed on the command line.
    help = "Cleanup background sv sets (keep 2 latest active)"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--timeout",
            help="Timeout (in hours) to allow in 'building' state, -1 to disable",
            type=int,
            required=False,
            default=settings.SV_CLEANUP_BUILDING_SV_SETS,
        )

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        self.stderr.write("Removing background svs")
        tasks.cleanup_bg_sv_set_task(timeout_hours=options["timeout"])
        self.stderr.write(self.style.SUCCESS("All done, have a nice day!"))

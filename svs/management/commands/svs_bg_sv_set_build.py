"""Django management command for building a new ``BackgroundSv`` record"""

from django.core.management import BaseCommand

from svs import tasks


class Command(BaseCommand):
    """Create a new background sv set"""

    #: Help message displayed on the command line.
    help = "Create a new background sv set"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--chromosome", help="Chromosome to build for", required=False, default=None
        )

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        extra_args = {}
        if options["chromosome"] is not None:
            extra_args["chromosomes"] = [options["chromosome"]]
        tasks.build_bg_sv_set_task(**extra_args)

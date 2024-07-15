"""Django management command for importing a new regulatory map collection."""

from django.core.management.base import BaseCommand

from regmaps.cmds import CollectionImportImpl


class Command(BaseCommand):
    """Implement removal of regulatory map collections"""

    #: Help message displayed on the command line.
    help = "Remove a regulatory map collection"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--path", help="Path to the regulatory map directory or index.yml file", required=True
        )

    def handle(self, *args, **options):
        """Execute the command."""
        return CollectionImportImpl(stderr=self.stderr, style=self.style, **options).run()

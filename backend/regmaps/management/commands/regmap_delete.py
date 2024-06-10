"""Django management command for deleting an existing regulatory map collection."""

from django.core.management.base import BaseCommand

from regmaps.cmds import CollectionDeleteImpl


class Command(BaseCommand):
    """Implement removal of regulatory map collections"""

    #: Help message displayed on the command line.
    help = "Remove a regulatory map collection"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--uuid", help="The UUID of the regulatory map to remove", required=True
        )

    def handle(self, *args, **options):
        """Execute the command."""
        return CollectionDeleteImpl(**options).run()

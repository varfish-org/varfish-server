"""Django management command for listing regulatory map collections."""

from django.core.management.base import BaseCommand

from regmaps.cmds import CollectionListImpl


class Command(BaseCommand):
    """Implement listing of regulatory map collections"""

    #: Help message displayed on the command line.
    help = "List regulatory map collections"

    def handle(self, *args, **options):
        """Execute the command."""
        return CollectionListImpl().run()

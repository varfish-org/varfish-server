"""Django management command for listing ``BackgroundSvSet`` records."""

from django.core.management import BaseCommand
from prettytable import PrettyTable

from svs.models import BackgroundSvSet


class Command(BaseCommand):
    """List all existing ``BackgroundSvSet`` records"""

    #: Help message displayed on the command line.
    help = "List existing background SV sets"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        table = PrettyTable()
        table.field_names = ["id", "UUID", "created", "state"]
        for bg_sv_set in BackgroundSvSet.objects.order_by("date_created"):
            table.add_row(
                [bg_sv_set.pk, bg_sv_set.sodar_uuid, bg_sv_set.date_created, bg_sv_set.state]
            )
        print(table)

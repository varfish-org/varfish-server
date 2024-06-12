"""Django management command for triggering clinvar_export individual update."""

from django.core.management.base import BaseCommand

from clinvar_export.models import refresh_individual_sex_affected


class Command(BaseCommand):
    #: Help message displayed on the command line.
    help = "Refresh ClinVar export individual sex/affected attributes."

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""
        self.stderr.write(self.style.NOTICE("Refreshing all clinvar_xml individuals"))
        refresh_individual_sex_affected()
        self.stderr.write(self.style.NOTICE("All done. Have a nice day!"))

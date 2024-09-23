"""Django command for removing queries with invalid query settings."""

from django.core.management.base import BaseCommand
from django.db import transaction
from jsonschema import Draft7Validator

from variants.models.queries import SmallVariantQuery
from variants.query_schemas import SCHEMA_QUERY, FormToQueryJsonConverter, extend_with_default

DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


class Command(BaseCommand):
    """Implementation of removing invalid query settigns."""

    #: Help message displayed on the command line.
    help = "Remove queries with invalid query settings."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--no-dry-run",
            action="store_true",
            dest="no_dry_run",
            default=False,
            help="Perfom deleting invalid queries.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform removing incompatible queries."""
        no_dry_run = options.get("no_dry_run", False)

        for i in SmallVariantQuery.objects.all():
            query_settings = FormToQueryJsonConverter().convert(i.query_settings)
            try:
                DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(query_settings)
            except Exception as e:
                if options.get("verbosity", False):
                    self.stdout.write(self.style.ERROR(e))
                self.stdout.write(self.style.ERROR(f"Query {i.id} is invalid. Deleting..."))
                if no_dry_run:
                    i.delete()

        if no_dry_run:
            self.stdout.write(self.style.SUCCESS("Incompatible queries have been removed."))
        else:
            self.stdout.write(self.style.SUCCESS("Dry run completed. No queries were deleted."))

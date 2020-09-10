"""Django command for importing a case after annotation with ``varfish-annotator``."""
import json
import gzip

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from importer.management.commands.import_case import CaseImportBase


#: The User model to use.
User = get_user_model()

TMPL_ARG_REQUIRED = "Argument `{}` is required in case #{}"
TMPL_ARG_TYPE = "Argument `{}` must be of type `{}` in case #{}"


def open_file(path, mode):
    """Open gzip or normal file."""
    if path.endswith(".gz"):
        return gzip.open(path, mode)
    else:
        return open(path, mode)


class Command(CaseImportBase, BaseCommand):
    """Implementation of importing a case from pedigree, variants, and genotype file.

    The necessary steps are:

    - Create a new ``Case`` in the appropriate ``Project`` (specified by UUID)
    - Import the variant ``Annotation`` records for the case's variants
    - Import the ``SmallVariant`` call information

    All steps are executed in a transaction, so no stale state is left in the database.
    """

    #: Help message displayed on the command line.
    help = "Import case from PED file and varfish-annotator output. DEPRECATED"

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--json", required=True, help="JSON file with parameters for bulk import of cases"
        )

    def _requirements_check(self, i, **options):
        """Simulate checking of arguments"""

        def _check_argument(arg, typ, required):
            """Check if element is in options if required and check argument type or set default argument type and
            return tuple of transformed name and value."""
            value = options.get(arg, None if required else typ())
            if value is None:
                raise CommandError(TMPL_ARG_REQUIRED.format(arg, i))
            if not isinstance(value, typ):
                raise CommandError(TMPL_ARG_TYPE.format(arg, typ.__name__, i))
            return {arg.replace("-", "_"): value}

        options_ = {}
        # Handle required arguments
        options_.update(_check_argument("case-name", typ=str, required=True))
        options_.update(_check_argument("index-name", typ=str, required=True))
        options_.update(_check_argument("path-ped", typ=str, required=True))
        options_.update(_check_argument("path-genotypes", typ=list, required=True))
        options_.update(_check_argument("path-db-info", typ=list, required=True))
        options_.update(_check_argument("project-uuid", typ=str, required=True))
        # Handle optional arguments
        options_.update(_check_argument("path-bam-qc", typ=list, required=False))
        options_.update(_check_argument("path-feature-effects", typ=list, required=False))
        options_.update(_check_argument("force", typ=bool, required=False))
        options_.update(_check_argument("sync", typ=bool, required=False))
        return options_

    def handle(self, *args, **options):
        """The actual implementation is in ``_handle()``, splitting to get commit times."""

        self.stdout.write(self.style.NOTICE("!!! THIS COMMAND IS MARKED AS DEPCREATED !!!"))
        self.stdout.write(self.style.NOTICE("Please use the varfish-cli instead."))

        with open(options["json"], "r") as jsonfile:
            import_data = json.load(jsonfile)
            for i, case in enumerate(import_data):
                case_options = self._requirements_check(i, **case)
                self._run(*args, **case_options)

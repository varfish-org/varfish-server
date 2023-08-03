"""Django command for generating query result sets."""
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from variants.models import Case
from variants.tasks import create_queryresultset as task_create_queryresultset
from variants.utils import create_queryresultset


class Command(BaseCommand):
    """Implementation of clearing expired exported files."""

    #: Help message displayed on the command line.
    help = "Generate query result set for case."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--async", help="Run the creating asynchronously.", action="store_false"
        )
        parser.add_argument("--case-uuid", help="UUID of the case to create the query set for.")
        parser.add_argument(
            "--project-uuid", help="UUID of the project to create the query set for all cases."
        )
        parser.add_argument("--all", help="Create query set for all cases.", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""
        if bool(options["case_uuid"]) + bool(options["project_uuid"]) + bool(options["all"]) != 1:
            self.stdout.write(self.style.ERROR("Please specify exactly one of the options."))
            return

        if options["case_uuid"]:
            try:
                Case.objects.get(sodar_uuid=options["case_uuid"])
                msg = "Creating query set for case {}.".format(options["case_uuid"])
            except Case.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Case with UUID {options['case_uuid']} not found.")
                )
                return
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(" ".join(e)))
                return
        elif options["project_uuid"]:
            try:
                Project.objects.get(sodar_uuid=options["project_uuid"])
                msg = "Creating query sets for all cases of project {}.".format(
                    options["project_uuid"]
                )
            except Project.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Project with UUID {options['project_uuid']} not found.")
                )
                return
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(" ".join(e)))
                return
        else:
            msg = "Creating query set for all cases."

        self.stdout.write(self.style.NOTICE(msg))
        msg_warning = None

        if options["async"]:
            count, fill_count = create_queryresultset(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Done creating result sets:"
            if (
                count["smallvariantqueryresultset"]
                or count["svqueryresultset"]
                or fill_count["small_variants"]
                or fill_count["structural_variants"]
            ):
                msg += f"""
- SmallVariantQueryResultSets created: {count['smallvariantqueryresultset']}
- SvQueryResultSets created: {count['svqueryresultset']}
- User annotations added to SmallVariantQueryResultSets: {fill_count['small_variants']}
- User annotations added to SvQueryResultSets: {fill_count['structural_variants']}"""
            else:
                msg += "\n- Nothing to do."
            if (
                fill_count["small_variants_orphaned"]
                or fill_count["structural_variants_orphaned"]
                or fill_count["small_variants_no_query_result_set"]
                or fill_count["structural_variants_no_query_result_set"]
                or fill_count["small_variants_no_case_result_set"]
                or fill_count["structural_variants_no_case_result_set"]
            ):
                msg_warning = f"""
WARNING! There are orphaned user annotations or cases or queries without result set:
- Orphaned small variant user annotations: {fill_count['small_variants_orphaned']}
- Small variant queries without result set: {fill_count['small_variants_no_query_result_set']}
- Cases without small variant query result set: {fill_count['small_variants_no_case_result_set']}
- Orphaned structural variant user annotations: {fill_count['structural_variants_orphaned']}
- Structural variant queries without result set: {fill_count['structural_variants_no_query_result_set']}
- Cases without structural variant query result set: {fill_count['structural_variants_no_case_result_set']}""".lstrip()
        else:
            task_create_queryresultset.delay(
                options["case_uuid"], options["project_uuid"], options["all"]
            )
            msg = "Pushed creating the query set to background."

        self.stdout.write(self.style.SUCCESS(msg))
        if msg_warning:
            self.stdout.write(self.style.WARNING(msg_warning))

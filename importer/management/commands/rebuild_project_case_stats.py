"""Django command for rebuilding cohort statistics after import."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from projectroles.plugins import get_backend_api

from variants.helpers import get_engine
from variants.models import CaseAwareProject
from variants.variant_stats import rebuild_case_variant_stats

timeline = get_backend_api("timeline_backend")


#: The User model to use.
User = get_user_model()


class Command(BaseCommand):
    """Implementation of rebuilding project-wide statistics.

    All steps are executed in a transaction, so no stale state is used or left in the database.
    """

    #: Help message displayed on the command line.
    help = "Rebuild all case variant stats within a project."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument(
            "--project-uuid", help="UUID of the project to add the case to", required=True
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""
        try:
            self.stdout.write(
                "Rebuilding statistics as user: {}".format(settings.PROJECTROLES_ADMIN_OWNER)
            )
            admin = User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER)
        except User.DoesNotExist as e:
            raise CommandError(
                "Could not get configured admin user for stats rebuild with username {}".format(
                    settings.PROJECTROLES_ADMIN_OWNER
                )
            ) from e

        project = self._get_project(options["project_uuid"])

        if timeline:
            tl_event = timeline.add_event(
                project=project,
                app_name="variants",
                user=admin,
                event_name="project_case_stats_build",
                description="build project-wide variant statistics",
                status_type="INIT",
            )

        try:
            for case in project.case_set.all():
                self.stdout.write("Rebuilding stats for case: {}".format(case.name))
                rebuild_case_variant_stats(
                    get_engine(), case.latest_variant_set, logger=self.stdout.write
                )
            self.stdout.write(self.style.SUCCESS("Done rebuilding project case stats."))
            if timeline:
                tl_event.set_status("OK", "finished  rebuilding project case stats")
        except Exception as e:
            if timeline:
                tl_event.set_status("FAILED", "could not rebuild project case stats: {}".format(e))
            raise

    def _get_project(self, project_uuid):
        """Get query or raise appropriate exception."""
        try:
            return CaseAwareProject.objects.get(sodar_uuid=project_uuid)
        except ObjectDoesNotExist:
            raise CommandError("Project with UUID {} does not exist".format(project_uuid))

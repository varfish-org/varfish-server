"""Django command for rebuilding cohort statistics after import."""

import aldjemy
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from projectroles.models import Project
from projectroles.plugins import get_backend_api
from variants.variant_stats import rebuild_project_variant_stats

timeline = get_backend_api("timeline_backend")


#: The User model to use.
User = get_user_model()


#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


class Command(BaseCommand):
    """Implementation of rebuilding project-wide statistics.

    All steps are executed in a transaction, so no stale state is used or left in the database.
    """

    #: Help message displayed on the command line.
    help = "Import case from PED file and varfish-annotator output."

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
        rebuild_project_variant_stats(SQLALCHEMY_ENGINE, project, admin)
        self.stdout.write(self.style.SUCCESS("Done rebuilding project-wide stats"))

    def _get_project(self, project_uuid):
        """Get query or raise appropriate exception."""
        try:
            return Project.objects.get(sodar_uuid=project_uuid)
        except ObjectDoesNotExist:
            raise CommandError("Project with UUID {} does not exist".format(project_uuid))

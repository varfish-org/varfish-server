"""Setting in_clinvar field in SmallVariant aligned with Clinvar database."""

from django.core.management.base import BaseCommand
from django.db import transaction
from projectroles.models import Project

from clinvar.models import Clinvar
from variants.models import SmallVariant


def update_in_clinvar_full(case):
    """Update the in_clinvar field in SmallVariant with information from Clinvar database."""
    variants = SmallVariant.objects.filter(case_id=case.id)
    result = {
        "true": 0,
        "false": 0,
        "total": 0,
    }
    for var in variants:
        coords = {
            "release": var.release,
            "chromosome": var.chromosome,
            "start": var.start,
            "end": var.end,
            "reference": var.reference,
            "alternative": var.alternative,
        }
        var.in_clinvar = Clinvar.objects.filter(**coords).exists()
        var.save()
        result["true" if var.in_clinvar else "false"] += 1
        result["total"] += 1
    return result


def update_in_clinvar_light(project, printer=lambda x: None):
    result = 0
    for cv in Clinvar.objects.all():
        coords = {
            "release": cv.release,
            "chromosome": cv.chromosome,
            "start": cv.start,
            "end": cv.end,
            "reference": cv.reference,
            "alternative": cv.alternative,
        }
        for case in project.case_set.all():
            for var in SmallVariant.objects.filter(case_id=case.id, **coords):
                if var.in_clinvar:
                    continue
                var.in_clinvar = True
                var.save()
                result += 1
    return result


@transaction.atomic
def run(*args, **options):
    """Run the command."""

    project = Project.objects.get(sodar_uuid=options["project_uuid"])
    updates = {
        "true": 0,
        "false": 0,
        "total": 0,
    }

    if options["full"]:
        for case in project.case_set.all():
            result = update_in_clinvar_full(case)
            updates["true"] += result["true"]
            updates["false"] += result["false"]
            updates["total"] += result["total"]
    else:
        updates["true"] += update_in_clinvar_light(project)

    return updates


class Command(BaseCommand):
    """Command to set the in_clinvar field in SmallVariant with information from Clinvar database.

    Background: When updating the Clinvar database, the in_clinvar field in SmallVariant
    should be updated to reflect the changes in the Clinvar database.
    """

    #: Help message displayed on the command line.
    help = "Update in_clinvar field in SmallVariant with information from Clinvar database."

    def add_arguments(self, parser):
        """Add the command's argument to the ``parser``."""
        parser.add_argument("--project-uuid", help="Project UUID to apply on")
        parser.add_argument(
            "--full",
            help="Reset ALL variants instead of only variants in Clinvar.",
            action="store_true",
        )
        # parser.add_argument("--all", help="Apply on all projects", action="store_true")

    def handle(self, *args, **options):
        self.stdout.write("Call options:")
        self.stdout.write(f"- {options['project_uuid']=}")
        self.stdout.write(f"- {options['full']=}")
        self.stdout.write(f"Performing ...")

        updates = run(*args, **options)

        self.stdout.write(f"{updates=}")
        self.stdout.write(f"Done.")

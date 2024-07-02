"""Django command for initializing data a development instance.

This Django command prepares a development instance by executing the following steps,
when necessary:

- create the superuser "root" exists
- create a superuser "devadmin" exists
- create a normal user "devuser" exists
- create a root category "DevCategory", owned by devuser
- create a project "DevProject" in the "DevCategory", owned by devuser
- create a Case within the "DevProject" with v2 data
    - note that no actual data will be created

All steps are executed in a transaction, so no stale state is used or left in the database.
"""

import traceback
from typing import Literal, Optional
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from projectroles.models import PROJECT_ROLE_OWNER, Project, Role, RoleAssignment

from cases.models import Individual, Pedigree
from variants.models import Case

#: The User model to use.
User = get_user_model()


class Command(BaseCommand):
    #: Help message displayed on the command line.
    help = "Initialize data for a dev environment."

    def add_arguments(self, parser):
        parser.add_argument(
            "--category-name", help="Name of the category to use.", default="DevCategory"
        )
        parser.add_argument(
            "--project-name", help="Name of the project to use.", default="DevProject"
        )
        parser.add_argument("--case-name", help="Name of the case to use.", default="DevCase")
        parser.add_argument(
            "--reset-password", help="Reset password for users.", action="store_true", default=False
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Entrypoint from command line"""
        _ = args
        category_name = options["category_name"]
        project_name = options["project_name"]
        case_name = options["case_name"]

        try:
            self.stderr.write(
                self.style.SUCCESS(
                    "Rebuilding statistics as user: {}".format(settings.PROJECTROLES_ADMIN_OWNER)
                )
            )
            self._create_user(username="root", is_superuser=True, is_staff=True)
            self._create_user(username="devadmin", is_superuser=True, is_staff=True)
            devuser = self._create_user(username="devuser")
            category = self._create_project(
                title=category_name, owner=devuser, project_type="CATEGORY"
            )
            project = self._create_project(title=project_name, owner=devuser, parent=category)
            self._create_case(name=case_name, project=project)
            self.stderr.write(self.style.SUCCESS(self.style.SUCCESS("All done. Have a nice day!")))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    "A problem occured (see below). Rolling back database.\n\n--- BEGIN TRACEBACK ---\n"
                    f"{traceback.format_exc()}--- END TRACEBACK ---\n"
                )
            )
            raise CommandError("Could not initialize the database.") from e

    def _create_user(
        self,
        *,
        username: str,
        is_superuser: bool = False,
        is_staff: bool = False,
        reset_password: bool = False,
    ):
        """Create a superuser if it does not exist."""
        obj, created = User.objects.get_or_create(
            username=username, defaults={"is_superuser": is_superuser, "is_staff": is_staff}
        )
        if created:
            password = str(uuid4())
            obj.set_password(password)
            self.stderr.write(
                self.style.SUCCESS(f"Created user {username}. Password is '{password}'")
            )
        else:
            if reset_password:
                password = str(uuid4())
                obj.set_password(password)
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Reset password for user {username}. New password is '{password}'"
                    )
                )
            self.stderr.write(self.style.SUCCESS(f"User {username} already exists"))
        return obj

    def _create_project(
        self,
        *,
        title: str,
        owner: User,
        parent: Optional[Project] = None,
        project_type: Literal["PROJECT"] | Literal["CATEGORY"] = "PROJECT",
    ):
        """Create a project / category if it does not exist."""
        project, project_created = Project.objects.get_or_create(
            title=title,
            parent=parent,
            defaults={
                "type": project_type,
            },
        )
        if project_created:
            self.stderr.write(
                self.style.SUCCESS(f"Created project {title} with type {project_type}")
            )
        else:
            self.stderr.write(self.style.SUCCESS(f"Project {title} already exists."))

        if owner:
            owner_role = Role.objects.get(name=PROJECT_ROLE_OWNER)
            _, ra_created = RoleAssignment.objects.get_or_create(
                role=owner_role, project=project, user=owner
            )
            if ra_created:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Assigned owner role for {owner.username} to project {project.title}"
                    )
                )
            else:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"User {owner.username} already has owner role for project {project.title}"
                    )
                )

        return project

    def _create_case(self, *, project: Project, name: str) -> Case:
        """Create a case with pedigree if it does not exist."""
        # Create case unless it exists.
        case, case_created = Case.objects.get_or_create(
            project=project,
            name=name,
            defaults={
                "case_version": 2,
                "state": Case.STATE_ACTIVE,
            },
            pedigree=[
                {
                    "patient": "index",
                    "father": "father",
                    "mother": "mother",
                    "sex": 1,
                    "affected": 2,
                },
                {
                    "patient": "sibling",
                    "father": "father",
                    "mother": "mother",
                    "sex": 2,
                    "affected": 1,
                },
                {"patient": "father", "father": "0", "mother": "0", "sex": 1, "affected": 1},
                {"patient": "mother", "father": "0", "mother": "0", "sex": 2, "affected": 1},
            ],
        )
        if case_created:
            self.stderr.write(self.style.SUCCESS(f"Created case {name}"))
        else:
            self.stderr.write(self.style.SUCCESS(f"Case {name} already exists."))

        # Bail out if the case has the wrong version.
        if case.case_version != 2:
            raise ValueError(
                "Case does not have version 2. Try to create with different --case-name."
            )

        # Create pedigree for case.
        pedigree, ped_created = Pedigree.objects.get_or_create(
            case=case,
        )
        if ped_created:
            self.stderr.write(self.style.SUCCESS(f"Created pedigree for case {name}"))
        else:
            self.stderr.write(self.style.SUCCESS(f"Pedigree for case {name} already exists."))

        # Create individuals in pedigree.
        _, _ = Individual.objects.get_or_create(
            pedigree=pedigree,
            name="index",
            defaults={
                "father": "father",
                "mother": "mother",
                "affected": True,
                "sex": Individual.SEX_MALE,
                "karyotypic_sex": "XY",
                "assay": Individual.ASSAY_WGS,
            },
        )
        _, _ = Individual.objects.get_or_create(
            pedigree=pedigree,
            name="sibling",
            defaults={
                "father": "father",
                "mother": "mother",
                "affected": True,
                "sex": Individual.SEX_FEMALE,
                "karyotypic_sex": "XX",
                "assay": Individual.ASSAY_WGS,
            },
        )
        _, _ = Individual.objects.get_or_create(
            pedigree=pedigree,
            name="father",
            defaults={
                "affected": False,
                "sex": Individual.SEX_FEMALE,
                "karyotypic_sex": "XY",
                "assay": Individual.ASSAY_WGS,
            },
        )
        _, _ = Individual.objects.get_or_create(
            pedigree=pedigree,
            name="mother",
            defaults={
                "affected": False,
                "sex": Individual.SEX_FEMALE,
                "karyotypic_sex": "XX",
                "assay": Individual.ASSAY_WGS,
            },
        )

        return case

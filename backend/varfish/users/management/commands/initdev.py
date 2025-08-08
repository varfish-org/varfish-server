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

import pathlib
import traceback
from typing import Literal, Optional
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.template import Context, Template
from google.protobuf.json_format import ParseDict, ParseError
import phenopackets
from projectroles.app_settings import AppSettingAPI
from projectroles.models import PROJECT_ROLE_OWNER, Project, Role, RoleAssignment
import yaml

from cases.models import Individual, Pedigree
from cases_import import models, tasks
from cases_import.models.base import CaseImportAction, CaseImportBackgroundJob
from seqmeta.models import EnrichmentKit, TargetBedFile
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
        parser.add_argument(
            "--data-release",
            default="grch37",
            choices=["grch37", "grch38"],
            help="Genome release to use when adding data or import job",
        )
        parser.add_argument(
            "--data-case",
            default="Case_1",
            choices=["Case_1", "Case_1_exons"],
            help="Name of case to use when adding data or import job",
        )
        parser.add_argument(
            "--data-import-job",
            action="store_true",
            default=False,
            help="Run import job for case",
        )
        parser.add_argument(
            "--data-create",
            default="disabled",
            choices=["disabled", "job-create", "job-run"],
            help="Run import job for case",
        )

    def handle(self, *args, **options):
        """Entrypoint from command line"""
        _ = args
        category_name = options["category_name"]
        project_name = options["project_name"]
        case_name = options["case_name"]
        data_release = options["data_release"]
        data_case = options["data_case"]
        data_create = options["data_create"]
        reset_password = options["reset_password"]

        job_pk: Optional[int] = None
        with transaction.atomic():
            job_pk = self._handle(
                category_name=category_name,
                project_name=project_name,
                case_name=case_name,
                data_release=data_release,
                data_case=data_case,
                data_create=data_create,
                reset_password=reset_password,
            )
        self.stderr.write(self.style.SUCCESS("-- comitting transaction --"))
        if data_create == "job-create" and job_pk is not None:
            tasks.run_caseimportactionbackgroundjob.delay(caseimportactionbackgroundjob_pk=job_pk)
            self.stderr.write(
                self.style.SUCCESS(f"Launched job (ID={job_pk}). Make sure that celery is running.")
            )
        elif data_create == "job-run" and job_pk is not None:
            self.stderr.write(self.style.SUCCESS("Executing import job..."))
            models.run_caseimportactionbackgroundjob(pk=job_pk)
            self.stderr.write(self.style.SUCCESS("... import job executed successfully."))

    def _handle(
        self,
        *,
        category_name: str,
        project_name: str,
        case_name: str,
        data_release: Literal["grch37", "grch38"],
        data_case: str,
        data_create: Literal["disabled", "job-create", "job-run"],
        reset_password: bool,
    ) -> Optional[int]:
        """Handle the actual initialization, called within ``transaction.atomic()``.

        Returns import job ID if any.
        """
        self.stderr.write(self.style.SUCCESS("Running initialization within transaction..."))
        job_pk: Optional[int] = None
        try:
            self._setup_seqmeta()
            self._create_user(
                username="root", is_superuser=True, is_staff=True, reset_password=reset_password
            )
            self._create_user(
                username="devadmin", is_superuser=True, is_staff=True, reset_password=reset_password
            )
            devuser = self._create_user(username="devuser", reset_password=reset_password)
            category = self._create_project(
                title=category_name, owner=devuser, project_type="CATEGORY"
            )
            project = self._create_project(title=project_name, owner=devuser, parent=category)
            if data_create in ["job-create", "job-run"]:
                job = self._create_import_job(
                    case_name=case_name,
                    project=project,
                    data_release=data_release,
                    data_case=data_case,
                    user=devuser,
                )
                job_pk = job.pk
            else:  # data_create == "disabled"
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

        return job_pk

    def _setup_seqmeta(self):
        """Setup seqmeta configuration."""
        kit, kit_created = EnrichmentKit.objects.get_or_create(
            identifier="all-coding-exons",
            defaults={
                "title": "all coding exons",
            },
        )
        if kit_created:
            self.stderr.write(
                self.style.SUCCESS(
                    f"Created enrichment kit {kit.identifier} with title {kit.title}"
                )
            )
        else:
            self.stderr.write(
                self.style.SUCCESS(f"Enrichment kit {kit.identifier} already exists.")
            )

        for genome_release in ["grch37", "grch38"]:
            bed, bed_created = TargetBedFile.objects.get_or_create(
                file_uri=f"s3://varfish-server/seqmeta/exon-set/{genome_release}/all-coding-exons-1.0.bed.gz",
                genome_release=genome_release,
                enrichmentkit=kit,
            )
            if bed_created:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Created target bed file {bed.file_uri} for {bed.genome_release}"
                    )
                )
            else:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Target bed file {bed.file_uri} for {bed.genome_release} already exists."
                    )
                )

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
            obj.save()
            self.stderr.write(
                self.style.SUCCESS(f"Created user {username}. Password is '{password}'")
            )
        else:
            if reset_password:
                password = str(uuid4())
                obj.set_password(password)
                obj.save()
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

        if project_type == "PROJECT":
            # Ensure the settings are configured as needed.  We use the ``backend/``
            # path as the data path.
            app_settings = AppSettingAPI()
            project_settings = app_settings.get_all(project=project, user=None)
            setting_value = {
                "import_data_protocol": "file",
                "import_data_host": "",
                "import_data_path": str(pathlib.Path(__file__).parent.parent.parent.parent),
                "import_data_port": 0,
                "import_data_user": "",
            }
            for setting_name, value in setting_value.items():
                if project_settings.get(setting_name) != value:
                    app_settings.set(
                        plugin_name="cases_import",
                        setting_name=setting_name,
                        value=value,
                        project=project,
                        user=None,
                    )
                    self.stderr.write(
                        self.style.SUCCESS(
                            f"Set project setting {setting_name} to {value} for {project.title}"
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

    def _create_import_job(
        self, *, project: Project, case_name: str, data_release: str, data_case: str, user: User
    ) -> CaseImportBackgroundJob:
        """
        Create an import job into the given ``project`` using the development
        data with the given ``name``.
        """
        # Check whether the case already exists.
        case_exists = Case.objects.filter(project=project, name=case_name).exists()
        # Read the phenopacket template and replace variables.
        data_path = pathlib.Path(__file__).parent / "data"
        with open(data_path / f"{data_case}.{data_release}.yaml.tpl") as f:
            pp_yaml_tpl_raw = f.read()
            pp_yaml_tpl = Template(template_string=pp_yaml_tpl_raw)
        pp_yaml = pp_yaml_tpl.render(
            Context(
                {
                    "case_name": case_name,
                    "data_case": data_case,
                    "data_path": str(data_path),
                }
            )
        )
        # Parse into YAML, ensure that conversion to phenopackets works.
        payload = yaml.load(pp_yaml, Loader=yaml.SafeLoader)["family"]
        try:
            ParseDict(js_dict=payload, message=phenopackets.Family())
        except ParseError as e:
            raise ValueError("Could not parse phenopacket") from e
        # Create the import action record and case import job.
        job = CaseImportBackgroundJob.objects.create_full(
            caseimportaction=CaseImportAction.objects.create(
                project=project,
                action=(
                    CaseImportAction.ACTION_UPDATE
                    if case_exists
                    else CaseImportAction.ACTION_CREATE
                ),
                payload=payload,
            ),
            user=user,
        )
        self.stderr.write(self.style.SUCCESS("Created import job."))
        return job

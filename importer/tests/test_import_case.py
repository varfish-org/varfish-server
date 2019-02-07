import os
from io import StringIO
from test_plus.test import TestCase

from django.test import RequestFactory
from django.core.management.base import CommandError

from annotation.models import Annotation
from projectroles.models import Project
from variants.models import Case, SmallVariant, AnnotationReleaseInfo

from ..management.commands.import_case import Command

# Set test data path
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data")

# Shared project settings
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


DEFAULT_IMPORT_PARAMETERS = {
    "project_uuid": PROJECT_DICT["sodar_uuid"],
    "case_name": "ISDBM322015",
    "index_name": "ISDBM322015",
    "path_ped": os.path.join(TEST_DATA_PATH, "ISDBM322015.ped"),
    "path_genotypes": os.path.join(TEST_DATA_PATH, "corpasome.gts.tsv"),
    "path_variants": os.path.join(TEST_DATA_PATH, "corpasome.vars.tsv"),
    "path_db_info": os.path.join(TEST_DATA_PATH, "db-info"),
    "update_case": False,
}


class TestCaseImportCase(TestCase):
    """Test import_case manage.py command.
    """

    def setUp(self):
        self.request_factory = RequestFactory()

        # Setup super user
        self.user = self.make_user("admin")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        # Setup command. Call ``handle()`` to execute import. Get output via ``self.import_case.stdout.getvalue()``.
        self.import_case = Command()
        self.import_case.stdout = StringIO()

        # Setup project
        Project.objects.create(**PROJECT_DICT)

    def test_import_valid(self):
        """Import files once and correctly."""
        # Execute import command
        self.import_case.handle(**DEFAULT_IMPORT_PARAMETERS)
        # Check number of imported lines
        self.assertEqual(Annotation.objects.count(), 999)
        case = Case.objects.get(name="ISDBM322015")
        self.assertEqual(case.name, "ISDBM322015")
        for member in case.get_filtered_pedigree_with_samples():
            if member["patient"] == case.name:
                self.assertEqual(member["affected"], 0)
        self.assertEqual(SmallVariant.objects.filter(case_id=case.id).count(), 999)
        self.assertEqual(AnnotationReleaseInfo.objects.filter(case__name="ISDBM322015").count(), 16)

    def test_update_case_valid(self):
        """Import files, then import files again with update flag"""
        # Execute import command
        self.import_case.handle(**DEFAULT_IMPORT_PARAMETERS)
        # Check number of imported lines
        self.assertEqual(Annotation.objects.count(), 999)
        case = Case.objects.get(name="ISDBM322015")
        self.assertEqual(case.name, "ISDBM322015")
        for member in case.get_filtered_pedigree_with_samples():
            if member["patient"] == case.name:
                self.assertEqual(member["affected"], 0)
        self.assertEqual(SmallVariant.objects.filter(case_id=case.id).count(), 999)
        self.assertEqual(AnnotationReleaseInfo.objects.filter(case__name="ISDBM322015").count(), 16)

        # Import same case with updated data.
        updated_parameters = {
            **DEFAULT_IMPORT_PARAMETERS,
            "path_ped": os.path.join(TEST_DATA_PATH, "ISDBM322015.updated.ped"),
            "path_genotypes": os.path.join(TEST_DATA_PATH, "corpasome.gts.updated.tsv"),
            "path_variants": os.path.join(TEST_DATA_PATH, "corpasome.vars.updated.tsv"),
            "path_db_info": os.path.join(TEST_DATA_PATH, "db-info-updated"),
            "update_case": True,
        }

        # Execute import command
        self.import_case.handle(**updated_parameters)
        # Check number of imported lines
        self.assertEqual(Annotation.objects.count(), 999)
        case = Case.objects.get(name="ISDBM322015")
        for member in case.get_filtered_pedigree_with_samples():
            if member["patient"] == case.name:
                self.assertEqual(member["affected"], 1)
        self.assertEqual(case.name, "ISDBM322015")
        self.assertEqual(SmallVariant.objects.filter(case_id=case.id).count(), 499)
        self.assertEqual(AnnotationReleaseInfo.objects.filter(case__name="ISDBM322015").count(), 9)

    def test_update_case_that_doesnt_exist(self):
        """Import files with update flag and not pre-existing import."""
        with self.assertRaisesRegex(CommandError, "^Unable to update case"):
            # Execute import command
            self.import_case.handle(**{**DEFAULT_IMPORT_PARAMETERS, "update_case": True})
            # Check number of imported lines
            self.assertEqual(Annotation.objects.count(), 999)
            case = Case.objects.get(name="ISDBM322015")
            self.assertEqual(case.name, "ISDBM322015")
            self.assertEqual(SmallVariant.objects.filter(case_id=case.id).count(), 999)
            self.assertEqual(
                AnnotationReleaseInfo.objects.filter(case__name="ISDBM322015").count(), 16
            )

    def test_import_already_existing_case(self):
        """Import files twice without update flag the second time."""
        # Execute import command
        self.import_case.handle(**DEFAULT_IMPORT_PARAMETERS)
        # Check number of imported lines
        self.assertEqual(Annotation.objects.count(), 999)
        case = Case.objects.get(name="ISDBM322015")
        self.assertEqual(case.name, "ISDBM322015")
        self.assertEqual(SmallVariant.objects.filter(case_id=case.id).count(), 999)
        self.assertEqual(AnnotationReleaseInfo.objects.filter(case__name="ISDBM322015").count(), 16)

        # Import second time
        with self.assertRaisesRegex(CommandError, "^Case already imported"):
            self.import_case.handle(**DEFAULT_IMPORT_PARAMETERS)

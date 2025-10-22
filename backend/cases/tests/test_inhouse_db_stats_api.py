"""Tests for the InhouseDbStatsApiView."""

from django.urls import reverse
from projectroles.app_settings import AppSettingAPI
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from variants.tests.factories import CaseFactory


class TestInhouseDbStatsApiView(ProjectAPIPermissionTestBase):
    """Tests for InhouseDbStatsApiView."""

    def setUp(self):
        super().setUp()
        self.setting_api = AppSettingAPI()

    def test_unauthenticated(self):
        """Test that unauthenticated users cannot access the endpoint."""
        url = reverse("cases:api-inhouse-db-stats")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_no_cases(self):
        """Test that authenticated users can access the endpoint with no cases."""
        url = reverse("cases:api-inhouse-db-stats")
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"count": 0})

    def test_authenticated_with_cases(self):
        """Test that the endpoint correctly counts individuals from cases."""
        # Create a case with 3 individuals in pedigree
        case1 = CaseFactory(project=self.project)
        case1.pedigree = [
            {
                "patient": "index",
                "father": "father",
                "mother": "mother",
                "sex": 1,
                "affected": 2,
            },
            {
                "patient": "father",
                "father": "0",
                "mother": "0",
                "sex": 1,
                "affected": 1,
            },
            {
                "patient": "mother",
                "father": "0",
                "mother": "0",
                "sex": 2,
                "affected": 1,
            },
        ]
        case1.save()

        # Create another case with 2 individuals
        case2 = CaseFactory(project=self.project)
        case2.pedigree = [
            {
                "patient": "index2",
                "father": "0",
                "mother": "0",
                "sex": 1,
                "affected": 2,
            },
            {
                "patient": "sibling",
                "father": "0",
                "mother": "0",
                "sex": 2,
                "affected": 1,
            },
        ]
        case2.save()

        url = reverse("cases:api-inhouse-db-stats")
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should count all 5 individuals (3 + 2)
        self.assertEqual(response.json(), {"count": 5})

    def test_excludes_cases_from_excluded_projects(self):
        """Test that cases from projects with exclude_from_inhouse_db setting are excluded."""
        # Create a case with 3 individuals in a regular project
        case1 = CaseFactory(project=self.project)
        case1.pedigree = [
            {
                "patient": "index",
                "father": "father",
                "mother": "mother",
                "sex": 1,
                "affected": 2,
            },
            {
                "patient": "father",
                "father": "0",
                "mother": "0",
                "sex": 1,
                "affected": 1,
            },
            {
                "patient": "mother",
                "father": "0",
                "mother": "0",
                "sex": 2,
                "affected": 1,
            },
        ]
        case1.save()

        # Create another project with the exclude setting enabled
        from projectroles.tests.test_models import ProjectMixin

        project_mixin = ProjectMixin()
        category = project_mixin.make_project(title="TestCategory", type="CATEGORY", parent=None)
        excluded_project = project_mixin.make_project(
            title="ExcludedProject", type="PROJECT", parent=category
        )

        # Set the exclude_from_inhouse_db setting
        self.setting_api.set(
            "variants",
            "exclude_from_inhouse_db",
            True,
            project=excluded_project,
        )

        # Create a case in the excluded project with 2 individuals
        case2 = CaseFactory(project=excluded_project)
        case2.pedigree = [
            {
                "patient": "excluded_index",
                "father": "0",
                "mother": "0",
                "sex": 1,
                "affected": 2,
            },
            {
                "patient": "excluded_sibling",
                "father": "0",
                "mother": "0",
                "sex": 2,
                "affected": 1,
            },
        ]
        case2.save()

        url = reverse("cases:api-inhouse-db-stats")
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should only count the 3 individuals from case1, not the 2 from excluded case2
        self.assertEqual(response.json(), {"count": 3})

    def test_different_users_see_same_count(self):
        """Test that all authenticated users see the same global count."""
        # Create a case
        case = CaseFactory(project=self.project)
        case.pedigree = [
            {
                "patient": "index",
                "father": "0",
                "mother": "0",
                "sex": 1,
                "affected": 2,
            }
        ]
        case.save()

        url = reverse("cases:api-inhouse-db-stats")

        # Test with different users
        for user in [
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]:
            with self.login(user):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"count": 1})

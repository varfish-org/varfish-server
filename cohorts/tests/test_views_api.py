from django.urls import reverse

from cohorts.models import Cohort, CohortCase
from cohorts.tests.factories import CohortCaseFactory, CohortFactory
from variants.tests.factories import CaseFactory, ProjectFactory, SmallVariantSetFactory
from variants.tests.helpers import ApiViewTestBase


class CohortSetupMixin:
    def setUp(self):
        super().setUp()

        # Create second project and assign the owner user
        self.project2 = ProjectFactory()
        self._make_assignment(self.project2, self.user_contributor, self.role_contributor)

        # Create first cohort created by contributor in first project
        self.cohort = CohortFactory(project=self.project, user=self.contributor_as.user)
        self.project_cases = CaseFactory.create_batch(5, project=self.project)
        SmallVariantSetFactory(case=self.project_cases[0])
        SmallVariantSetFactory(case=self.project_cases[1])
        SmallVariantSetFactory(case=self.project_cases[2])
        SmallVariantSetFactory(case=self.project_cases[3])
        # Note that there is one case in project1 without SmallVariantSet

        # Create second project and assign cases to cohort from both projects
        self.project2_case = CaseFactory(project=self.project2)
        self.cohortcases = [
            CohortCaseFactory(cohort=self.cohort, case=self.project_cases[0]),
            CohortCaseFactory(cohort=self.cohort, case=self.project2_case),
        ]
        SmallVariantSetFactory(case=self.project2_case)


class TestCohortListCreateApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``CohortListCreateApiView``."""

    def test_list(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(data_json["count"], 1)
        self.assertEqual(len(data_json["results"][0]["cases"]), 2)
        self.assertEqual(data_json["results"][0]["inaccessible_cases"], 0)

    def test_list_inaccessible_cases_as_owner(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.user_owner):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(data_json["count"], 1)
        self.assertEqual(len(data_json["results"][0]["cases"]), 1)
        self.assertEqual(data_json["results"][0]["inaccessible_cases"], 1)

    def test_list_as_creator(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.user_contributor):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(data_json["count"], 1)
        self.assertEqual(len(data_json["results"][0]["cases"]), 2)
        self.assertEqual(data_json["results"][0]["inaccessible_cases"], 0)

    def test_list_multiple_cohorts(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        cohort2 = CohortFactory(project=self.project, user=self.user_owner)
        CohortCaseFactory(cohort=cohort2, case=self.project_cases[3])

        with self.login(self.user_owner):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(data_json["count"], 2)

    def test_create(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        post_data = {
            "name": "TestCohort",
        }

        with self.login(self.superuser):
            response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 201)

        data_json = response.json()
        self.assertEqual(data_json["user"]["username"], self.superuser.username)
        self.assertEqual(data_json["project"], str(self.project.sodar_uuid))
        self.assertEqual(data_json["name"], post_data["name"])
        self.assertEqual(data_json["cases"], [])

        self.assertEqual(Cohort.objects.count(), 2)
        cohort_object = Cohort.objects.get(sodar_uuid=data_json["sodar_uuid"])
        self.assertEqual(cohort_object.user, self.superuser)
        self.assertEqual(cohort_object.name, data_json["name"])
        self.assertEqual(cohort_object.cases.count(), 0)

    def test_create_missing_data(self):
        url = reverse(
            "cohorts:api-cohort-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        post_data = {}

        with self.login(self.superuser):
            response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.exception)

        data_json = response.json()
        self.assertEqual(data_json["name"][0], "This field is required.")


class TestCohortRetrieveUpdateDestroyApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``CohortRetrieveUpdateDestroyApiView``."""

    def test_update(self):
        url = reverse(
            "cohorts:api-cohort-retrieve-update-destroy",
            kwargs={"cohort": self.cohort.sodar_uuid},
        )
        post_data = {
            "name": "TestCohort updated",
        }
        cohort_user = self.cohort.user.username
        cohort_uuid = str(self.cohort.sodar_uuid)

        with self.login(self.superuser):
            response = self.client.put(url, post_data)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(data_json["user"]["username"], cohort_user)
        self.assertEqual(data_json["sodar_uuid"], cohort_uuid)
        self.assertEqual(data_json["name"], post_data["name"])
        self.assertEqual(len(data_json["cases"]), 2)
        self.assertEqual(Cohort.objects.count(), 1)

    def test_update_missing_data(self):
        url = reverse(
            "cohorts:api-cohort-retrieve-update-destroy",
            kwargs={"cohort": self.cohort.sodar_uuid},
        )
        post_data = {}

        with self.login(self.superuser):
            response = self.client.put(url, post_data)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.exception)

        data_json = response.json()
        self.assertEqual(data_json["name"][0], "This field is required.")

    def test_destroy(self):
        url = reverse(
            "cohorts:api-cohort-retrieve-update-destroy",
            kwargs={"cohort": self.cohort.sodar_uuid},
        )

        with self.login(self.superuser):
            response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Cohort.objects.count(), 0)


class TestAccessibleProjectsCasesApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``AccessibleProjectsCasesApiView``."""

    def test_list_as_administrator(self):
        url = reverse(
            "cohorts:api-accessible-projects-cases-list",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(len(data_json), 2)
        self.assertEqual(len(data_json[0]["case_set"]), 4)
        self.assertEqual(len(data_json[1]["case_set"]), 1)
        self.assertEqual(len(self.project_cases), 5)

    def test_list_access_to_both_projects(self):
        url = reverse(
            "cohorts:api-accessible-projects-cases-list",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.user_contributor):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(len(data_json), 2)
        self.assertEqual(len(data_json[0]["case_set"]), 4)
        self.assertEqual(len(data_json[1]["case_set"]), 1)

    def test_list_acccess_to_one_project(self):
        url = reverse(
            "cohorts:api-accessible-projects-cases-list",
            kwargs={"project": self.project.sodar_uuid},
        )

        with self.login(self.user_owner):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data_json = response.json()
        self.assertEqual(len(data_json), 1)
        self.assertEqual(len(data_json[0]["case_set"]), 4)


class TestCohortCaseListApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``CohortCaseListApiView``."""

    def test_list(self):
        url = reverse(
            "cohorts:api-cohortcase-list",
            kwargs={"cohort": self.cohort.sodar_uuid},
        )

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        cohort_cases_uuids = [
            str(cc.sodar_uuid) for cc in CohortCase.objects.filter(cohort=self.cohort)
        ]

        data_json = response.json()
        self.assertEqual(len(data_json), 2)
        self.assertIn(data_json[0]["sodar_uuid"], cohort_cases_uuids)
        self.assertIn(data_json[1]["sodar_uuid"], cohort_cases_uuids)


class TestCohortCaseCreateApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``CohortCaseCreateApiView``."""

    def test_create(self):
        url = reverse(
            "cohorts:api-cohortcase-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        post_data = {
            "case": str(self.project_cases[2].sodar_uuid),
            "cohort": str(self.cohort.sodar_uuid),
        }
        count = CohortCase.objects.count()
        cohort_count = self.cohort.cases.count()

        with self.login(self.superuser):
            response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CohortCase.objects.count(), count + 1)

        data_json = response.json()
        self.assertEqual(data_json["case"], post_data["case"])
        self.assertEqual(data_json["cohort"], post_data["cohort"])

        cohort_case_object = CohortCase.objects.get(sodar_uuid=data_json["sodar_uuid"])
        self.assertEqual(str(cohort_case_object.case.sodar_uuid), post_data["case"])
        self.assertEqual(str(cohort_case_object.cohort.sodar_uuid), post_data["cohort"])
        self.assertEqual(self.cohort.cases.count(), cohort_count + 1)

    def test_create_missing_data(self):
        url = reverse(
            "cohorts:api-cohortcase-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        post_data = {}

        with self.login(self.superuser):
            response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 400)

        data_json = response.json()
        self.assertEqual(data_json["cohort"][0], "This field is required.")
        self.assertEqual(data_json["case"][0], "This field is required.")


class TestCohortCaseDestroyApiView(CohortSetupMixin, ApiViewTestBase):
    """Tests for the ``CohortCaseDestroyApiView``."""

    def test_destroy(self):
        url = reverse(
            "cohorts:api-cohortcase-destroy",
            kwargs={"cohortcase": self.cohortcases[0].sodar_uuid},
        )
        count = CohortCase.objects.count()
        cohort_count = self.cohort.cases.count()

        with self.login(self.superuser):
            response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(CohortCase.objects.count(), count - 1)
        self.assertEqual(self.cohort.cases.count(), cohort_count - 1)

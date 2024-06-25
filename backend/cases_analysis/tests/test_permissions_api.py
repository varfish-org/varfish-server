import json

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from variants.tests.factories import CaseFactory


class TestCaseAnalysisViewSet(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``Case``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases_analysis:api-caseanalysis-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        caseanalysis = CaseAnalysisFactory(case=self.case)
        url = reverse(
            "cases_analysis:api-caseanalysis-detail",
            kwargs={"case": self.case.sodar_uuid, "caseanalysis": caseanalysis.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestCasenalysisSessionViewSet(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``Case``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases_analysis:api-caseanalysissession-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        all_users = good_users + bad_users_401 + bad_users_403

        caseanalysis = CaseAnalysisFactory(case=self.case)
        for user in filter(lambda u: u != None, all_users):
            caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=caseanalysis, user=user)

            url = reverse(
                "cases_analysis:api-caseanalysissession-detail",
                kwargs={"case": self.case.sodar_uuid, "caseanalysissession": caseanalysissession.sodar_uuid},
            )
            if user in good_users:
                self.assert_response(url, [user], 200, method="GET")
            elif user in bad_users_401:
                self.assert_response(url, [user], 401, method="GET")
            elif user in bad_users_403:
                self.assert_response(url, [user], 403, method="GET")

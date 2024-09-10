from django.urls import reverse
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from cases_qc.tests.factories import CaseQcFactory


class TestCaseQcRetrieveApiView(ProjectAPIPermissionTestBase):
    """Permission tests for the API views dealing with ``CaseQc``."""

    def setUp(self):
        super().setUp()
        self.caseqc = CaseQcFactory(case__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "cases_qc:api-caseqc-retrieve",
            kwargs={"case": self.caseqc.case.sodar_uuid},
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


class TestVarfishStatsRetrieveApiView(ProjectAPIPermissionTestBase):
    """Permission tests for the API views dealing with ``VarfishStats``."""

    def setUp(self):
        super().setUp()
        self.caseqc = CaseQcFactory(case__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "cases_qc:api-varfishstats-retrieve",
            kwargs={"case": self.caseqc.case.sodar_uuid},
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

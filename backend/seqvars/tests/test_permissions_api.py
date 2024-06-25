import json

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from variants.models import Case, CaseComments, CasePhenotypeTerms
from variants.tests.factories import CaseCommentsFactory, CaseFactory, CasePhenotypeTermsFactory


class TestSeqvarQueryPresetsSetViewSet(TestProjectAPIPermissionBase):
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

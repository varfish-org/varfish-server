from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.tests.factories import CaseFactory


class TestCaseApiView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``Case``."""

    def test_list(self):
        url = reverse(
            "cases:api-case-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestCaseCommentApiView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``CaseComment``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:api-casecomment-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestCaseGeneAnnotationListApiView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``CaseGeneAnnotation``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:api-casegeneannotation-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

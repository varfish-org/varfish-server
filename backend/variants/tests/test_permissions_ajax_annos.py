from django.urls import reverse
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from variants.tests.factories import CaseFactory


class TestCaseUserAnnotatedVariantsAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse(
            "variants:ajax-smallvariant-userannotatedcase",
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
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

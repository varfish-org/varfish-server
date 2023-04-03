"""Permission tests for the views in ``svs.views.ajax.presets``."""

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.tests.factories import CaseFactory


class TestSvQuerySettingsShortcutAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse("svs:ajax-svquerysettings-shortcut", kwargs={"case": self.case.sodar_uuid})
        good_users = [
            self.superuser,
            self.contributor_as.user,
            self.owner_as.user,
            self.delegate_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

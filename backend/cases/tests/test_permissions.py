from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase


class TestCasesViews(TestProjectPermissionBase):
    """Permission tests for the ``cases`` views"""

    def test_entrypoint(self):
        """Test permissions for the entrypoint view"""
        url = reverse("cases:entrypoint", kwargs={"project": self.project.sodar_uuid})
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, bad_users, 302)

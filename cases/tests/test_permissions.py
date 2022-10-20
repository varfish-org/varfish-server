from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase


class TestCasesViews(TestProjectPermissionBase):
    """Permission tests for the ``cases`` views"""

    def test_entrypoint(self):
        """Test permissions for the entrypoint view"""
        url = reverse("cases:entrypoint", kwargs={"project": self.project.sodar_uuid})
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, bad_users, 302)

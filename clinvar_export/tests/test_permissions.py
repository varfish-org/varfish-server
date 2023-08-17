from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase


class TestClinvarExportViews(TestProjectPermissionBase):
    """Permission tests for the ``clinvar_export`` views"""

    def test_entrypoint(self):
        """Test permissions for the entrypoint view"""
        url = reverse("clinvar_export:entrypoint", kwargs={"project": self.project.sodar_uuid})
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, bad_users, 302)

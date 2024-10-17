from django.urls import reverse
from projectroles.tests.test_permissions import ProjectPermissionTestBase

from varannos.tests.factories import VarAnnoSetFactory


class TestVarAnnoSetViews(ProjectPermissionTestBase):
    """Permission tests for the ``VarAnnoSet`` views"""

    def setUp(self):
        super().setUp()
        self.varannoset = VarAnnoSetFactory(project=self.project)

    def test_list(self):
        """Test permissions for the list view"""
        url = reverse("varannos:varannoset-list", kwargs={"project": self.project.sodar_uuid})
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

    def test_detail(self):
        """Test permissions for the detail view"""
        url = reverse(
            "varannos:varannoset-detail", kwargs={"varannoset": self.varannoset.sodar_uuid}
        )
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

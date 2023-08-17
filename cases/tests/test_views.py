from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase


class TestCasesViews(TestProjectPermissionBase):
    """Tests for the ``cases`` views"""

    def test_entrypoint(self):
        """Test permissions for the entrypoint view"""
        url = reverse("cases:entrypoint", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.user_contributor):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertInHTML('<div id="app" class="h-100">', response.content.decode("utf-8"))

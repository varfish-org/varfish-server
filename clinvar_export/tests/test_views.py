from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase


class TestClinvarExportViews(TestProjectPermissionBase):
    """Tests for the ``clinvar_export`` views"""

    def test_entrypoint(self):
        """Test permissions for the entrypoint view"""
        url = reverse("clinvar_export:entrypoint", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertInHTML('<div id="app">', response.content.decode("utf-8"))

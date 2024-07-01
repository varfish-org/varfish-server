from django.urls import reverse

from variants.tests.factories import ProjectFactory
from variants.tests.helpers import ApiViewTestBase
from vf_settings.tests.factories import (
    PROJECT_SETTINGS_A,
    PROJECT_USER_SETTINGS_A,
    SITE_SETTINGS_A,
    USER_SETTINGS_A,
)


class TestSiteSettingsRetrieveUpdateAPIView(ApiViewTestBase):
    """Tests for the SiteSettingsRetrieveUpdateAPIView view class."""

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-site-settings-retrieve-update",
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_reset(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-site-settings-retrieve-update",
                )
                + "?a=reset",
            )
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "vf_settings:api-site-settings-retrieve-update",
                ),
                data=SITE_SETTINGS_A,
            )
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "vf_settings:api-site-settings-retrieve-update",
                ),
                data={},
            )
        self.assertEqual(response.status_code, 200)


class TestProjectSettingsRetrieveUpdateAPIView(ApiViewTestBase):
    """Tests for the ProjectSettingsRetrieveUpdateAPIView view class."""

    def setUp(self):
        self.project = ProjectFactory()
        return super().setUp()

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-project-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_reset(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-project-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                )
                + "?a=reset",
            )
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "vf_settings:api-project-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data=PROJECT_SETTINGS_A,
            )
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "vf_settings:api-project-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={},
            )
        self.assertEqual(response.status_code, 200)


class TestProjectUserSettingsRetrieveUpdateAPIView(ApiViewTestBase):
    """Tests for the ProjectUserSettingsRetrieveUpdateAPIView view class."""

    def setUp(self):
        self.project = ProjectFactory()
        return super().setUp()

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-project-user-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_reset(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-project-user-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                )
                + "?a=reset",
            )
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "vf_settings:api-project-user-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data=PROJECT_USER_SETTINGS_A,
            )
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "vf_settings:api-project-user-settings-retrieve-update",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={},
            )
        self.assertEqual(response.status_code, 200)


class TestUserSettingsRetrieveUpdateAPIView(ApiViewTestBase):
    """Tests for the UserSettingsRetrieveUpdateAPIView view class."""

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-user-settings-retrieve-update",
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_reset(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-user-settings-retrieve-update",
                )
                + "?a=reset",
            )
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "vf_settings:api-user-settings-retrieve-update",
                ),
                data=USER_SETTINGS_A,
            )
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "vf_settings:api-user-settings-retrieve-update",
                ),
                data={},
            )
        self.assertEqual(response.status_code, 200)


class AllSettingsRetrieveAPIView(ApiViewTestBase):
    """Tests for the AllSettingsRetrieveAPIView view class."""

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-all-settings-retrieve",
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_with_project(self):
        project = ProjectFactory()
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "vf_settings:api-all-project-settings-retrieve",
                    kwargs={"project": project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

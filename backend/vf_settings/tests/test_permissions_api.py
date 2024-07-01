from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from vf_settings.tests.factories import (
    PROJECT_SETTINGS_A,
    PROJECT_USER_SETTINGS_A,
    SITE_SETTINGS_A,
    USER_SETTINGS_A,
)


class SiteSettingsRetrieveUpdateAPIView(TestProjectAPIPermissionBase):
    """Tests for the site settings API view."""

    def test_site_settings_get(self):
        url = reverse("vf_settings:api-site-settings-retrieve-update")
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, [self.anonymous], 401)

    def test_site_settings_get_reset(self):
        url = reverse("vf_settings:api-site-settings-retrieve-update") + "?a=reset"
        good_users = [
            self.superuser,
        ]
        forbidden_users = [
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

    def test_site_settings_put(self):
        url = reverse("vf_settings:api-site-settings-retrieve-update")
        good_users = [
            self.superuser,
        ]
        forbidden_users = [
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PUT", data=SITE_SETTINGS_A)
        self.assert_response(url, forbidden_users, 403, method="PUT")
        self.assert_response(url, [self.anonymous], 401, method="PUT")

    def test_site_settings_patch(self):
        url = reverse("vf_settings:api-site-settings-retrieve-update")
        good_users = [
            self.superuser,
        ]
        forbidden_users = [
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, forbidden_users, 403, method="PATCH")
        self.assert_response(url, [self.anonymous], 401, method="PATCH")


class ProjectSettingsRetrieveUpdateAPIView(TestProjectAPIPermissionBase):
    """Tests for the project settings API view."""

    def test_project_settings_get(self):
        url = reverse(
            "vf_settings:api-project-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

    def test_project_settings_get_reset(self):
        url = (
            reverse(
                "vf_settings:api-project-settings-retrieve-update",
                kwargs={"project": self.project.sodar_uuid},
            )
            + "?a=reset"
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
        ]
        forbidden_users = [
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

    def test_project_settings_put(self):
        url = reverse(
            "vf_settings:api-project-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
        ]
        forbidden_users = [
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(
            url,
            good_users,
            200,
            method="PUT",
            data=PROJECT_SETTINGS_A,
        )
        self.assert_response(url, forbidden_users, 403, method="PUT")
        self.assert_response(url, [self.anonymous], 401, method="PUT")

    def test_project_settings_patch(self):
        url = reverse(
            "vf_settings:api-project-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
        ]
        forbidden_users = [
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, forbidden_users, 403, method="PATCH")
        self.assert_response(url, [self.anonymous], 401, method="PATCH")


class ProjectUserSettingsRetrieveUpdateAPIView(TestProjectAPIPermissionBase):
    """Tests for the project user settings API view."""

    def test_project_user_settings_get(self):
        url = reverse(
            "vf_settings:api-project-user-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

    def test_project_user_settings_get_reset(self):
        url = (
            reverse(
                "vf_settings:api-project-user-settings-retrieve-update",
                kwargs={"project": self.project.sodar_uuid},
            )
            + "?a=reset"
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

    def test_project_user_settings_put(self):
        url = reverse(
            "vf_settings:api-project-user-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PUT", data=PROJECT_USER_SETTINGS_A)
        self.assert_response(url, forbidden_users, 403, method="PUT")
        self.assert_response(url, [self.anonymous], 401, method="PUT")

    def test_project_user_settings_patch(self):
        url = reverse(
            "vf_settings:api-project-user-settings-retrieve-update",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, forbidden_users, 403, method="PATCH")
        self.assert_response(url, [self.anonymous], 401, method="PATCH")


class UserSettingsRetrieveUpdateAPIView(TestProjectAPIPermissionBase):
    """Tests for the user settings API view."""

    def test_user_settings_get(self):
        url = reverse(
            "vf_settings:api-user-settings-retrieve-update",
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, [self.anonymous], 401)

    def test_user_settings_get_reset(self):
        url = (
            reverse(
                "vf_settings:api-user-settings-retrieve-update",
            )
            + "?a=reset"
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, [self.anonymous], 401)

    def test_user_settings_put(self):
        url = reverse(
            "vf_settings:api-user-settings-retrieve-update",
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(
            url,
            good_users,
            200,
            method="PUT",
            data=USER_SETTINGS_A,
        )
        self.assert_response(
            url,
            [self.anonymous],
            401,
            method="PUT",
        )

    def test_user_settings_patch(self):
        url = reverse(
            "vf_settings:api-user-settings-retrieve-update",
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, [self.anonymous], 401, method="PATCH")


class AllSettingsRetrieveAPIView(TestProjectAPIPermissionBase):
    """Tests for the all settings API view."""

    def test_all_settings_get(self):
        url = reverse("vf_settings:api-all-settings-retrieve")
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, [self.anonymous], 401)

    def test_all_settings_with_project(self):
        url = reverse(
            "vf_settings:api-all-project-settings-retrieve",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        forbidden_users = [
            self.user_no_roles,
            self.user_finder_cat,
        ]
        self.assert_response(url, good_users, 200)
        self.assert_response(url, forbidden_users, 403)
        self.assert_response(url, [self.anonymous], 401)

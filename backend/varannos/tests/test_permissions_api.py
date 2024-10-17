from django.urls import reverse
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from varannos.models import VarAnnoSet
from varannos.tests.factories import VarAnnoSetFactory


class TestVarAnnoSetApiView(ProjectAPIPermissionTestBase):
    """Permission tests for the API views dealing with ``VarAnnoSet``."""

    def setUp(self):
        super().setUp()
        self.varannoset = VarAnnoSetFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "varannos:api-varannoset-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [
            self.user_no_roles,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        data = {
            "title": "Set Title",
            "release": "GRCh37",
            "fields": ["pathogenicity", "notes"],
        }

        def cleanup_create():
            VarAnnoSet.objects.all().delete()

        url = reverse(
            "varannos:api-varannoset-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [
            self.user_no_roles,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        self.assert_response(
            url, good_users, 201, method="POST", data=data, cleanup_method=cleanup_create
        )
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup_create
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup_create
        )

    def test_retrieve(self):
        url = reverse(
            "varannos:api-varannoset-retrieveupdatedestroy",
            kwargs={"varannoset": self.varannoset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [
            self.user_no_roles,
        ]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        data = {
            "title": "New Title",
            "release": "GRCh37",
            "fields": ["pathogenicity", "notes"],
        }

        url = reverse(
            "varannos:api-varannoset-retrieveupdatedestroy",
            kwargs={"varannoset": self.varannoset.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [
            self.user_no_roles,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        self.assert_response(
            url,
            good_users,
            200,
            method="PUT",
            data=data,
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="PUT",
            data=data,
        )
        self.assert_response(
            url,
            bad_users_403,
            403,
            method="PUT",
            data=data,
        )

    def test_destroy(self):
        url = reverse(
            "varannos:api-varannoset-retrieveupdatedestroy",
            kwargs={"varannoset": self.varannoset.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_404 = [
            self.user_no_roles,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        self.assert_response(
            url,
            good_users,
            204,
            method="DELETE",
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="DELETE",
        )
        self.assert_response(
            url,
            bad_users_404,
            404,
            method="DELETE",
        )

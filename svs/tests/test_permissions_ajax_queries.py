"""Permission tests for the views in ``svs.views.ajax.queries``."""

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from svs.models import SvQuery
from svs.tests.factories import SvQueryFactory, SvQueryResultSetFactory
from variants.tests.factories import CaseFactory


class TestSvQueryListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_post(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        data = {"query_settings": "{}"}
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestSvQueryRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svquery = SvQueryFactory(case=self.case)

    def test_get(self):
        url = reverse(
            "svs:ajax-svquery-retrieveupdatedestroy", kwargs={"svquery": self.svquery.sodar_uuid}
        )
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

    def test_patch(self):
        url = reverse(
            "svs:ajax-svquery-retrieveupdatedestroy", kwargs={"svquery": self.svquery.sodar_uuid}
        )
        data = {}
        good_users = [
            self.superuser,
            self.contributor_as.user,
            self.owner_as.user,
            self.delegate_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.guest_as.user]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):
        svquery_uuid = self.svquery.sodar_uuid

        def cleanup():
            """Re-create self.casephenotypetermss with the correct UUID if necessary."""
            if not SvQuery.objects.filter(sodar_uuid=svquery_uuid):
                self.svquery = SvQueryFactory(sodar_uuid=svquery_uuid, case=self.case)

        kwargs = {"svquery": self.svquery.sodar_uuid}
        url = reverse("svs:ajax-svquery-retrieveupdatedestroy", kwargs=kwargs)
        good_users = [
            self.contributor_as.user,
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.guest_as.user]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSvQueryResultSetListAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svqueryresultset = SvQueryResultSetFactory(svquery__case=self.case)
        self.svquery = self.svqueryresultset.svquery

    def test_get(self):
        url = reverse("svs:ajax-svqueryresultset-list", kwargs={"svquery": self.svquery.sodar_uuid})
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


class TestSvQueryResultSetRetrieveAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svqueryresultset = SvQueryResultSetFactory(svquery__case=self.case)
        self.svquery = self.svqueryresultset.svquery

    def test_get(self):
        url = reverse(
            "svs:ajax-svqueryresultset-retrieve",
            kwargs={"svqueryresultset": self.svqueryresultset.sodar_uuid},
        )
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


class TestSvQueryResultRowListAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svqueryresultset = SvQueryResultSetFactory(svquery__case=self.case)
        self.svquery = self.svqueryresultset.svquery

    def test_get(self):
        url = reverse(
            "svs:ajax-svqueryresultrow-list",
            kwargs={"svqueryresultset": self.svqueryresultset.sodar_uuid},
        )
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

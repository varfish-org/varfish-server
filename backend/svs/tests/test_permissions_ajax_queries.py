"""Permission tests for the views in ``svs.views.ajax.queries``."""

from django.urls import reverse
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from svs.models import SvQuery
from svs.tests.factories import SvQueryFactory, SvQueryResultRowFactory, SvQueryResultSetFactory
from variants.tests.factories import CaseFactory


class TestSvQueryListCreateAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_post(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        data = {"query_settings": "{}"}
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestSvQueryRetrieveUpdateDestroyAjaxView(ProjectAPIPermissionTestBase):
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
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
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
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]
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
            self.user_contributor,
            self.superuser,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSvQueryResultSetListAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svqueryresultset = SvQueryResultSetFactory(svquery__case=self.case)
        self.svquery = self.svqueryresultset.svquery

    def test_get(self):
        url = reverse("svs:ajax-svqueryresultset-list", kwargs={"svquery": self.svquery.sodar_uuid})
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSvQueryResultSetRetrieveAjaxView(ProjectAPIPermissionTestBase):
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
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSvQueryResultRowListAjaxView(ProjectAPIPermissionTestBase):
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
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSvQueryResultRowRetrieveView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.svqueryresultrow = SvQueryResultRowFactory(svqueryresultset__svquery__case=self.case)

    def test_get(self):
        url = reverse(
            "svs:ajax-svqueryresultrow-retrieve",
            kwargs={"svqueryresultrow": self.svqueryresultrow.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

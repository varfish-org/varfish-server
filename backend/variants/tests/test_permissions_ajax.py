"""Permission tests for the views in ``variants.views.api.queries``."""

import json

from django.urls import reverse
from projectroles.tests.test_permissions_api import ProjectAPIPermissionTestBase

from variants.models import SmallVariantQuery
from variants.tests.factories import (
    CaseFactory,
    SmallVariantQueryFactory,
    SmallVariantQueryResultSetFactory,
    SmallVariantSetFactory,
)

# TODO: Using permission class `SessionAuthentication` returns wrong status code for unauthenticated user (= no user)
#  expected: 401, got: 403


class TestSmallVariantQueryListCreateAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        SmallVariantSetFactory(case=self.case)

    def test_get(self):
        url = reverse("variants:ajax-query-list-create", kwargs={"case": self.case.sodar_uuid})
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        # self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_post(self):
        url = reverse("variants:ajax-query-list-create", kwargs={"case": self.case.sodar_uuid})
        data = {
            "query_settings": json.dumps(
                {"effects": [], "quality": {self.case.pedigree[0]["patient"]: {}}, "genotype": {}}
            )
        }
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 201, method="POST", data=data)
        # self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestSmallVariantQueryRetrieveUpdateDestroyAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.query = SmallVariantQueryFactory(case=self.case)

    def test_get(self):
        url = reverse(
            "variants:ajax-query-retrieve-update-destroy",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        # self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "variants:ajax-query-retrieve-update-destroy",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
        )
        data = {}
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_guest, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        # self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):
        query_uuid = self.query.sodar_uuid

        def cleanup():
            """Re-create self.casephenotypetermss with the correct UUID if necessary."""
            if not SmallVariantQuery.objects.filter(sodar_uuid=query_uuid):
                self.query = SmallVariantQueryFactory(sodar_uuid=query_uuid, case=self.case)

        kwargs = {"smallvariantquery": self.query.sodar_uuid}
        url = reverse("variants:ajax-query-retrieve-update-destroy", kwargs=kwargs)
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_guest, self.user_finder_cat]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        # self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSmallVariantQueryResultSetListAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:ajax-query-result-set-list",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        # self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSmallVariantQueryResultSetRetrieveAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:ajax-query-result-set-retrieve",
            kwargs={"smallvariantqueryresultset": self.smallvariantqueryresultset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        # self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSmallVariantQueryResultRowListAjaxView(ProjectAPIPermissionTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:ajax-query-result-row-list",
            kwargs={"smallvariantqueryresultset": self.smallvariantqueryresultset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.owner_as.user,
            self.user_delegate,
            self.user_guest,
        ]
        # bad_users_401 = [self.anonymous]
        bad_users_403 = [self.anonymous, self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        # self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

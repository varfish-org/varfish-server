"""Permission tests for the views in ``variants.views.api.queries``."""
import json

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.models import SmallVariantQuery
from variants.tests.factories import (
    CaseFactory,
    SmallVariantQueryFactory,
    SmallVariantQueryResultSetFactory,
)


class TestSmallVariantQueryListCreateApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse("variants:api-query-list-create", kwargs={"case": self.case.sodar_uuid})
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
        url = reverse("variants:api-query-list-create", kwargs={"case": self.case.sodar_uuid})
        data = {
            "query_settings": json.dumps(
                {"effects": [], "quality": {self.case.pedigree[0]["patient"]: {}}, "genotype": {}}
            )
        }
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


class TestSmallVariantQueryRetrieveUpdateDestroyApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.query = SmallVariantQueryFactory(case=self.case)

    def test_get(self):
        url = reverse(
            "variants:api-query-retrieve-update-destroy",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
        )
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

    def test_patch(self):
        url = reverse(
            "variants:api-query-retrieve-update-destroy",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
        )
        data = {}
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.guest_as.user]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):
        query_uuid = self.query.sodar_uuid

        def cleanup():
            """Re-create self.casephenotypetermss with the correct UUID if necessary."""
            if not SmallVariantQuery.objects.filter(sodar_uuid=query_uuid):
                self.query = SmallVariantQueryFactory(sodar_uuid=query_uuid, case=self.case)

        kwargs = {"smallvariantquery": self.query.sodar_uuid}
        url = reverse("variants:api-query-retrieve-update-destroy", kwargs=kwargs)
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.guest_as.user]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSmallVariantQueryResultSetListApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:api-query-result-set-list",
            kwargs={"smallvariantquery": self.query.sodar_uuid},
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


class TestSmallVariantQueryResultSetRetrieveApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:api-query-result-set-retrieve",
            kwargs={"smallvariantqueryresultset": self.smallvariantqueryresultset.sodar_uuid},
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


class TestSmallVariantQueryResultRowListApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            smallvariantquery__case=self.case
        )
        self.query = self.smallvariantqueryresultset.smallvariantquery

    def test_get(self):
        url = reverse(
            "variants:api-query-result-row-list",
            kwargs={"smallvariantqueryresultset": self.smallvariantqueryresultset.sodar_uuid},
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

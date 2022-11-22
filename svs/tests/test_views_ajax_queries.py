"""Tests for the module ``svs.views.ajax.queries``."""

import json
import re

from django.urls import reverse
import jsonmatch

from svs.models import SvQuery
from svs.tests.factories import SvQueryFactory, SvQueryResultSetFactory
from variants.tests.factories import CaseWithVariantSetFactory
from variants.tests.helpers import ApiViewTestBase

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestSvQueryListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, _, self.structural_variant_set = CaseWithVariantSetFactory.get("structural")
        self.svquery = SvQueryFactory(case=self.case)

    def test_get(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.case.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "query_settings": {},
                "query_state": "initial",
                "query_state_msg": None,
                "sodar_uuid": RE_UUID4,
            }
        )
        self.assertEqual(len(res_json), 1)
        expected.assert_matches(res_json[0])

    def test_get_querylimit(self):
        for _ in range(100):
            SvQueryFactory(case=self.case)

        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        with self.login(self.superuser):
            # Empirically determined value of "12" below on 2022-12-06.
            with self.assertNumQueriesLessThan(12):
                response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        url = reverse("svs:ajax-svquery-listcreate", kwargs={"case": self.case.sodar_uuid})
        data = {"query_settings": json.dumps({"fake": "query"})}

        self.assertEqual(SvQuery.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(url, data=data)
        res_json = response.json()
        self.assertEqual(SvQuery.objects.count(), 2)
        self.assertEqual(response.status_code, 201)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "user": str(self.superuser.sodar_uuid),
                "case": str(self.case.sodar_uuid),
                "query_state": "initial",
                "query_state_msg": None,
                "query_settings": {"fake": "query"},
            }
        )
        expected.assert_matches(res_json)


class TestSvQueryRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, _, self.structural_variant_set = CaseWithVariantSetFactory.get("structural")
        self.svquery = SvQueryFactory(case=self.case)

    def test_get(self):
        url = reverse(
            "svs:ajax-svquery-retrieveupdatedestroy", kwargs={"svquery": self.svquery.sodar_uuid}
        )
        with self.login(self.superuser):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.svquery.sodar_uuid),
                "date_created": self.svquery.date_created.strftime(TIMEF),
                "date_modified": self.svquery.date_modified.strftime(TIMEF),
                "case": str(self.case.sodar_uuid),
                "query_settings": {},
                "query_state": "initial",
                "query_state_msg": None,
                "logs": [],
            }
        )
        expected.assert_matches(res_json)

    def test_patch(self):
        url = reverse(
            "svs:ajax-svquery-retrieveupdatedestroy", kwargs={"svquery": self.svquery.sodar_uuid}
        )
        data = {"query_state_msg": "will be ignored"}
        with self.login(self.superuser):
            response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.svquery.sodar_uuid),
                "date_created": self.svquery.date_created.strftime(TIMEF),
                "date_modified": self.svquery.date_modified.strftime(TIMEF),
                "case": str(self.case.sodar_uuid),
                "query_settings": {},
                "query_state": "initial",
                "query_state_msg": None,
                "logs": [],
            }
        )
        expected.assert_matches(res_json)

    def test_delete(self):
        self.assertEquals(SvQuery.objects.count(), 1)
        url = reverse(
            "svs:ajax-svquery-retrieveupdatedestroy", kwargs={"svquery": self.svquery.sodar_uuid}
        )
        with self.login(self.superuser):
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEquals(SvQuery.objects.count(), 0)


class TestTestSvQueryResultSetListAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, _, self.structural_variant_set = CaseWithVariantSetFactory.get("structural")
        self.svquery = SvQueryFactory(case=self.case)
        self.svqueryresult = SvQueryResultSetFactory(svquery=self.svquery)

    def test_get(self):
        url = reverse("svs:ajax-svqueryresultset-list", kwargs={"svquery": self.svquery.sodar_uuid})

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "date_created": self.svqueryresult.date_created.strftime(TIMEF),
                "date_modified": self.svqueryresult.date_modified.strftime(TIMEF),
                "elapsed_seconds": 3600.0,
                "end_time": self.svqueryresult.end_time.strftime(TIMEF),
                "sodar_uuid": str(self.svqueryresult.sodar_uuid),
                "start_time": self.svqueryresult.start_time.strftime(TIMEF),
                "result_row_count": 0,
                "svquery": str(self.svquery.sodar_uuid),
            }
        )
        self.assertEqual(len(res_json), 1)
        expected.assert_matches(res_json[0])


class TestSvQueryResultRetrieveAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, _, self.structural_variant_set = CaseWithVariantSetFactory.get("structural")
        self.svquery = SvQueryFactory(case=self.case)
        self.svqueryresult = SvQueryResultSetFactory(svquery=self.svquery)

    def test_get(self):
        url = reverse(
            "svs:ajax-svqueryresultset-retrieve",
            kwargs={"svqueryresultset": self.svqueryresult.sodar_uuid},
        )

        with self.login(self.superuser):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "date_created": self.svqueryresult.date_created.strftime(TIMEF),
                "date_modified": self.svqueryresult.date_modified.strftime(TIMEF),
                "elapsed_seconds": 3600.0,
                "end_time": self.svqueryresult.end_time.strftime(TIMEF),
                "sodar_uuid": str(self.svqueryresult.sodar_uuid),
                "start_time": self.svqueryresult.start_time.strftime(TIMEF),
                "result_row_count": 0,
                "svquery": str(self.svquery.sodar_uuid),
            }
        )
        expected.assert_matches(res_json)

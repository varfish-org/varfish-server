from bgjobs.models import JOB_STATE_DONE
from rest_framework.reverse import reverse

from variants.serializers import JobStatus
from variants.tests.factories import FilterBgJobFactory, SmallVariantQueryFactory
from variants.tests.test_views_api import TestSmallVariantQueryBase


class TestSmallVariantQueryListAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryListAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_get(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse("variants:ajax-query-case-list", kwargs={"case": self.case.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)


class TestSmallVariantQueryCreateAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryCreateAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_post(self):
        with self.login(self.superuser):
            query_settings = {
                "effects": ["missense_variant"],
                "quality": {
                    self.case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}
                },
                "genotype": {self.case.index: "variant"},
            }
            request_data = self._construct_request_data(query_settings)
            response = self.client.post(
                reverse("variants:ajax-query-case-create", kwargs={"case": self.case.sodar_uuid}),
                request_data,
                format="json",
            )
            self.assertEqual(response.status_code, 201)


class TestSmallVariantQueryRetrieveAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryRetrieveAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_get(self):
        query = SmallVariantQueryFactory(case=self.case, user=self.superuser)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-query-case-retrieve",
                    kwargs={"smallvariantquery": query.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)


class TestSmallVariantQueryStatusAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryStatusAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_get(self):
        filter_job = FilterBgJobFactory(
            case=self.case, user=self.superuser, bg_job__status=JOB_STATE_DONE
        )
        query = filter_job.smallvariantquery
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-query-case-status",
                    kwargs={"smallvariantquery": query.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)


class TestSmallVariantQueryUpdateAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryUpdateAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_put(self):
        query = SmallVariantQueryFactory(case=self.case, user=self.superuser)
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "variants:ajax-query-case-update",
                    kwargs={"smallvariantquery": query.sodar_uuid},
                ),
                {"name": "new name", "public": True},
            )
            self.assertEqual(response.status_code, 200)

    def test_patch(self):
        query = SmallVariantQueryFactory(case=self.case, user=self.superuser)
        with self.login(self.superuser):
            response = self.client.put(
                reverse(
                    "variants:ajax-query-case-update",
                    kwargs={"smallvariantquery": query.sodar_uuid},
                ),
                {"name": "new name", "public": True},
            )
            self.assertEqual(response.status_code, 200)


class TestSmallVariantQueryFetchResultsAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryFetchResultsAjaxView.

    Logic is tested in test_view_api.py, this is testing the base functionality.
    """

    def test_get(self):
        filter_job = FilterBgJobFactory(
            case=self.case, user=self.superuser, bg_job__status=JOB_STATE_DONE
        )
        query = filter_job.smallvariantquery
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-query-case-fetch-results",
                    kwargs={"smallvariantquery": query.sodar_uuid},
                ),
            )
            self.assertEqual(response.status_code, 200)

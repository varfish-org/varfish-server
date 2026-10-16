from rest_framework.reverse import reverse

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


class TestSmallVariantQueryListCreateAjaxView(TestSmallVariantQueryBase):
    """Tests for SmallVariantQueryListCreateAjaxView."""

    def test_post_query_settings_violating_schema(self):
        url = reverse("variants:ajax-query-list-create", kwargs={"case": self.case.sodar_uuid})
        query_settings = {
            "effects": [],
            "quality": {self.case.pedigree[0]["patient"]: {}},
            "genotype": {},
            "gnomad_exomes_frequency": 0.1,
        }
        with self.login(self.superuser):
            response = self.client.post(url, {"query_settings": query_settings}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "query_settings": [
                    "$.gnomad_exomes_frequency: 0.1 is greater than the maximum of 0.05"
                ]
            },
        )

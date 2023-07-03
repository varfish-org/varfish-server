from bgjobs.models import JOB_STATE_DONE
from rest_framework.reverse import reverse

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

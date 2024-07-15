import re

from django.urls import reverse
import jsonmatch
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
import requests_mock

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")


class TestBeaconInfoAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with Organisation."""

    def setUp(self):
        super().setUp()

    @requests_mock.Mocker()
    def get_get(self, r_mock):
        url = reverse("beaconsite:ajax-beacon-info", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 2)
        expected0 = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "clinvar_id": 505735,
                "name": (
                    "Institute for Medical Genetics and Human Genetics (Charité - Universitätsmedizin "
                    "Berlin), Charité - Universitätsmedizin"
                ),
            }
        )
        expected0.assert_matches(res_json[0])
        expected1 = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "clinvar_id": 507461,
                "name": "CUBI - Core Unit Bioinformatics (Berlin Institute of Health)",
            }
        )
        expected1.assert_matches(res_json[1])

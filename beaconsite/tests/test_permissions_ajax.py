from unittest import skip

import cattr
from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
import requests_mock

from ..models import Site
from ..models_api import BeaconAlleleRequest
from .factories import SiteFactory


class TestOrganisationAjaxViews(TestProjectAPIPermissionBase):
    @requests_mock.Mocker()
    def test_get(self, r_mock):
        _local_site = SiteFactory(role=Site.LOCAL)
        remote_site = SiteFactory()
        url = reverse(
            "beaconsite:ajax-beacon-info",
            kwargs={"site": remote_site.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users = [
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
            self.anonymous,
            self.user_no_roles,
        ]

        r_mock.get(
            remote_site.entrypoint_url,
            status_code=200,
            json={
                "id": "com.example.beacon",
                "name": "Example Beacon Site",
                "apiVersion": "v1.0.0",
                "organisation": {
                    "id": "com.example",
                    "name": "Example Org",
                    "description": "Just for example...",
                },
                "datasets": [
                    {
                        "id": "com.example.beacon.ds-1",
                        "name": "Dataset",
                        "assembly": "GRCh37",
                        "description": None,
                    }
                ],
            },
        )

        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 302, method="GET")  # redirect to login


class TestBeaconQueryAjaxView(TestProjectAPIPermissionBase):
    @requests_mock.Mocker()
    def test_get(self, r_mock):
        _local_site = SiteFactory(role=Site.LOCAL)
        remote_site = SiteFactory()
        beacon_allele_request = BeaconAlleleRequest(
            assemblyId="GRCh37",
            referenceName="1",
            start=123,
            referenceBases="C",
            alternateBases="T",
        )
        url_params = "&".join(
            "%s=%s" % (k, v) for k, v in cattr.unstructure(beacon_allele_request).items()
        )
        url = reverse(
            "beaconsite:ajax-beacon-query",
            kwargs={"site": remote_site.sodar_uuid},
        )
        good_users = [
            self.superuser,
        ]
        bad_users = [
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
            self.anonymous,
            self.user_no_roles,
        ]

        r_mock.get(
            "%s/query?%s" % (remote_site.entrypoint_url, url_params),
            status_code=200,
            json={
                "beaconId": "com.example.beacon",
                "apiVersion": "v1.0.0",
                "exists": True,
                "alleleRequest": {
                    "referenceName": "1",
                    "referenceBases": "G",
                    "start": 16977,
                    "alternateBases": "A",
                    "assemblyId": "GRCh37",
                },
                "datasetAlleleResponse": None,
                "error": None,
            },
        )

        self.maxDiff = None

        self.assert_response("%s?%s" % (url, url_params), good_users, 200, method="GET")
        self.assert_response(
            "%s?%s" % (url, url_params), bad_users, 302, method="GET"
        )  # redirect to login

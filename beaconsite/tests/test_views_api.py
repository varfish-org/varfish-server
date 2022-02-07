import cattr
from django.shortcuts import reverse
from projectroles.tests.test_views_api import TestAPIViewsBase

from variants.tests.factories import SmallVariantFactory
from .test_permissions_api import AcceptHeaderMixin
from ..models import Site
from .factories import ConsortiumWithLocalAndRemoteSiteFactory, ConsortiumAssignmentFactory
from ..models_api import BeaconAlleleRequest


class TestBeaconInfoApiView(AcceptHeaderMixin, TestAPIViewsBase):
    def setUp(self):
        super().setUp()
        self.consortium = ConsortiumWithLocalAndRemoteSiteFactory()
        self.local_site = Site.objects.get(role=Site.LOCAL)
        self.remote_site = Site.objects.get(role=Site.REMOTE)
        ConsortiumAssignmentFactory(
            consortium=self.consortium, project=self.project,
        )

    def test_get_info(self):
        with self.login(self.user):
            extra = self.get_accept_header(None, None)
            response = self.client.get(reverse("beaconsite:beacon-api-info"), **extra)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.local_site.identifier,
                "name": self.local_site.title,
                "apiVersion": "v1.0.0",
                "organisation": {
                    "id": str(self.local_site.sodar_uuid),
                    "name": self.local_site.title,
                    "description": self.local_site.description,
                },
                "datasets": [
                    {
                        "id": str(self.project.sodar_uuid),
                        "name": self.project.title,
                        "assembly": "GRCh37",
                        "description": str(self.project.description),
                    }
                ],
            },
        )


class TestBeaconQueryApiView(AcceptHeaderMixin, TestAPIViewsBase):
    def setUp(self):
        super().setUp()
        self.consortium = ConsortiumWithLocalAndRemoteSiteFactory()
        self.local_site = Site.objects.get(role=Site.LOCAL)
        self.remote_site = Site.objects.get(role=Site.REMOTE)
        ConsortiumAssignmentFactory(
            consortium=self.consortium, project=self.project,
        )
        self.small_variant = SmallVariantFactory(case__project=self.project)
        self.beacon_allele_request = BeaconAlleleRequest(
            assemblyId=self.small_variant.release,
            referenceName=self.small_variant.chromosome,
            start=self.small_variant.start,
            referenceBases=self.small_variant.reference,
            alternateBases=self.small_variant.alternative,
        )

    def test_query(self):
        url = reverse("beaconsite:beacon-api-query")
        url += "?" + "&".join(
            "%s=%s" % (k, v) for k, v in cattr.unstructure(self.beacon_allele_request).items()
        )

        with self.login(self.user):
            extra = self.get_accept_header(None, None)
            response = self.client.get(url, **extra)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "alleleRequest": cattr.unstructure(self.beacon_allele_request),
                "apiVersion": "v1.0.0",
                "beaconId": self.local_site.identifier,
                "datasetAlleleResponse": None,
                "error": None,
                "exists": False,
            },
        )

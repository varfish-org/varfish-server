import datetime
import urllib
from wsgiref.handlers import format_date_time

from Crypto.PublicKey import RSA
import cattr
from django.shortcuts import reverse
from django.utils import timezone
import httpsig
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.tests.factories import SmallVariantFactory

from ..models import Site
from ..models_api import BeaconAlleleRequest
from ..views_api import _header_canonical
from .factories import ConsortiumAssignmentFactory, ConsortiumWithLocalAndRemoteSiteFactory


class AcceptHeaderMixin:
    def get_date(self):
        return timezone.now()

    def get_private_key(self):
        return self.remote_site.private_key

    # TODO: this should not be necessary but accept header is always generated in tests
    # TODO: but we need a way to spike in keyword arguments into the header.
    def get_accept_header(self, media_type, version):
        hs = httpsig.HeaderSigner(
            self.remote_site.identifier,
            self.get_private_key(),
            algorithm="rsa-sha256",
            headers=["date", "x-beacon-user"],
        )
        header = {
            "X-Beacon-User": "jdoe",
            "Date": format_date_time(self.get_date().timestamp()),
        }
        entrypoint_url = urllib.parse.urlsplit(self.remote_site.entrypoint_url)
        signed_headers_dict = hs.sign(header, method="GET", path=entrypoint_url.path)
        return {_header_canonical(k): v for k, v in signed_headers_dict.items()}


class TestBeaconInfoApiView(AcceptHeaderMixin, TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.consortium = ConsortiumWithLocalAndRemoteSiteFactory()
        self.remote_site = Site.objects.get(role=Site.REMOTE)
        ConsortiumAssignmentFactory(
            consortium=self.consortium,
            project=self.project,
        )

    def test_success(self):
        url = reverse("beaconsite:beacon-api-info")

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        self.assert_response_api(url, all_users, 200)

    def test_fail_key(self):
        url = reverse("beaconsite:beacon-api-info")

        def _get_private_key():
            return RSA.generate(2048).export_key("PEM").decode("ascii")

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        old_get_private_key = self.get_private_key
        self.get_private_key = _get_private_key
        self.assert_response_api(url, all_users, 403)
        self.get_private_key = old_get_private_key

    def test_fail_clock_skew(self):
        url = reverse("beaconsite:beacon-api-info")

        def _get_date():
            return timezone.now() - datetime.timedelta(hours=5)

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        old_get_date = self.get_date
        self.get_date = _get_date
        self.assert_response_api(url, all_users, 403)
        self.get_date = old_get_date


class TestBeaconQueryApiView(AcceptHeaderMixin, TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.consortium = ConsortiumWithLocalAndRemoteSiteFactory()
        self.remote_site = Site.objects.get(role=Site.REMOTE)
        ConsortiumAssignmentFactory(
            consortium=self.consortium,
            project=self.project,
        )
        self.small_variant = SmallVariantFactory(case__project=self.project)
        self.beacon_allele_request = BeaconAlleleRequest(
            assemblyId=self.small_variant.release,
            referenceName=self.small_variant.chromosome,
            start=self.small_variant.start,
            referenceBases=self.small_variant.reference,
            alternateBases=self.small_variant.alternative,
        )

    def test_success(self):
        url = reverse("beaconsite:beacon-api-query")
        url += "?" + "&".join(
            "%s=%s" % (k, v) for k, v in cattr.unstructure(self.beacon_allele_request).items()
        )

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        self.assert_response_api(url, all_users, 200)

    def test_fail_key(self):
        url = reverse("beaconsite:beacon-api-query")
        url += "?" + "&".join(
            "%s=%s" % (k, v) for k, v in cattr.unstructure(self.beacon_allele_request).items()
        )

        def _get_private_key():
            return RSA.generate(2048).export_key("PEM").decode("ascii")

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        old_get_private_key = self.get_private_key
        self.get_private_key = _get_private_key
        self.assert_response_api(url, all_users, 403)
        self.get_private_key = old_get_private_key

    def test_fail_clock_skew(self):
        url = reverse("beaconsite:beacon-api-query")
        url += "?" + "&".join(
            "%s=%s" % (k, v) for k, v in cattr.unstructure(self.beacon_allele_request).items()
        )

        def _get_date():
            return timezone.now() - datetime.timedelta(hours=5)

        # The user does not matter, the key does.
        all_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
            self.anonymous,
        ]
        old_get_date = self.get_date
        self.get_date = _get_date
        self.assert_response_api(url, all_users, 403)
        self.get_date = old_get_date

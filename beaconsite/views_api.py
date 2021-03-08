import re

import cattr
from django.utils import timezone
from django.utils.http import parse_http_date
from httpsig import HeaderVerifier
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, authentication
from sqlalchemy import select, and_

from variants.helpers import SQLALCHEMY_ENGINE
from variants.models import Case, SmallVariant
from .models import Site
from .models_api import (
    BeaconInfo,
    Dataset,
    Organisation,
    BeaconAlleleRequest,
    API_VERSION,
    BeaconAlleleResponse,
)


def _header_canonical(header_name):
    """Translate HTTP headers to Django header names."""
    # Translate as stated in the docs:
    # https://docs.djangoproject.com/en/1.6/ref/request-response/#django.http.HttpRequest.META
    header_name = header_name.lower()
    if header_name == "content-type":
        return "CONTENT-TYPE"
    elif header_name == "content-length":
        return "CONTENT-LENGTH"
    return "HTTP_%s" % header_name.replace("-", "_").upper()


class _SignedSiteAuthentication(authentication.BaseAuthentication):
    """Based on the code of ``django-rest-framework-httpsignature``."""

    SIGNATURE_RE = re.compile('signature="(.+?)"')
    HEADERS_RE = re.compile('headers="([\(\)\sa-z0-9-]+?)"')
    KEYID_RE = re.compile('keyId="([\(\)\sa-z0-9-]+?)"')
    ALGORITHM_RE = re.compile('algorithm="([\(\)\sa-z0-9-]+?)"')

    def get_signature_from_signature_string(self, signature):
        """Return the signature from the signature header or None."""
        match = self.SIGNATURE_RE.search(signature)
        if not match:
            return None
        return match.group(1)

    def get_headers_from_signature(self, signature):
        """Returns a list of headers fields to sign.

        According to http://tools.ietf.org/html/draft-cavage-http-signatures-03
        section 2.1.3, the headers are optional. If not specified, the single
        value of "Date" must be used.
        """
        match = self.HEADERS_RE.search(signature)
        if not match:
            return ["date", "x-beacon-user"]
        headers_string = match.group(1)
        return headers_string.split()

    def get_keyid_from_signature(self, signature):
        """Returns the keyId field."""
        match = self.KEYID_RE.search(signature)
        if not match:
            return None
        return match.group(1)

    def get_algorithm_from_signature(self, signature):
        """Returns the algorithm field."""
        match = self.ALGORITHM_RE.search(signature)
        if not match:
            return None
        return match.group(1)

    def build_dict_to_verify(self, request, signature_headers):
        """Build a dict with headers and values used in the signature.
        "signature_headers" is a list of lowercase header names.
        """
        d = {}
        for header in signature_headers:
            if header == "(request-target)":
                continue
            d[header] = request.META.get(_header_canonical(header))
        return d

    def is_signature_valid(self, site, request):
        """Return whether the request signature is valid for ``site``."""
        secret = site.private_key if site.is_key_algo_symmetric() else site.public_key

        x = _header_canonical("Authorization")
        sent_signature = request.META.get(x)
        signature_headers = self.get_headers_from_signature(sent_signature)
        if len({"date", "x-beacon-user"} & set(signature_headers)) != 2:
            raise exceptions.AuthenticationFailed("Headers Date and X-Beacon-User must be signed")
        if "authorization" not in signature_headers:
            signature_headers += ["authorization"]
        headers_to_sign = self.build_dict_to_verify(request, signature_headers)

        # Sign string and compare.
        verifier = HeaderVerifier(headers=headers_to_sign, secret=secret)
        return verifier.verify()

    def authenticate(self, request):
        # Check if request has a "Signature" request header.
        authorization_header = _header_canonical("Authorization")
        sent_string = request.META.get(authorization_header)
        if not sent_string:
            raise exceptions.AuthenticationFailed("No signature provided")
        key_id = self.get_keyid_from_signature(sent_string)

        # Fetch site for API key from the data store.
        try:
            site = Site.objects.get(identifier=key_id, state=Site.ENABLED)
        except TypeError:
            raise exceptions.AuthenticationFailed("Bad site")

        if not self.is_signature_valid(site, request):
            raise exceptions.AuthenticationFailed("Bad signature")
        return site, key_id


class _SiteBeaconPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None


class _RequestAgeAcceptable(BasePermission):
    def has_permission(self, request, view):
        site = request.user
        header_ts = parse_http_date(request.META.get(_header_canonical("Date")))
        now_ds = timezone.now().timestamp()
        clock_skew = header_ts - now_ds
        if abs(clock_skew) > site.max_clock_skew:
            raise exceptions.PermissionDenied("Clock skeq detected (%d seconds)" % clock_skew)
        return True


class BeaconInfoApiView(APIView):
    """Implementation of the GA4GH info endpoint."""

    authentication_classes = (_SignedSiteAuthentication,)
    permission_classes = (_SiteBeaconPermission, _RequestAgeAcceptable)
    http_method_names = ("get",)

    def get(self, request, *args, **kwargs):
        return self._handle(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._handle(request, *args, **kwargs)

    def _handle(self, request, *_args, **_kwargs):
        """Handle the GA4GH Beacon query.

        NB: the remote ``Site`` object is stored in request.user.  The permission logic ensures that only active
        sites can query.
        """
        remote_site = request.user
        local_site = Site.objects.get(role=Site.LOCAL)
        if local_site.state != Site.ENABLED:
            return (
                Response({"detail": "The site is not enabled!"}, status=400, reason="invalid site"),
            )

        if local_site.state != Site.ENABLED:
            return Response(
                {"detail": "The site is not enabled!"}, status=400, reason="invalid site"
            )
        datasets = [
            Dataset(
                id=str(p.sodar_uuid), name=p.title, assembly="GRCh37", description=p.description,
            )
            for p in remote_site.get_all_projects()
        ]
        result = BeaconInfo(
            id=local_site.identifier,
            name=local_site.title,
            apiVersion=API_VERSION,
            organisation=Organisation(
                id=str(local_site.sodar_uuid),
                name=local_site.title,
                description=local_site.description,
            ),
            datasets=tuple(datasets),
        )
        return Response(cattr.unstructure(result))


class BeaconQueryApiView(APIView):
    """Implementation of the GA4GH query endpoint."""

    authentication_classes = (_SignedSiteAuthentication,)
    permission_classes = (_SiteBeaconPermission, _RequestAgeAcceptable)
    http_method_names = ("get", "post")

    def get(self, request, *args, **kwargs):
        return self._handle(request.GET, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._handle(request.POST, request, *args, **kwargs)

    def _handle(self, params, request, *_args, **_kwargs):
        """Handle the GA4GH Beacon query.

        NB: the remote ``Site`` object is stored in request.user.  The permission logic ensures that only active
        sites can query.
        """
        allele_req = cattr.structure(dict(params.items()), BeaconAlleleRequest)
        remote_site = request.user
        # TODO: perform one large query only
        project_pks = [p.pk for p in remote_site.get_all_projects()]
        result = (
            select(["*"])
            .select_from(SmallVariant.sa)
            .where(
                and_(
                    SmallVariant.sa.case_id.in_(
                        select([Case.sa.id])
                        .select_from(Case.sa)
                        .where(Case.sa.project_id.in_(project_pks))
                    ),
                    SmallVariant.sa.release == allele_req.assemblyId,
                    SmallVariant.sa.chromosome == allele_req.referenceName,
                    SmallVariant.sa.start == allele_req.start,
                    SmallVariant.sa.reference == allele_req.referenceBases,
                    SmallVariant.sa.alternative == allele_req.alternateBases,
                )
            )
        )
        sum_hom_alt = 0
        sum_het_alt = 0
        sum_hemi_alt = 0
        for row in SQLALCHEMY_ENGINE.execute(result):
            sum_hom_alt += row.num_hom_alt
            sum_het_alt += row.num_het
            sum_hemi_alt += row.num_hemi_alt
        total_alleles = sum_hom_alt * 2 + sum_het_alt + sum_hemi_alt

        site = Site.objects.get(role=Site.LOCAL)
        if site.state != Site.ENABLED:
            return (
                Response({"detail": "The site is not enabled!"}, status=400, reason="invalid site"),
            )

        result = BeaconAlleleResponse(
            beaconId=site.identifier,
            apiVersion=API_VERSION,
            exists=(total_alleles > 0),
            alleleRequest=allele_req,
        )
        return Response(cattr.unstructure(result))

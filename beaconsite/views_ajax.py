import cattr
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from projectroles.views import LoginRequiredMixin, LoggedInPermissionMixin
import requests
from requests_http_signature import HTTPSignatureAuth

from .models import Site
from .models_api import BeaconAlleleRequest


class BeaconInfoAjaxView(LoginRequiredMixin, LoggedInPermissionMixin, View):
    """AJAX endpoint to remote site info endpoint via GA4GH Beacon API."""

    permission_required = "beaconsite.view_data"

    def get(self, request, *args, **kwargs):
        local_site = Site.objects.get(role=Site.LOCAL)
        remote_site = get_object_or_404(Site, sodar_uuid=kwargs.get("site"))
        r = requests.get(
            remote_site.entrypoint_url,
            headers={"X-Beacon-User": request.user.username},
            auth=HTTPSignatureAuth(
                algorithm=local_site.key_algo,
                key=str(local_site.private_key).encode("utf-8"),
                key_id=local_site.identifier,
                headers=["date", "x-beacon-user"],
            ),
        )
        return JsonResponse(data=r.json(), status=r.status_code, reason=r.reason)


class BeaconQueryAjaxView(LoginRequiredMixin, LoggedInPermissionMixin, View):
    """AJAX endpoint to remote site query endpoint via GA4GH Beacon API."""

    permission_required = "beaconsite.view_data"

    def get(self, request, *args, **kwargs):
        local_site = Site.objects.get(role=Site.LOCAL)
        remote_site = get_object_or_404(Site, sodar_uuid=kwargs.get("site"))
        allele_req = cattr.structure(request.GET, BeaconAlleleRequest)
        entrypoint_url = "%s/query" % remote_site.entrypoint_url
        r = requests.get(
            entrypoint_url,
            params=cattr.unstructure(allele_req),
            headers={"X-Beacon-User": request.user.username},
            auth=HTTPSignatureAuth(
                algorithm=local_site.key_algo,
                key=str(local_site.private_key).encode("utf-8"),
                key_id=local_site.identifier,
                headers=["date", "x-beacon-user"],
            ),
        )
        return JsonResponse(data=r.json(), status=r.status_code, reason=r.reason)

"""API views for ``variants`` app.

Currently, the REST API only works for the ``Case`` model.
"""
from projectroles.views_api import SODARAPIBaseProjectMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView

# # TOOD: timeline update

from .models import Case
from .serializers import CaseSerializer


class CaseListCreateView(
    SODARAPIBaseProjectMixin, ListAPIView,
):
    """DRF list-create API view the ``Case`` model."""

    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        if self.request.method == "POST":
            return "variants.add_case"
        else:
            return "variants.view_data"


class CaseListRetrieveUpdateDestroyView(
    SODARAPIBaseProjectMixin, RetrieveAPIView,
):
    """DRF retrieve-update-destroy API view for the ``Case`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        if self.request.method == "GET":
            return "variants.view_data"
        elif self.request.method == "DELETE":
            return "variants.delete_case"
        else:
            return "variants.update_case"

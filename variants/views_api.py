"""API views for ``variants`` app.

Currently, the REST API only works for the ``Case`` model.
"""

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

# # TOOD: timeline update
# from projectroles.plugins import get_backend_api

from varfish.utils import ProjectMixin
from .models import Case
from .serializers import CaseSerializer


class CaseApiMixin(ProjectMixin):
    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())


class CaseListCreateView(CaseApiMixin, ListCreateAPIView):
    """DRF list-create API view the ``Folder`` model."""

    serializer_class = CaseSerializer

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_permission_required(self):
        if self.request.method == "POST":
            return "filesfolders.add_data"
        else:
            return "filesfolders.view_data"


class CaseListRetrieveUpdateDestroyView(CaseApiMixin, RetrieveUpdateDestroyAPIView):
    """DRF retrieve-update-destroy API view for the ``Folder`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"
    serializer_class = CaseSerializer

    def get_permission_required(self):
        if self.request.method == "GET":
            return "case.view_data"
        elif self.request.method == "DELETE":
            return "case.delete_case"
        else:
            return "case.update_case"

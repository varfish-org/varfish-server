from django.shortcuts import get_object_or_404
from projectroles.models import Project
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination

from cases_import.models import CaseImportAction
from cases_import.serializers import CaseImportActionSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CaseImportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CaseImportActionListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    pagination_class = CaseImportPagination
    permission_classes = [SODARAPIProjectPermission]
    queryset = CaseImportAction.objects.all()
    renderer_classes = [VarfishApiRenderer]
    serializer_class = CaseImportActionSerializer
    versioning_class = VarfishApiVersioning

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = get_object_or_404(
            Project.objects.all(), sodar_uuid=self.kwargs["project"]
        )
        return result

    def get_queryset(self):
        return CaseImportAction.objects.filter(project__sodar_uuid=self.kwargs["project"])

    def get_permission_required(self):
        if self.request.method == "POST":
            return "cases_import.create_data"
        else:
            return "cases_import.view_data"


class CaseImportActionRetrieveUpdateDestroyApiView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "caseimportaction"

    pagination_class = CaseImportPagination
    permission_classes = [SODARAPIProjectPermission]
    queryset = CaseImportAction.objects.all()
    renderer_classes = [VarfishApiRenderer]
    serializer_class = CaseImportActionSerializer
    versioning_class = VarfishApiVersioning

    def get_permission_required(self):
        if self.request.method == "GET":
            return "cases_import.view_data"
        elif self.request.method == "DELETE":
            return "cases_import.delete_data"
        else:
            return "cases_import.update_data"

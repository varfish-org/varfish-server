from django.db import transaction
from django.shortcuts import get_object_or_404
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination

from cases_import.models import CaseImportAction, CaseImportBackgroundJob
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
        result["project"] = self.get_project(request=self.request)
        return result

    def get_queryset(self):
        return CaseImportAction.objects.filter(project__sodar_uuid=self.kwargs["project"])

    def get_permission_required(self):
        if self.request.method == "POST":
            return "cases_import.create_data"
        else:
            return "cases_import.view_data"

    def perform_create(self, serializer):
        """Override the ``perform_create()`` method as to create the appropriate background
        import job.
        """
        with transaction.atomic():
            super().perform_create(serializer)
            # at this point ``serializer.instance`` has been set and can be used
            CaseImportBackgroundJob.objects.create_full(
                caseimportaction=serializer.instance,
                project=self.get_project(),
                user=self.request.user,
            )


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

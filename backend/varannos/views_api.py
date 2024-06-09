import sys

from projectroles.views_api import SODARAPIGenericProjectMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from varannos.models import VarAnnoSet, VarAnnoSetEntry
from varannos.serializers import VarAnnoSetEntrySerializer, VarAnnoSetSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class VarAnnoSetListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """DRF list-create API view the ``VarAnnoSet`` model."""

    serializer_class = VarAnnoSetSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return VarAnnoSet.objects.filter(project=self.get_project())

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["project"] = self.get_project()
        return result

    def get_permission_required(self):
        if self.request.method == "POST":
            return "varannos.create_data"
        else:
            return "varannose.view_data"


class VarAnnoSetRetrieveUpdateDestroyApiView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``VarAnnoSet`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "varannoset"

    serializer_class = VarAnnoSetSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_permission_required(self):
        if self.request.method == "GET":
            return "varannos.view_data"
        elif self.request.method == "DELETE":
            return "varannos.delete_data"
        else:
            return "varannos.update_data"


class VarAnnoSetEntryListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """DRF list-create API view the ``VarAnnoSetEntry`` model."""

    serializer_class = VarAnnoSetEntrySerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return VarAnnoSetEntry.objects.filter(varannoset=self.get_varannoset())

    def get_serializer_context(self):
        result = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:
            return result
        result["varannoset"] = self.get_varannoset()
        return result

    def get_varannoset(self):
        return VarAnnoSet.objects.get(sodar_uuid=self.kwargs["varannoset"])

    def get_permission_required(self):
        if self.request.method == "POST":
            return "varannos.create_data"
        else:
            return "varannose.view_data"


class VarAnnoSetEntryRetrieveUpdateDestroyApiView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``VarAnnoSetEntry`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "varannosetentry"

    serializer_class = VarAnnoSetEntrySerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return VarAnnoSetEntry.objects.all()

    def get_permission_required(self):
        if self.request.method == "GET":
            return "varannos.view_data"
        elif self.request.method == "DELETE":
            return "varannos.delete_data"
        else:
            return "varannos.update_data"

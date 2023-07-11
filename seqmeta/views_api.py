from projectroles.views_api import SODARAPIGenericProjectMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from seqmeta.models import EnrichmentKit, TargetBedFile
from seqmeta.serializers import EnrichmentKitSerializer, TargetBedFileSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class EnrichmentKitListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """DRF list-create API view the ``EnrichmentKit`` model."""

    serializer_class = EnrichmentKitSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return EnrichmentKit.objects.filter(project=self.get_project())

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["project"] = self.get_project()
        return result

    def get_permission_required(self):
        if self.request.method == "POST":
            return "seqmeta.create_data"
        else:
            return "seqmeta.view_data"


class EnrichmentKitRetrieveUpdateDestroyApiView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``EnrichmentKit`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "enrichmentkit"

    serializer_class = EnrichmentKitSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_permission_required(self):
        if self.request.method == "GET":
            return "seqmeta.view_data"
        elif self.request.method == "DELETE":
            return "seqmeta.delete_data"
        else:
            return "seqmeta.update_data"


class TargetBedFileListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """DRF list-create API view the ``TargetBedFile`` model."""

    serializer_class = TargetBedFileSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return TargetBedFile.objects.filter(enrichmentkit=self.get_enrichmentkit())

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["enrichmentkit"] = self.get_enrichmentkit()
        return result

    def get_enrichmentkit(self):
        return EnrichmentKit.objects.get(sodar_uuid=self.kwargs["enrichmentkit"])

    def get_permission_required(self):
        if self.request.method == "POST":
            return "seqmeta.create_data"
        else:
            return "seqmeta.view_data"


class TargetBedFileRetrieveUpdateDestroyApiView(
    SODARAPIGenericProjectMixin, RetrieveUpdateDestroyAPIView
):
    """DRF retrieve-update-destroy API view for the ``TargetBedFile`` model."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "targetbedfile"

    serializer_class = TargetBedFileSerializer
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get_queryset(self):
        return TargetBedFile.objects.all()

    def get_permission_required(self):
        if self.request.method == "GET":
            return "seqmeta.view_data"
        elif self.request.method == "DELETE":
            return "seqmeta.delete_data"
        else:
            return "seqmeta.update_data"

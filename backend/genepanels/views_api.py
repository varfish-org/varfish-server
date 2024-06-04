from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404

from genepanels.models import GenePanel, GenePanelCategory
from genepanels.serializers import GenePanelCategorySerializer, GenePanelSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class GenePanelCategoryListApiView(ListAPIView):
    """List all ``GenePanelCategory`` entries with ``GenePanel``.

    **URL:** ``/genepanels/api/gene-panel-category``

    **Methods:** GET

    **Returns:**
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    queryset = GenePanelCategory.objects.all()

    serializer_class = GenePanelCategorySerializer


class LookupGenePanelApiView(RetrieveAPIView):
    """Retrieve information about a gene panel.

    **URL:** ``/genepanels/api/lookup-genepanel/``

    **Methods:** GET

    **Returns:**
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = GenePanelSerializer

    def get_object(self):
        query_term = self.request.GET.get("query", "")
        if query_term.startswith("GENEPANEL:"):
            return get_object_or_404(GenePanel.objects, identifier=query_term[10:])
        return Http404("Query does not start with 'GENEPANEL:'")

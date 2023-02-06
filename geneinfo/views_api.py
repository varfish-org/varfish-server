import re

from django.http import Http404
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from geneinfo.models import Hgnc
from geneinfo.serializers import (
    Gene,
    GeneInfoSerializer,
    GenePanelCategorySerializer,
    GenePanelSerializer,
    GeneSerializer,
)
from geneinfo.views import get_gene_infos
from genepanels.models import GenePanel, GenePanelCategory
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning

#: Regular expression for integers.
RE_INT = re.compile(r"^\d\+$")


class LookupGeneApiView(generics.RetrieveAPIView):
    """Retrieve information about a gene.

    **URL:** ``/geneinfo/api/lookup-gene/``

    **Methods:** GET

    **Returns:**
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = GeneInfoSerializer

    def get_object(self):
        query_term = self.request.GET.get("query", "")
        if query_term.startswith("ENSG"):
            filter_kwargs = {"ensembl_gene_id": query_term}
        elif query_term.startswith("HGNC:"):
            filter_kwargs = {"hgnc_id": query_term}
        elif RE_INT.match(query_term):
            filter_kwargs = {"entrez_id": query_term}
        else:
            filter_kwargs = {"symbol": query_term}
        return get_object_or_404(Hgnc.objects, **filter_kwargs)


class LookupGenePanelApiView(generics.RetrieveAPIView):
    """Retrieve information about a gene panel.

    **URL:** ``/geneinfo/api/lookup-genepanel/``

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


class GeneInfosApiView(generics.RetrieveAPIView):
    """Retrieve detailed information about genes (for variant details view).

    **URL:** ``/geneinfo/api/gene-infos/${database}/${geneid}/?ensembl_transcript_id=${ensembl_transcript_id}``

    **Methods:** GET

    **Returns:**
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = GeneSerializer

    def get_object(self):
        return Gene(
            **get_gene_infos(
                self.kwargs["database"],
                self.kwargs["geneid"],
                self.request.GET.get("ensembl_transcript_id"),
            )
        )


class GenePanelCategoryListApiView(generics.ListAPIView):
    """List all ``GenePanelCategory`` entries with ``GenePanel``.

    **URL:** ``/geneinfo/api/gene-panel-category``

    **Methods:** GET

    **Returns:**
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    queryset = GenePanelCategory.objects.all()

    serializer_class = GenePanelCategorySerializer

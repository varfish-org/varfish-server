import binning
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from svs.models import StructuralVariant
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case


class SvFetchVariantsAjaxViewPermission(SODARAPIProjectPermission):
    """Project-based permission for ``SvQueryListCreateAjaxView``.

    Also used for ``SvQueryRetrieveUpdateDestroyAjaxViewPermission``.
    """

    def get_project(self, request=None, kwargs=None):
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class SvFetchVariantsAjaxView(APIView):
    """AJAX endpoint for retrieving structural variants from the given case.

    **URL:** ``/ajax/fetch-variants/{case.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SvFetchVariantsAjaxViewPermission]

    #: Will at most query this number of records from database.  Fewer may be returned to the client as we fetch
    #: by UCSC bin and then post-filter for overlap.
    MAX_RECORDS = 100

    def get(self, request, **kwargs):
        def overlaps(s1, e1, s2, e2):
            return s1 < e2 and s2 < e1

        def describe(record):
            if record.sv_type == "INS":
                return f"INS @{record.chromosome}:{record.start:,}"
            elif record.sv_type == "BND":
                return f"BND {record.chromosome}:{record.start:,} -> {record.chromosome2}:{record.end:,}"
            else:
                return f"{record.sv_type} @{record.chromosome}:{record.start:,}-{record.end:,}"

        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        structuralvariantset = case.latest_structural_variant_set
        chromosome = request.GET.get("chromosome")
        if chromosome.startswith("chr"):
            chromosome = chromosome[3:]
        if structuralvariantset.release == "GRCh38":
            chromosome = f"chr{chromosome}"
        start = int(float(request.GET.get("start", "1")))
        end = int(float(request.GET.get("end", start)))
        if start > end:
            end = start
        bins = binning.overlapping_bins(start, end)
        qs = StructuralVariant.objects.filter(
            case_id=case.id, set_id=structuralvariantset.id, chromosome=chromosome, bin__in=bins
        )
        if self.MAX_RECORDS:
            qs = qs[: self.MAX_RECORDS]
        result = [
            {
                "chromosome": record.chromosome,
                "start": record.start - 1,
                "end": record.end,
                "sv_type": record.sv_type,
                "sv_sub_type": record.sv_sub_type,
                "genotype": record.genotype,
                "name": describe(record),
            }
            for record in qs
            if overlaps(record.start, record.end, start, end)
        ]
        return Response(result)

    def get_permission_required(self):
        return "svs.view_data"

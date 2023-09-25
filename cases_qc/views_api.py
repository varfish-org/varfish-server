from django.http import Http404
from projectroles.views_api import SODARAPIBaseProjectMixin
from rest_framework.generics import RetrieveAPIView

from cases.views_api import CasesApiPermission
from cases_qc.models import CaseQc
from cases_qc.serializers import CaseQcSerializer, VarfishStatsSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models.case import Case


class CaseQcRetrieveApiView(SODARAPIBaseProjectMixin, RetrieveAPIView):
    """
    Retrieve the latest ``CaseQc`` for the given case.

    This corresponds to the raw QC values imported into VarFish.  See
    ``VarfishStatsRetrieveApiView`` for the information used by the UI.

    **URL:** ``/cases_qc/api/caseqc/retrieve/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** serialized ``CaseQc`` if any, HTTP 404 if not found
    """

    lookup_field = "case"

    permission_classes = [CasesApiPermission]
    permission_required = "cases_qc.view_data"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseQcSerializer

    def get_project(self, request=None, kwargs=None):
        _ = request
        casephenotypeterms = CaseQc.objects.get(sodar_uuid=kwargs["case"])
        return casephenotypeterms.case.project

    def get_queryset(self):
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        qs = CaseQc.objects.filter(case=case)
        qs = qs.prefetch_related("dragencnvmetrics_set")
        return qs

    def get_object(self):
        result = self.get_queryset().filter(state=CaseQc.STATE_ACTIVE).first()
        if not result:
            raise Http404()
        return result


class VarfishStatsRetrieveApiView(CaseQcRetrieveApiView):
    """
    Retrieve the latest statistics to display in the UI for a case.

    **URL:** ``/cases_qc/api/varfishstats/retrieve/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** serialized ``CaseQc`` if any, HTTP 404 if not found
    """

    serializer_class = VarfishStatsSerializer

    def get_object(self):
        caseqc = super().get_object()
        return caseqc

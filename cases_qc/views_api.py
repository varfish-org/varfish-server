from projectroles.views_api import SODARAPIBaseProjectMixin
from rest_framework.generics import RetrieveAPIView

from cases.views_api import CasesApiPermission
from cases_qc.models import CaseQc
from cases_qc.serializers import CaseQcSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CaseQcRetrieveApiView(SODARAPIBaseProjectMixin, RetrieveAPIView):
    """
    Display the latest ``CaseQc`` for the given case.

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
        casephenotypeterms = CaseQc.objects.get(sodar_uuid=kwargs["case"])
        return casephenotypeterms.case.project

    def get_queryset(self):
        qs = CaseQc.objects.filter(case__sodar_uuid=self.kwargs["case"])
        qs = qs.prefetch_related("dragencnvmetrics_set")
        return qs

    def get_object(self):
        return self.get_queryset().filter(state=CaseQc.STATE_ACTIVE).first()

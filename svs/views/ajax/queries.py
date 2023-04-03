"""AJAX views for detailing with SV variant queries."""

from django.db.models.expressions import RawSQL
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination

from svs.models import SvQuery, SvQueryResultRow, SvQueryResultSet, create_sv_query_bg_job
from svs.serializers import (
    SvQueryResultRowSerializer,
    SvQueryResultSetSerializer,
    SvQuerySerializer,
    SvQueryWithLogsSerializer,
)
from svs.tasks import run_sv_query_bg_job
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case


class SvQueryListCreateAjaxViewPermission(SODARAPIProjectPermission):
    """Project-based permission for ``SvQueryListCreateAjaxView``."""

    def get_project(self, request=None, kwargs=None):
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class SvQueryListCreateAjaxView(ListCreateAPIView):
    """AJAX endpoint for listing and creating SV queries for a given case.

    After creation, a background job will be started to execute the query.

    **URL:** ``/svs/ajax/sv-query/list-create/{case.sodar_uuid}/``

    **Methods:** ``GET``, ``POST``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SvQueryListCreateAjaxViewPermission]

    serializer_class = SvQuerySerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        """Override to execute the new query in the background."""
        super().perform_create(serializer)
        bg_job = create_sv_query_bg_job(
            case=serializer.instance.case,
            svquery=SvQuery.objects.get(id=serializer.instance.id),
            user=serializer.instance.user,
        )
        run_sv_query_bg_job.delay(bg_job.id)

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return result

    def get_queryset(self):
        return SvQuery.objects.filter(case__sodar_uuid=self.kwargs.get("case")).select_related(
            "user", "case"
        )

    def get_permission_required(self):
        return "svs.view_data"


class SvQueryRetrieveUpdateDestroyAjaxViewPermission(SODARAPIProjectPermission):
    """Project-based permission for ``SvQueryListCreateAjaxView``.

    Also used for ``SvQueryRetrieveUpdateDestroyAjaxViewPermission``.
    """

    def get_project(self, request=None, kwargs=None):
        if "svquery" in kwargs:
            svquery = SvQuery.objects.get(sodar_uuid=kwargs["svquery"])
            return svquery.case.project
        elif "svqueryresultset" in kwargs:
            svqueryresultset = SvQueryResultSet.objects.get(sodar_uuid=kwargs["svqueryresultset"])
            return svqueryresultset.svquery.case.project
        else:
            raise RuntimeError("Must never happen")


class SvQueryRetrieveUpdateDestroyAjaxView(RetrieveUpdateDestroyAPIView):
    """AJAX endpoint for retrieving, updating, and deleting SV queries for a given case.

    **URL:** ``/svs/ajax/sv-query/retrieve-update-destroy/{svquery.sodar_uuid}/``

    **Methods:** ``GET``, ``PATCH``, ``PUT``, ``DELETE``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "svquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SvQueryRetrieveUpdateDestroyAjaxViewPermission]

    serializer_class = SvQueryWithLogsSerializer

    def get_queryset(self):
        return SvQuery.objects.all().select_related("user", "case")

    def get_permission_required(self):
        # TODO: only allow update/deletion of own query
        if self.request.method == "GET":
            return "svs.view_data"
        elif self.request.method == "DELETE":
            return "svs.delete_data"
        else:
            return "svs.update_data"


class SvQueryResultSetListAjaxView(ListAPIView):
    """AJAX endpoint for listing query result sets for a query.

    **URL:** ``/svs/ajax/sv-query-result-set/list/{svquery.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "svquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SvQueryRetrieveUpdateDestroyAjaxViewPermission]
    pagination_class = PageNumberPagination

    serializer_class = SvQueryResultSetSerializer

    def get_queryset(self):
        return SvQueryResultSet.objects.filter(
            svquery__sodar_uuid=self.kwargs.get("svquery")
        ).select_related("svquery")

    def get_permission_required(self):
        return "svs.view_data"


class SvQueryResultSetRetrieveAjaxView(RetrieveAPIView):
    """AJAX endpoint for retrieving query result sets.

    **URL:** ``/svs/ajax/sv-query-result-set/retrieve/{svqueryresultset.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "svqueryresultset"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SODARAPIProjectPermission]

    serializer_class = SvQueryResultSetSerializer

    def get_queryset(self):
        return SvQueryResultSet.objects.all().select_related("svquery")

    def get_permission_required(self):
        return "svs.view_data"


class SvQueryResultRowPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 1000
    page_size_query_param = "page_size"


class SvQueryResultRowListAjaxView(ListAPIView):
    """AJAX endpoint for listing query result rows for a query.

    **URL:** ``/svs/ajax/sv-query-result-row/list/{svqueryresultset.sodar_uuid}/``

    **Methods:** ``GET``
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "svqueryresultset"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    permission_classes = [SvQueryRetrieveUpdateDestroyAjaxViewPermission]
    pagination_class = SvQueryResultRowPagination

    serializer_class = SvQueryResultRowSerializer

    def get_queryset(self):
        bgdbs = ("dbvar", "dgv", "dgv_gs", "exac", "g1k", "gnomad", "inhouse")

        order_by_str = self.request.query_params.get("order_by", "chromosome_no,start")
        order_dir = self.request.query_params.get("order_dir", "asc")
        if order_by_str in ["payload.sv_length", "payload.tad_boundary_distance"]:
            key = order_by_str.split(".")[1]
            order_by_raw = RawSQL("COALESCE((payload->>%s)::int, 0)", (key,))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        elif order_by_str in [f"payload.overlap_counts.{bgdb}" for bgdb in bgdbs]:
            key1, key2 = order_by_str.split(".")[1:3]
            order_by_raw = RawSQL("(payload->%s->>%s)::int", (key1, key2))
            if order_dir == "desc":
                order_by_raw = order_by_raw.desc()
            order_by = [order_by_raw]
        else:
            order_by = order_by_str.split(",")
            if order_dir == "desc":
                order_by = [f"-{value}" for value in order_by]

        qs = SvQueryResultRow.objects.filter(
            svqueryresultset__sodar_uuid=self.kwargs.get("svqueryresultset")
        ).select_related("svqueryresultset")
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def get_permission_required(self):
        return "svs.view_data"

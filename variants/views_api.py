"""API views for ``variants`` app.

Currently, the REST API only works for the ``Case`` model.
"""
import typing

import attr
from bgjobs.models import JOB_STATE_FAILED, JOB_STATE_DONE, JOB_STATE_RUNNING, JOB_STATE_INITIAL
from django.db.models import Q
from projectroles.views_api import SODARAPIGenericProjectMixin, SODARAPIProjectPermission
from rest_framework import serializers
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning

# # TOOD: timeline update
from .models import Case, SmallVariantQuery, FilterBgJob, SmallVariant
from .serializers import (
    CaseSerializer,
    SmallVariantQuerySerializer,
    SmallVariantQueryUpdateSerializer,
    SmallVariantForResultSerializer,
)


class VariantsApiBaseMixin(SODARAPIGenericProjectMixin):
    """Mixin to enforce project-based permissions."""

    permission_classes = [SODARAPIProjectPermission]


class CaseListApiView(VariantsApiBaseMixin, ListAPIView):
    """
    List all cases in the current project.

    **URL:** ``/variants/api/case/{project.sodar_uid}/``

    **Methods:** ``GET``

    **Returns:** List of project details (see :py:class:`CaseRetrieveApiView`)
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        return "variants.view_data"


class CaseRetrieveApiView(
    VariantsApiBaseMixin, RetrieveAPIView,
):
    """
    Retrieve detail of the specified case.

    **URL:** ``/variants/api/case/{project.sodar_uuid}/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:**

    - ``date_created`` - creation timestamp (ISO 8601 ``str``)
    - ``date_modified`` - modification timestamp (ISO 8601 ``str``)
    - ``index`` - index sample name (``str``)
    - ``name`` - case name (``str``)
    - ``notes`` - any notes related to case (``str`` or ``null``)
    - ``num_small_vars`` - number of small variants (``int`` or ``null``)
    - ``num_svs`` - number of structural variants (``int`` or ``null``)
    - ``pedigree`` - ``list`` of ``dict`` representing pedigree entries, ``dict`` have keys

        - ``sex`` - PLINK-PED encoded biological sample sex (``int``, 0-unknown, 1-male, 2-female)
        - ``father`` - father sample name (``str``)
        - ``mother`` - mother sample name (``str``)
        - ``name`` - current sample's name (``str``)
        - ``affected`` - PLINK-PED encoded affected state (``int``, 0-unknown, 1-unaffected, 2-affected)
        - ``has_gt_entries`` - whether sample has genotype entries (``boolean``)

    - ``project`` - UUID of owning project (``str``)
    - ``release`` - genome build (``str``, one of ``["GRCh37", "GRCh37"]``)
    - ``sodar_uuid`` - case UUID (``str``)
    - ``status`` - status of case (``str``, one of ``"initial"``, ``"active"``, ``"closed-unsolved"``,
      ``"closed-uncertain"``, ``"closed-solved"``)
    - ``tags`` - ``list`` of ``str`` tags
    """

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"
    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project=self.get_project())

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryApiMixin(VariantsApiBaseMixin):
    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "smallvariantquery"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    serializer_class = SmallVariantQuerySerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SmallVariantQuery.objects.all()
        elif self.request.user.is_anonymous:
            return SmallVariantQuery.objects.none()
        else:
            return SmallVariantQuery.objects.filter(Q(user=self.request.user) | Q(public=True))

    def get_permission_required(self):
        return "variants.view_data"


class SmallVariantQueryApiView(SmallVariantQueryApiMixin, ListAPIView):
    """List small variant queries for the given Case.

    **URL:** ``/variants/api/query-case/list/{case.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    - ``page`` - specify page to return (default/first is ``1``)
    - ``page_size`` -- number of elements per page (default is ``10``, maximum is ``100``)

    **Returns:**

    - ``count`` - number of total elements (``int``)
    - ``next`` - URL to next page (``str`` or ``null``)
    - ``previous`` - URL to next page (``str`` or ``null``)
    - ``results`` - ``list`` of case small variant query details (see :py:class:`SmallVariantQuery`)
    """


class SmallVariantQueryCreateApiView(SmallVariantQueryApiMixin, CreateAPIView):
    """Create new small variant query for the given case.

    **URL:** ``/variants/api/query-case/create/{case.sodar_uuid}``

    **Methods:** ``POST``

    **Parameters:**

    - ``form_id``: query settings form (``str``, use ``"variants.small_variant_filter_form"``)
    - ``form_version``: query settings version (``int``, only valid: ``1``)
    - ``query_settings``: the query settings (``dict``, cf. :ref:`api_json_schemas_case_query_v1`)
    - ``name``: optional string (``str``, defaults to ``None``)
    - ``public``: whether or not this query (settings) are public (``bool``, defaults to ``False``)

    **Returns:**

    JSON serialization of case small variant query details (see :py:class:`SmallVariantQuery`)
    """

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        return result


class SmallVariantQueryRetrieveApiView(SmallVariantQueryApiMixin, RetrieveAPIView):
    """Retrieve small variant query details for the qiven query.

    **URL:** ``/variants/api/query-case/retrieve/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    None

    **Returns:**

    JSON serialization of case small variant query details (see :py:class:`SmallVariantQuery`)
    """


@attr.s(auto_attribs=True)
class JobStatus:
    status: typing.Optional[str] = None


JobStatus.INITIAL = JOB_STATE_INITIAL
JobStatus.RUNNING = JOB_STATE_RUNNING
JobStatus.DONE = JOB_STATE_DONE
JobStatus.FAILED = JOB_STATE_FAILED


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)


class SmallVariantQueryStatusApiView(SmallVariantQueryApiMixin, RetrieveAPIView):
    """Returns the status of the small variant query.

    **URL:** ``/variants/api/query-case/status/{query.sodar_uuid}``

    **Methods:** ``GET``

    **Parameters:**

    None

    **Returns:**

    ``dict`` with one key ``status`` (``str``)
    """

    serializer_class = StatusSerializer

    def get_object(self):
        query = super().get_object()
        filter_job = FilterBgJob.objects.select_related("bg_job").get(smallvariantquery=query)
        return JobStatus(status=filter_job.bg_job.status)


class SmallVariantQueryUpdateApiView(SmallVariantQueryApiMixin, UpdateAPIView):
    """Update small variant query for the qiven query.

    **URL:** ``/variants/api/query-case/update/{query.sodar_uuid}``

    **Methods:** ``PUT``, ``PATCH``

    **Parameters:**

    - ``name``: new name attribute of the query
    - ``public``: whether or not to make this query public

    **Returns:**

    JSON serialization of updated case small variant query details (see :py:class:`SmallVariantQuery`)
    """

    serializer_class = SmallVariantQueryUpdateSerializer

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result["case"] = self.get_object().case
        return result


class SmallVariantQueryFetchResultsApiView(SmallVariantQueryApiMixin, ListAPIView):
    """Fetch results for small variant query.

    Will return a HTTP 400 if the results are not ready yet.

    **URL:** ``/variants/api/query-case/results/{query.sodar_uuid}``

    **Methods:** ``GET``

    - ``page`` - specify page to return (default/first is ``1``)
    - ``page_size`` -- number of elements per page (default is ``10``, maximum is ``100``)

    **Returns:**

    - ``count`` - number of total elements (``int``)
    - ``next`` - URL to next page (``str`` or ``null``)
    - ``previous`` - URL to next page (``str`` or ``null``)
    - ``results`` - ``list`` of results (``dict``)
    """

    serializer_class = SmallVariantForResultSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query = None

    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        query = self._get_query()
        job = FilterBgJob.objects.get(smallvariantquery=query)
        if job.bg_job.status == "done":
            return result
        else:
            if job.bg_job.status == "failed":
                reason = "query failed"
            else:
                reason = "query result not available yet"
            return Response(data={"reason": reason}, status=503)

    def _get_query(self):
        if not self._query:
            if self.request.user.is_superuser:
                qs = SmallVariantQuery.objects.all()
            elif self.request.user.is_anonymous:
                qs = SmallVariantQuery.objects.none()
            else:
                qs = SmallVariantQuery.objects.filter(Q(user=self.request.user) | Q(public=True))
            self._query = get_object_or_404(qs, sodar_uuid=self.kwargs["smallvariantquery"])
        return self._query

    def get_queryset(self):
        return SmallVariant.objects.filter(smallvariantquery=self._get_query())

    def get_permission_required(self):
        return "variants.view_data"

from projectroles.views_api import (
    SODARAPIBaseMixin,
    SODARAPIBaseProjectMixin,
    SODARAPIProjectPermission,
)
from rest_framework.generics import ListAPIView, UpdateAPIView

from cases.serializers import CaseCommentSerializer, CaseGeneAnnotationSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models import Case, CaseComments, CaseGeneAnnotationEntry
from variants.serializers import CaseSerializer


class CaseListApiView(SODARAPIBaseProjectMixin, ListAPIView):
    """
    List all cases in the current project.

    **URL:** ``/cases/api/case/list/{project.sodar_uid}/``

    **Methods:** ``GET``

    **Returns:** List of project details (see :py:class:`CaseRetrieveApiView`)
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(project__sodar_uuid=self.kwargs["project"])

    def get_permission_required(self):
        return "cases.view_data"


class CasesApiPermission(SODARAPIProjectPermission):
    """Project-based permission for the ``cases`` app."""

    def get_project(self, request=None, kwargs=None):
        case = Case.objects.get(sodar_uuid=kwargs["case"])
        return case.project


class CaseApiBaseMixin(SODARAPIBaseMixin):
    """Mixin to enforce project-based permissions."""

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "case"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    permission_classes = [CasesApiPermission]

    def get_permission_required(self):
        return "cases.view_data"


class CaseUpdateApiView(CaseApiBaseMixin, UpdateAPIView):
    """
    Update a given case.

    **URL:** ``/cases/api/case/update/{case.sodar_uid}/``

    **Methods:** ``PATCH``, ``PUT``.

    **Returns:** Updated case details.
    """

    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.all()

    def get_permission_required(self):
        return "cases.update_case"


class CaseCommentApiMixin(CaseApiBaseMixin):
    serializer_class = CaseCommentSerializer

    def get_queryset(self):
        return CaseComments.objects.filter(case__sodar_uuid=self.kwargs["case"])


class CaseCommentListApiView(CaseCommentApiMixin, ListAPIView):
    """List case comments for the given case.

    **URL:** ``/cases/api/case-comment/list/{case.sodar_uuid}``

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


class CaseGeneAnnotationApiMixin(CaseApiBaseMixin):
    serializer_class = CaseGeneAnnotationSerializer

    def get_queryset(self):
        return CaseGeneAnnotationEntry.objects.filter(case__sodar_uuid=self.kwargs["case"])


class CaseGeneAnnotationListApiView(CaseGeneAnnotationApiMixin, ListAPIView):
    """List case gene annotations for the given case.

    **URL:** ``/cases/api/case-gene-annotation/list/{case.sodar_uuid}``

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

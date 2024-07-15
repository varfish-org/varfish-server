from projectroles.models import Project
from projectroles.views_api import (
    SODARAPIBaseProjectMixin,
    SODARAPIGenericProjectMixin,
    SODARAPIProjectPermission,
)
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination

from cohorts.models import Cohort, CohortCase
from cohorts.serializers import CohortCaseSerializer, CohortSerializer, ProjectCasesSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CohortPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CohortApiPermission(SODARAPIProjectPermission):
    """Fine-granular permissions for ``Cohort``."""

    def has_permission(self, request, view):
        if not request.user:
            return False  # no user, forbidden
        elif request.user.is_superuser:
            return True  # is superuser, allowed
        # Otherwise, check rules.
        if hasattr(view, "permission_required"):
            perm = view.permission_required
        else:
            perm = view.get_permission_required()
        cohort = view.get_object()
        return request.user.has_perm(perm, cohort)


class CohortCaseApiPermission(SODARAPIProjectPermission):
    """Fine-granular permissions for ``CohortCase``."""

    def has_permission(self, request, view):
        if not request.user:
            return False  # no user, forbidden
        elif request.user.is_superuser:
            return True  # is superuser, allowed
        # Otherwise, check rules.
        if hasattr(view, "permission_required"):
            perm = view.permission_required
        else:
            perm = view.get_permission_required()
        cohortcase = view.get_object()
        return request.user.has_perm(perm, cohortcase.cohort)


class AccessibleProjectsCasesApiView(SODARAPIGenericProjectMixin, ListAPIView):
    """List all accessible projects including cases for a user.

    **URL:** ``/cohorts/api/accessible-projects-cases/list/{cohort.sodar_uuid}/``

    **Methods:**: ``GET``

    **Returns:** List of project including cases.
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = ProjectCasesSerializer

    def get_queryset(self):
        # Only list projects that have at least one active variant set.
        qs = Project.objects.filter(
            type="PROJECT", case__smallvariantset__state="active"
        ).distinct()

        if not self.request.user.is_superuser:
            qs = qs.filter(roles__user=self.request.user)

        return qs.prefetch_related("case_set")

    def get_permission_required(self):
        return "cohorts.view_data"


class CohortListCreateApiView(SODARAPIGenericProjectMixin, ListCreateAPIView):
    """List cohorts of a project or create a cohort in the project.

    **URL:** ``/cohorts/api/cohort/list-create/{project.sodar_uuid}/``

    **Methods:** ``GET``, ``POST``

    **Returns:** List of cohorts
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CohortSerializer

    pagination_class = CohortPagination

    def get_queryset(self):
        qs = Cohort.objects.filter(project__sodar_uuid=self.kwargs["project"])
        if self.request.GET.get("q"):
            qs = qs.filter(name__icontains=self.request.GET.get("q"))
        return qs.select_related("project")

    def get_permission_required(self):
        if self.request.method == "POST":
            return "cohorts.create_cohort"
        else:
            return "cohorts.view_data"


class CohortRetrieveUpdateDestroyApiView(SODARAPIBaseProjectMixin, RetrieveUpdateDestroyAPIView):
    """Retrieve, update destroy a given cohort.

    **URL:** ``/cohorts/api/cohort/retrieve-update-destroy/{cohort.sodar_uuid}/``

    **Methods:** ``GET``, ``PATCH``, ``PUT``, ``DELETE``

    **Returns:** Cohort.
    """

    permission_classes = [CohortApiPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CohortSerializer

    queryset = Cohort.objects.all()

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "cohort"

    def get_permission_required(self):
        if self.request.method == "GET":
            return "cohorts.view_data"
        elif self.request.method == "DELETE":
            return "cohorts.delete_cohort"
        else:
            return "cohorts.update_cohort"


class CohortCaseCreateApiView(SODARAPIGenericProjectMixin, CreateAPIView):
    """Create cohortcase in the current project.

    **URL:** ``/cohorts/api/cohortcase/create/{project.sodar_uuid}/``

    **Methods:** ``POST``

    **Returns:** CohortCase.
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CohortCaseSerializer

    queryset = CohortCase.objects.all()

    def get_permission_required(self):
        return "cohorts.create_cohort"


class CohortCaseListApiView(SODARAPIBaseProjectMixin, ListAPIView):
    """List all cohortcase for a given cohort.

    **URL:** ``/cohorts/api/cohortcase/list/{cohort.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** List of CohortCase.
    """

    permission_classes = [SODARAPIProjectPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CohortCaseSerializer

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "cohort"

    def get_queryset(self):
        return CohortCase.objects.filter(cohort__sodar_uuid=self.kwargs["cohort"])

    def get_permission_required(self):
        return "cohorts.view_data"


class CohortCaseDestroyApiView(SODARAPIBaseProjectMixin, DestroyAPIView):
    """Destroy a given cohortcase.

    **URL:** ``/cohorts/api/cohortcase/destroy/{cohortcase.sodar_uuid}/``

    **Methods:** ``DELETE``

    **Returns:** None
    """

    permission_classes = [CohortCaseApiPermission]

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CohortCaseSerializer

    queryset = CohortCase.objects.all()

    lookup_field = "sodar_uuid"
    lookup_url_kwarg = "cohortcase"

    def get_permission_required(self):
        return "cohorts.delete_cohort"

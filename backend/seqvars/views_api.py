import sys

from django.shortcuts import get_object_or_404
from django_pydantic_field.rest_framework import AutoSchema
from projectroles.models import Project
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import viewsets
from rest_framework.pagination import CursorPagination

from seqvars.models import (
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarResultRow,
    SeqvarResultSet,
)
from seqvars.serializers import (
    SeqvarPresetsFrequencySerializer,
    SeqvarQueryExecutionSerializer,
    SeqvarQueryPresetsSetRetrieveSerializer,
    SeqvarQueryPresetsSetSerializer,
    SeqvarQuerySerializer,
    SeqvarQuerySettingsSerializer,
    SeqvarResultRowSerializer,
    SeqvarResultSetSerializer,
)


class StandardPagination(CursorPagination):
    """Standard cursor navigation for the API."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = "-date_created"


class BaseViewSet(viewsets.ModelViewSet):
    """Base view set for app."""

    #: Use canonical lookup field ``sodar_uuid``.
    lookup_field = "sodar_uuid"
    #: Use the app's standard pagination.
    pagination_class = StandardPagination
    #: Enable generation of OpenAPI schemas for pydantic field.
    schema = AutoSchema()


class ProjectContextBaseViewSet(BaseViewSet):
    """Base class for app view sets having project from URL kwarg as context."""

    def get_queryset(self):
        """Return queryset with all ``CaseAnalysis`` records for the given case.

        Currently, this will be at most one.
        """
        assert self.serializer_class
        assert self.serializer_class.Meta
        assert self.serializer_class.Meta.model

        result = self.serializer_class.Meta.model.objects.all()
        result = result.filter(project__sodar_uuid=self.kwargs["project"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the project from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["project"] = Project.objects.get(sodar_uuid=self.kwargs["project"])
        return context


class SeqvarQueryPresetsPermission(SODARAPIProjectPermission):
    """Permission class that obtains the project from the ``case`` parameter in URL."""

    def get_project(self, request=None, kwargs=None):
        _ = request
        if "project" in kwargs:  # list/create actions
            project = get_object_or_404(Project.objects.all(), sodar_uuid=kwargs["project"])
        elif "seqvarquerypresetsset" in kwargs:  # other actions
            seqvarquerypresetsset = get_object_or_404(
                SeqvarQueryPresetsSet.objects.all, sodar_uuid=kwargs["seqvarquerypresetsset"]
            )
            project = seqvarquerypresetsset.project
        else:
            raise ValueError("No project or seqvarquerypresetsset in URL kwargs")
        return project


class SeqvarQueryPresetsSetViewSet(ProjectContextBaseViewSet):
    """ViewSet for the ``SeqvarQueryPresetsSet`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarquerypresetsset"
    #: The default serializer class to use.
    serializer_class = SeqvarQueryPresetsSetSerializer
    #: Override details serializer to render all presets.
    action_serializers = {"retrieve": SeqvarQueryPresetsSetRetrieveSerializer}
    #: Use the custom permission class.
    permission_classes = [SeqvarQueryPresetsPermission]

    def get_permission_required(self):
        """Return the permission required for the current action."""
        if self.action in ("list", "retrieve"):
            return "seqvars.view_data"
        else:
            return "seqvars.update_data"


class SeqvarCategoryPresetsViewSetBase(BaseViewSet):
    """ViewSet for the ``SeqvarPresets<*>ViewSet`` models."""

    def get_queryset(self):
        """Return queryset with all ``CaseAnalysis`` records for the given case.

        Currently, this will be at most one.
        """
        assert self.serializer_class
        assert self.serializer_class.Meta
        assert self.serializer_class.Meta.model

        result = self.serializer_class.Meta.model.objects.all()
        result = result.filter(presetsset__sodar_uuid=self.kwargs["presetsset"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the project from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["presetsset"] = SeqvarQueryPresetsSet.objects.get(
            sodar_uuid=self.kwargs["presetsset"]
        )
        context["project"] = context["presetsset"].project
        return context


class SeqvarPresetsFrequencyViewSet(SeqvarCategoryPresetsViewSetBase):
    """ViewSet for the ``SeqvarPresetsFrequency`` model."""

    lookup_url_kwargs = "seqvarpresetsfrequency"
    serializer_class = SeqvarPresetsFrequencySerializer


# class SeqvarPresetsConsequenceViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsConsequenceSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class SeqvarPresetsLocusViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsLocusSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class SeqvarPresetsPhenotypePrioViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsPhenotypePrioSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class SeqvarPresetsVariantPrioViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsVariantPrioSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class SeqvarPresetsColumnsViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsColumnsSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class SeqvarPresetsMiscViewSet(viewsets.ModelViewSet):
#     serializer_class = SeqvarPresetsMiscSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


class SeqvarQuerySettingsViewSet(viewsets.ModelViewSet):
    queryset = SeqvarQuerySettings.objects.all()
    serializer_class = SeqvarQuerySettingsSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarQueryViewSet(viewsets.ModelViewSet):
    queryset = SeqvarQuery.objects.all()
    serializer_class = SeqvarQuerySerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarQueryExecutionViewSet(viewsets.ModelViewSet):
    queryset = SeqvarQueryExecution.objects.all()
    serializer_class = SeqvarQueryExecutionSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarQueryViewSet(viewsets.ModelViewSet):
    """Allow CRUD of the user's queries."""

    # TODO: permissions

    serializer_class = SeqvarQuerySerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination

    def get_queryset(self):
        """Return queryset with all ``SeqvarQuery`` records for the given case
        analysis session (must be of current user).

        Currently, this will be at most one.
        """
        result = SeqvarQuery.objects.all()
        result = result.filter(
            session__sodar_uuid=self.kwargs["caseanalysissession"],
        )
        return result


class SeqvarQueryExecutionViewSet(viewsets.ModelViewSet):
    queryset = SeqvarQueryExecution.objects.all()
    serializer_class = SeqvarQueryExecutionSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarResultSetViewSet(viewsets.ModelViewSet):
    queryset = SeqvarResultSet.objects.all()
    serializer_class = SeqvarResultSetSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarResultRowViewSet(viewsets.ModelViewSet):
    queryset = SeqvarResultRow.objects.all()
    serializer_class = SeqvarResultRowSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination

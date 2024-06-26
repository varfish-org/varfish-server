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
    SeqvarQueryPresetsSetDetailSerializer,
    SeqvarQueryPresetsSetSerializer,
    SeqvarQuerySerializer,
    SeqvarQuerySettingsDetailSerializer,
    SeqvarQuerySettingsSerializer,
    SeqvarResultRowSerializer,
    SeqvarResultSetSerializer,
)
from variants.models.case import Case


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

    def get_permission_required(self):
        """Return the permission required for the current action."""
        if self.action in ("list", "retrieve"):
            return "seqvars.view_data"
        else:
            return "seqvars.update_data"

    def get_serializer_class(self):
        """Allow overriding serializer class based on action."""
        if hasattr(self, "action_serializers"):
            return self.action_serializers.get(self.action, self.serializer_class)
        return super().get_serializer_class()


def get_project(kwargs):
    """Return the project from the URL kwargs."""
    if "project" in kwargs:  # list/create actions
        project = get_object_or_404(Project.objects.all(), sodar_uuid=kwargs["project"])
    elif "seqvarquerypresetsset" in kwargs:
        seqvarquerypresetsset = get_object_or_404(
            SeqvarQueryPresetsSet.objects.all(), sodar_uuid=kwargs["seqvarquerypresetsset"]
        )
        project = seqvarquerypresetsset.project
    elif "case" in kwargs:
        case = get_object_or_404(Case.objects.all(), sodar_uuid=kwargs["case"])
        project = case.project
    else:
        raise ValueError("No project or seqvarquerypresetsset in URL kwargs")
    return project


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
        context["project"] = get_project(self.kwargs)
        return context


class SeqvarQueryPresetsPermission(SODARAPIProjectPermission):
    """Permission class that obtains the project from the ``lookup_kwarg`` parameter in URL."""

    def get_project(self, request=None, kwargs=None):
        _ = request
        return get_project(kwargs)


class PermissionBaseViewSetBase(ProjectContextBaseViewSet):
    """Base class for ``ViewSets``s protected by permission system."""

    #: Use the custom permission class.
    permission_classes = [SeqvarQueryPresetsPermission]


class SeqvarQueryPresetsSetViewSet(PermissionBaseViewSetBase):
    """ViewSet for the ``SeqvarQueryPresetsSet`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarquerypresetsset"
    #: The default serializer class to use.
    serializer_class = SeqvarQueryPresetsSetSerializer
    #: Override ``retrieve`` serializer to render all presets.
    action_serializers = {"retrieve": SeqvarQueryPresetsSetDetailSerializer}


class SeqvarCategoryPresetsViewSetBase(PermissionBaseViewSetBase):
    """ViewSet for the ``SeqvarPresets<*>ViewSet`` models."""

    def get_queryset(self):
        """Return queryset with all ``SeqvarPresets*`` records for the given presets set."""
        assert self.serializer_class
        assert self.serializer_class.Meta
        assert self.serializer_class.Meta.model

        result = self.serializer_class.Meta.model.objects.all()
        result = result.filter(presetsset__sodar_uuid=self.kwargs["seqvarquerypresetsset"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the project from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["seqvarquerypresetsset"] = SeqvarQueryPresetsSet.objects.get(
            sodar_uuid=self.kwargs["seqvarquerypresetsset"]
        )
        context["project"] = context["seqvarquerypresetsset"].project
        return context


class SeqvarPresetsFrequencyViewSet(SeqvarCategoryPresetsViewSetBase):
    """ViewSet for the ``SeqvarPresetsFrequency`` model."""

    lookup_url_kwarg = "seqvarpresetsfrequency"
    serializer_class = SeqvarPresetsFrequencySerializer

    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


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


class SeqvarQuerySettingsViewSet(BaseViewSet):
    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarquerysettings"
    #: The default serializer class to use.
    serializer_class = SeqvarQuerySettingsSerializer
    #: Override ``create`` and ``*-detail`` serializer to render all presets.
    action_serializers = {
        "create": SeqvarQuerySettingsDetailSerializer,
        "retrieve": SeqvarQuerySettingsDetailSerializer,
        "update": SeqvarQuerySettingsDetailSerializer,
        "partial_update": SeqvarQuerySettingsDetailSerializer,
        "delete": SeqvarQuerySettingsDetailSerializer,
    }
    #: Use the custom permission class.
    permission_classes = [SeqvarQueryPresetsPermission]

    def get_queryset(self):
        """Return queryset with all ``SeqvarQuerySettings`` records for the given case."""
        result = SeqvarQuerySettings.objects.all()
        result = result.filter(case__sodar_uuid=self.kwargs["case"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the case from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["case"] = Case.objects.get(sodar_uuid=self.kwargs["case"])
        context["project"] = context["case"].project
        return context


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

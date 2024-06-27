import sys

from django.shortcuts import get_object_or_404
from django_pydantic_field.rest_framework import AutoSchema
from projectroles.models import Project
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import viewsets
from rest_framework.pagination import CursorPagination

from cases_analysis.models import CaseAnalysisSession
from seqvars.models import (
    Query,
    QueryExecution,
    QueryPresetsSet,
    QuerySettings,
    ResultRow,
    ResultSet,
)
from seqvars.serializers import (
    QueryDetailsSerializer,
    QueryExecutionDetailsSerializer,
    QueryExecutionSerializer,
    QueryPresetsFrequencySerializer,
    QueryPresetsSetDetailsSerializer,
    QueryPresetsSetSerializer,
    QuerySerializer,
    QuerySettingsDetailsSerializer,
    QuerySettingsSerializer,
    ResultRowSerializer,
    ResultSetSerializer,
)
from variants.models.case import Case


class StandardPagination(CursorPagination):
    """Standard cursor navigation for the API."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = "-date_created"


def get_project(kwargs):
    """Return the project from the URL kwargs."""
    if "project" in kwargs:  # list/create actions
        project = get_object_or_404(Project.objects.all(), sodar_uuid=kwargs["project"])
    elif "querypresetsset" in kwargs:
        querypresetsset = get_object_or_404(
            QueryPresetsSet.objects.all(), sodar_uuid=kwargs["querypresetsset"]
        )
        project = querypresetsset.project
    elif "session" in kwargs:
        session = get_object_or_404(CaseAnalysisSession.objects.all(), sodar_uuid=kwargs["session"])
        project = session.caseanalysis.case.project
    elif "query" in kwargs:
        query = get_object_or_404(Query.objects.all(), sodar_uuid=kwargs["query"])
        project = query.session.caseanalysis.case.project
    elif "resultset" in kwargs:
        resultset = get_object_or_404(ResultSet.objects.all(), sodar_uuid=kwargs["resultset"])
        project = resultset.queryexecution.query.session.caseanalysis.case.project
    elif "case" in kwargs:
        case = get_object_or_404(Case.objects.all(), sodar_uuid=kwargs["case"])
        project = case.project
    else:
        raise ValueError("No reference to project in URL kwargs")
    return project


class QueryPresetsPermission(SODARAPIProjectPermission):
    """Permission class that obtains the project from the ``lookup_kwarg`` parameter in URL."""

    def get_project(self, request=None, kwargs=None):
        _ = request
        return get_project(kwargs)


class BaseViewSetMixin:
    """Base mixin for view sets."""

    #: Use canonical lookup field ``sodar_uuid``.
    lookup_field = "sodar_uuid"
    #: Use the app's standard pagination.
    pagination_class = StandardPagination
    #: Enable generation of OpenAPI schemas for pydantic field.
    schema = AutoSchema()
    #: Use the custom permission class.
    permission_classes = [QueryPresetsPermission]

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


class BaseReadOnlyViewSet(BaseViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Base read only view sts for app."""


class BaseViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    """Base view set for app."""


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


class QueryPresetsSetViewSet(ProjectContextBaseViewSet, BaseViewSet):
    """ViewSet for the ``QueryPresetsSet`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querypresetsset"
    #: The default serializer class to use.
    serializer_class = QueryPresetsSetSerializer
    #: Override ``retrieve`` serializer to render all presets.
    action_serializers = {"retrieve": QueryPresetsSetDetailsSerializer}

    def get_queryset(self):
        """Return queryset with all ``QueryPresets`` records for the given project."""
        result = QueryPresetsSet.objects.all()
        result = result.filter(project__sodar_uuid=self.kwargs["project"])
        return result


class SeqvarCategoryPresetsViewSetBase(ProjectContextBaseViewSet, BaseViewSet):
    """ViewSet for the ``QueryPresets<*>ViewSet`` models."""

    def get_queryset(self):
        """Return queryset with all ``QueryPresets*`` records for the given presets set."""
        assert self.serializer_class
        assert self.serializer_class.Meta
        assert self.serializer_class.Meta.model

        result = self.serializer_class.Meta.model.objects.all()
        result = result.filter(presetsset__sodar_uuid=self.kwargs["querypresetsset"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the project from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["querypresetsset"] = QueryPresetsSet.objects.get(
            sodar_uuid=self.kwargs["querypresetsset"]
        )
        context["project"] = context["querypresetsset"].project
        return context


class QueryPresetsFrequencyViewSet(SeqvarCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsFrequency`` model."""

    lookup_url_kwarg = "querypresetsfrequency"
    serializer_class = QueryPresetsFrequencySerializer

    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


# class QueryPresetsConsequenceViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsConsequenceSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class QueryPresetsLocusViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsLocusSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class QueryPresetsPhenotypePrioViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsPhenotypePrioSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class QueryPresetsVariantPrioViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsVariantPrioSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class QueryPresetsColumnsViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsColumnsSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


# class QueryPresetsMiscViewSet(viewsets.ModelViewSet):
#     serializer_class = QueryPresetsMiscSerializer
#     schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
#     pagination_class = StandardPagination


class QuerySettingsViewSet(BaseViewSet):
    """ViewSet for the ``QuerySettings`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querysettings"
    #: The default serializer class to use.
    serializer_class = QuerySettingsSerializer
    #: Override ``create`` and ``*-detail`` serializer to render all presets.
    action_serializers = {
        "create": QuerySettingsDetailsSerializer,
        "retrieve": QuerySettingsDetailsSerializer,
        "update": QuerySettingsDetailsSerializer,
        "partial_update": QuerySettingsDetailsSerializer,
        "delete": QuerySettingsDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``QuerySettings`` records for the given case."""
        result = QuerySettings.objects.all()
        result = result.filter(session__sodar_uuid=self.kwargs["session"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the case from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["session"] = CaseAnalysisSession.objects.get(sodar_uuid=self.kwargs["session"])
        context["caseanalysis"] = context["session"].caseanalysis
        context["case"] = context["caseanalysis"].case
        context["project"] = context["case"].project
        return context


class QueryViewSet(BaseViewSet):
    """Allow CRUD of the user's queries."""

    # TODO XXX XXX ADD LAUNCH ACTION XXX XXX TODO

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "query"
    #: The default serializer class to use.
    serializer_class = QuerySerializer
    #: Override ``create`` and ``*-detail`` serializer to render all presets.
    action_serializers = {
        "create": QueryDetailsSerializer,
        "retrieve": QueryDetailsSerializer,
        "update": QueryDetailsSerializer,
        "partial_update": QueryDetailsSerializer,
        "delete": QueryDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``Query`` records for the given case
        analysis session (must be of current user).

        Currently, this will be at most one.
        """
        result = Query.objects.all()
        result = result.filter(
            session__sodar_uuid=self.kwargs["session"],
        )
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the case from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["session"] = CaseAnalysisSession.objects.get(sodar_uuid=self.kwargs["session"])
        context["caseanalysis"] = context["session"].caseanalysis
        context["case"] = context["caseanalysis"].case
        context["project"] = context["case"].project
        return context


class QueryExecutionViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``QueryExecution`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "queryexecution"
    #: The default serializer class to use.
    serializer_class = QueryExecutionSerializer
    #: Override ``retrieve`` serializer to render all presets.
    action_serializers = {
        "retrieve": QueryExecutionDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``QueryExecution`` records for the given query."""
        result = QueryExecution.objects.all()
        result = result.filter(
            query__sodar_uuid=self.kwargs["query"],
        )
        return result


class ResultSetViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``ResultSet`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "resultset"
    #: The default serializer class to use.
    serializer_class = ResultSetSerializer

    def get_queryset(self):
        """Return queryset with all ``ResultSet`` records for the given query."""
        result = ResultSet.objects.all()
        result = result.filter(
            queryexecution__query__sodar_uuid=self.kwargs["query"],
        )
        return result


class ResultRowPagination(StandardPagination):
    """Cursor navigation for result rows."""

    ordering = ["-chromosome_no", "start"]


class ResultRowViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``ResultRow`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarresultrow"
    #: The default serializer class to use.
    serializer_class = ResultRowSerializer
    #: Override pagination as rows do not have ``date_created``.
    pagination_class = ResultRowPagination

    def get_queryset(self):
        """Return queryset with all ``ResultRow`` records for the given result set."""
        result = ResultRow.objects.all()
        result = result.filter(
            resultset__sodar_uuid=self.kwargs["resultset"],
        )
        return result

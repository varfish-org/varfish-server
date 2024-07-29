import sys

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from modelcluster.queryset import FakeQuerySet
from projectroles.models import Project
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from cases_analysis.models import CaseAnalysisSession
from seqvars.factory_defaults import (
    create_seqvarspresetsset_short_read_exome_legacy,
    create_seqvarspresetsset_short_read_exome_modern,
    create_seqvarspresetsset_short_read_genome,
)
from seqvars.models import (
    SeqvarsQuery,
    SeqvarsQueryExecution,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQuerySettings,
    SeqvarsResultRow,
    SeqvarsResultSet,
)
from seqvars.serializers import (
    SeqvarsPredefinedQuerySerializer,
    SeqvarsQueryDetailsSerializer,
    SeqvarsQueryExecutionDetailsSerializer,
    SeqvarsQueryExecutionSerializer,
    SeqvarsQueryPresetsClinvarSerializer,
    SeqvarsQueryPresetsColumnsSerializer,
    SeqvarsQueryPresetsConsequenceSerializer,
    SeqvarsQueryPresetsFrequencySerializer,
    SeqvarsQueryPresetsLocusSerializer,
    SeqvarsQueryPresetsPhenotypePrioSerializer,
    SeqvarsQueryPresetsQualitySerializer,
    SeqvarsQueryPresetsSetCopyFromSerializer,
    SeqvarsQueryPresetsSetDetailsSerializer,
    SeqvarsQueryPresetsSetSerializer,
    SeqvarsQueryPresetsSetVersionDetailsSerializer,
    SeqvarsQueryPresetsSetVersionSerializer,
    SeqvarsQueryPresetsVariantPrioSerializer,
    SeqvarsQuerySerializer,
    SeqvarsQuerySettingsDetailsSerializer,
    SeqvarsQuerySettingsSerializer,
    SeqvarsResultRowSerializer,
    SeqvarsResultSetSerializer,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
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
    elif "querypresetssetversion" in kwargs:
        querypresetssetversion = get_object_or_404(
            SeqvarsQueryPresetsSetVersion.objects.all(), sodar_uuid=kwargs["querypresetssetversion"]
        )
        project = querypresetssetversion.presetsset.project
    elif "querypresetsset" in kwargs:
        querypresetsset = get_object_or_404(
            SeqvarsQueryPresetsSet.objects.all(), sodar_uuid=kwargs["querypresetsset"]
        )
        project = querypresetsset.project
    elif "session" in kwargs:
        session = get_object_or_404(CaseAnalysisSession.objects.all(), sodar_uuid=kwargs["session"])
        project = session.caseanalysis.case.project
    elif "query" in kwargs:
        query = get_object_or_404(SeqvarsQuery.objects.all(), sodar_uuid=kwargs["query"])
        project = query.session.caseanalysis.case.project
    elif "resultset" in kwargs:
        resultset = get_object_or_404(
            SeqvarsResultSet.objects.all(), sodar_uuid=kwargs["resultset"]
        )
        project = resultset.queryexecution.query.session.caseanalysis.case.project
    elif "case" in kwargs:
        case = get_object_or_404(Case.objects.all(), sodar_uuid=kwargs["case"])
        project = case.project
    else:
        raise ValueError("No reference to project in URL kwargs")
    return project


class SeqvarsQueryPresetsPermission(SODARAPIProjectPermission):
    """Permission class that obtains the project from the ``lookup_kwarg`` parameter in URL."""

    def get_project(self, request=None, kwargs=None):
        _ = request
        return get_project(kwargs)


class VersioningViewSetMixin:
    """Mixin for renderer and versioning."""

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning


class BaseViewSetMixin(VersioningViewSetMixin):
    """Base mixin for view sets."""

    #: Use canonical lookup field ``sodar_uuid``.
    lookup_field = "sodar_uuid"
    #: Use the app's standard pagination.
    pagination_class = StandardPagination
    #: Use the custom permission class.
    permission_classes = [SeqvarsQueryPresetsPermission]

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
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(project__sodar_uuid=self.kwargs["project"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the query preset set version from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["project"] = get_project(self.kwargs)
        return context


class SeqvarsQueryPresetsSetViewSet(ProjectContextBaseViewSet, BaseViewSet):
    """ViewSet for the ``QueryPresetsSet`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querypresetsset"
    #: The default serializer class to use.
    serializer_class = SeqvarsQueryPresetsSetSerializer

    def get_queryset(self):
        """Return queryset with all ``QueryPresetsSet`` records for the given project."""
        result = SeqvarsQueryPresetsSet.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(project__sodar_uuid=self.kwargs["project"])
        return result

    @extend_schema(request=SeqvarsQueryPresetsSetCopyFromSerializer)
    @action(methods=["post"], detail=True)
    def copy_from(self, *args, **kwargs):
        """Create a copy/clone of the given queryset."""
        source = None
        try:
            source = self.get_queryset().get(sodar_uuid=kwargs["querypresetsset"])
        except ObjectDoesNotExist:
            for value in (
                create_seqvarspresetsset_short_read_genome(),
                create_seqvarspresetsset_short_read_exome_modern(),
                create_seqvarspresetsset_short_read_exome_legacy(),
            ):
                if str(value.sodar_uuid) == kwargs["querypresetsset"]:
                    source = value
                    break

        instance = source.clone_with_latest_version(
            label=self.request.data.get("label"),
            project=get_project(self.kwargs),
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FakeQueryPresetsSetQuerySet(FakeQuerySet):
    """Helper class that fixes issue with calling ``get()`` with UUID.

    The actual implementation uses the ``python_value()`` of the query value
    but not the field.
    """

    def get(self, *args, **kwargs):
        if "sodar_uuid" in kwargs:
            filtered = [
                obj for obj in self.results if str(obj.sodar_uuid) == str(kwargs["sodar_uuid"])
            ]
            if filtered:
                return filtered[0]
            else:
                raise ObjectDoesNotExist()
        else:
            return super().get(*args, **kwargs)


class SeqvarsQueryPresetsFactoryDefaultsViewSet(
    VersioningViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """ViewSet for listing the factory defaults.

    This is a public view, no permissions are required.
    """

    #: Use canonical lookup field ``sodar_uuid``.
    lookup_field = "sodar_uuid"
    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querypresetsset"
    #: Use the app's standard pagination.
    pagination_class = StandardPagination
    #: Modify the schema operation ID to avoid name clashes with user-editable presets.
    schema = AutoSchema(
        # operation_id_base="QueryPresetsSetsFactoryDefaults"
    )

    def get_serializer_class(self):
        """Allow overriding serializer class based on action."""
        if self.action == "retrieve":
            return SeqvarsQueryPresetsSetDetailsSerializer
        else:
            return SeqvarsQueryPresetsSetSerializer

    def get_queryset(self):
        """Return queryset with all ``QueryPresetsSetVersion`` records for the given presetsset."""
        return FakeQueryPresetsSetQuerySet(
            model=SeqvarsQueryPresetsSetVersion,
            results=[
                create_seqvarspresetsset_short_read_genome(),
                create_seqvarspresetsset_short_read_exome_modern(),
                create_seqvarspresetsset_short_read_exome_legacy(),
            ],
        )


class SeqvarsQueryPresetsSetVersionViewSet(ProjectContextBaseViewSet, BaseViewSet):
    """ViewSet for the ``QueryPresetsSetVersion`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querypresetssetversion"
    #: The default serializer class to use.
    serializer_class = SeqvarsQueryPresetsSetVersionSerializer
    #: Override ``retrieve`` and ``copy_from`` serializer to render all presets.
    action_serializers = {
        "retrieve": SeqvarsQueryPresetsSetVersionDetailsSerializer,
        "copy_from": SeqvarsQueryPresetsSetVersionDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``QueryPresetsSetVersion`` records for the given presetsset."""
        result = SeqvarsQueryPresetsSetVersion.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(presetsset__sodar_uuid=self.kwargs["querypresetsset"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the query preset set from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["presetsset"] = SeqvarsQueryPresetsSet.objects.get(
            sodar_uuid=self.kwargs["querypresetsset"]
        )
        context["project"] = context["presetsset"].project
        # Set the current user from the request into the context.
        context["current_user"] = self.request.user
        return context

    @action(methods=["post"], detail=True)
    def copy_from(self, *args, **kwargs):
        """Copy from another presets set version."""
        source = self.get_queryset().get(sodar_uuid=kwargs["sodar_uuid"])
        instance = source.clone_with_presetsset(source.presetsset)
        instance.version_minor = instance.version_minor + 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SeqvarsCategoryPresetsViewSetBase(ProjectContextBaseViewSet, BaseViewSet):
    """ViewSet for the ``QueryPresets<*>ViewSet`` models."""

    def get_queryset(self):
        """Return queryset with all ``QueryPresets*`` records for the given presets set."""
        assert self.serializer_class
        assert self.serializer_class.Meta
        assert self.serializer_class.Meta.model

        result = self.serializer_class.Meta.model.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(presetssetversion__sodar_uuid=self.kwargs["querypresetssetversion"])
        return result

    def get_serializer_context(self):
        """Augment base serializer context with the query preset set version from URL kwargs."""
        context = super().get_serializer_context()
        if sys.argv[1:2] == ["generateschema"]:  # bail out for schema generation
            return context
        context["presetssetversion"] = SeqvarsQueryPresetsSetVersion.objects.get(
            sodar_uuid=self.kwargs["querypresetssetversion"]
        )
        context["presetsset"] = context["presetssetversion"].presetsset
        context["project"] = context["presetsset"].project
        return context


class SeqvarsQueryPresetsQualityViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsQuality`` model."""

    lookup_url_kwarg = "querypresetsquality"
    serializer_class = SeqvarsQueryPresetsQualitySerializer


class SeqvarsQueryPresetsConsequenceViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsConsequence`` model."""

    lookup_url_kwarg = "querypresetsconsequence"
    serializer_class = SeqvarsQueryPresetsConsequenceSerializer


class SeqvarsQueryPresetsFrequencyViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsFrequency`` model."""

    lookup_url_kwarg = "querypresetsfrequency"
    serializer_class = SeqvarsQueryPresetsFrequencySerializer


class SeqvarsQueryPresetsLocusViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsLocus`` model."""

    lookup_url_kwarg = "querypresetslocus"
    serializer_class = SeqvarsQueryPresetsLocusSerializer


class SeqvarsQueryPresetsPhenotypePrioViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsPhenotypePrio`` model."""

    lookup_url_kwarg = "querypresetsphenotypeprio"
    serializer_class = SeqvarsQueryPresetsPhenotypePrioSerializer


class SeqvarsQueryPresetsVariantPrioViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsVariantPrio`` model."""

    lookup_url_kwarg = "querypresetsvariantprio"
    serializer_class = SeqvarsQueryPresetsVariantPrioSerializer


class SeqvarsQueryPresetsColumnsViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsColumns`` model."""

    lookup_url_kwarg = "querypresetscolumns"
    serializer_class = SeqvarsQueryPresetsColumnsSerializer


class SeqvarsQueryPresetsClinvarViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``QueryPresetsClinvar`` model."""

    lookup_url_kwarg = "querypresetsclinvar"
    serializer_class = SeqvarsQueryPresetsClinvarSerializer


class SeqvarsPredefinedQueryViewSet(SeqvarsCategoryPresetsViewSetBase):
    """ViewSet for the ``PredefinedQuery`` model."""

    lookup_url_kwarg = "predefinedquery"
    serializer_class = SeqvarsPredefinedQuerySerializer


class SeqvarsQuerySettingsViewSet(BaseViewSet):
    """ViewSet for the ``QuerySettings`` model."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "querysettings"
    #: The default serializer class to use.
    serializer_class = SeqvarsQuerySettingsSerializer
    #: Override ``create`` and ``*-detail`` serializer to render all presets.
    action_serializers = {
        "create": SeqvarsQuerySettingsDetailsSerializer,
        "retrieve": SeqvarsQuerySettingsDetailsSerializer,
        "update": SeqvarsQuerySettingsDetailsSerializer,
        "partial_update": SeqvarsQuerySettingsDetailsSerializer,
        "delete": SeqvarsQuerySettingsDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``QuerySettings`` records for the given case."""
        result = SeqvarsQuerySettings.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
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


class SeqvarsQueryViewSet(BaseViewSet):
    """Allow CRUD of the user's queries."""

    # TODO XXX XXX ADD LAUNCH ACTION XXX XXX TODO

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "query"
    #: The default serializer class to use.
    serializer_class = SeqvarsQuerySerializer
    #: Override ``create`` and ``*-detail`` serializer to render all presets.
    action_serializers = {
        "create": SeqvarsQueryDetailsSerializer,
        "retrieve": SeqvarsQueryDetailsSerializer,
        "update": SeqvarsQueryDetailsSerializer,
        "partial_update": SeqvarsQueryDetailsSerializer,
        "delete": SeqvarsQueryDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``Query`` records for the given case
        analysis session (must be of current user).

        Currently, this will be at most one.
        """
        result = SeqvarsQuery.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
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


class SeqvarsQueryExecutionViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``QueryExecution`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "queryexecution"
    #: The default serializer class to use.
    serializer_class = SeqvarsQueryExecutionSerializer
    #: Override ``retrieve`` serializer to render all presets.
    action_serializers = {
        "retrieve": SeqvarsQueryExecutionDetailsSerializer,
    }

    def get_queryset(self):
        """Return queryset with all ``QueryExecution`` records for the given query."""
        result = SeqvarsQueryExecution.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(
            query__sodar_uuid=self.kwargs["query"],
        )
        return result


class SeqvarsResultSetViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``ResultSet`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "resultset"
    #: The default serializer class to use.
    serializer_class = SeqvarsResultSetSerializer

    def get_queryset(self):
        """Return queryset with all ``ResultSet`` records for the given query."""
        result = SeqvarsResultSet.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(
            queryexecution__query__sodar_uuid=self.kwargs["query"],
        )
        return result


class SeqvarsResultRowPagination(StandardPagination):
    """Cursor navigation for result rows."""

    ordering = ["-chromosome_no", "start"]


class SeqvarsResultRowViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``ResultRow`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarresultrow"
    #: The default serializer class to use.
    serializer_class = SeqvarsResultRowSerializer
    #: Override pagination as rows do not have ``date_created``.
    pagination_class = SeqvarsResultRowPagination

    def get_queryset(self):
        """Return queryset with all ``ResultRow`` records for the given result set."""
        result = SeqvarsResultRow.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(
            resultset__sodar_uuid=self.kwargs["resultset"],
        )
        return result

import sys
import typing

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from projectroles.models import Project
from projectroles.views_api import SODARAPIProjectPermission
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from cases_analysis.models import CaseAnalysisSession
from seqvars.factory_defaults import (
    create_seqvarspresetsset_short_read_exome_legacy,
    create_seqvarspresetsset_short_read_exome_modern,
    create_seqvarspresetsset_short_read_genome,
)
from seqvars.models.base import (
    SeqvarsPredefinedQuery,
    SeqvarsQuery,
    SeqvarsQueryExecution,
    SeqvarsQueryExecutionBackgroundJob,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQuerySettings,
    SeqvarsResultRow,
    SeqvarsResultSet,
)
from seqvars.serializers import (
    SeqvarsPredefinedQuerySerializer,
    SeqvarsQueryCreateFromSerializer,
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
from seqvars.tasks import run_seqvarsqueryexecutionbackgroundjob
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models.case import Case


class StandardPagination(PageNumberPagination):
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
    elif "queryexecution" in kwargs:
        queryexecution = get_object_or_404(
            SeqvarsQueryExecution.objects.all(), sodar_uuid=kwargs["queryexecution"]
        )
        project = queryexecution.query.session.caseanalysis.case.project
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
        result = result.filter(Q(project=None) | Q(project__sodar_uuid=self.kwargs["project"]))
        return result

    @extend_schema(request=SeqvarsQueryPresetsSetCopyFromSerializer)
    @action(methods=["post"], detail=True)
    def copy_from(self, *args, **kwargs):
        """Create a copy/clone of the given preset set."""
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
        source = self.get_queryset().get(sodar_uuid=kwargs["querypresetssetversion"])
        instance = source.clone_with_presetsset(presetsset=source.presetsset)
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

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "query"
    #: The default serializer class to use.
    serializer_class = SeqvarsQuerySerializer
    #: Override non-list serializers to serialize all preses.
    action_serializers = {
        "create": SeqvarsQueryDetailsSerializer,
        "retrieve": SeqvarsQueryDetailsSerializer,
        "update": SeqvarsQueryDetailsSerializer,
        "partial_update": SeqvarsQueryDetailsSerializer,
        "delete": SeqvarsQueryDetailsSerializer,
        "create_from": SeqvarsQueryDetailsSerializer,
    }

    @extend_schema(request=SeqvarsQueryCreateFromSerializer)
    @action(methods=["post"], detail=False)
    @transaction.atomic()
    def create_from(self, *args, **kwargs):
        """Create a new seqvars query from a predefined query."""
        source = None
        predefinedquery_uuid: str = self.request.data["predefinedquery"]
        label: typing.Optional[str] = self.request.data.get("label")
        try:
            # TODO: check permissions on the source's project
            source = SeqvarsPredefinedQuery.objects.get(sodar_uuid=predefinedquery_uuid)
        except ObjectDoesNotExist:
            for presetsset in (
                create_seqvarspresetsset_short_read_genome(),
                create_seqvarspresetsset_short_read_exome_modern(),
                create_seqvarspresetsset_short_read_exome_legacy(),
            ):
                for version in presetsset.versions.all():
                    for predefinedquery in version.seqvarspredefinedquery_set.all():
                        if str(predefinedquery.sodar_uuid) == predefinedquery_uuid:
                            source = predefinedquery
                            break
        if not source:
            raise ObjectDoesNotExist

        instance = SeqvarsQuery.objects.from_predefinedquery(
            session=CaseAnalysisSession.objects.get(sodar_uuid=self.kwargs["session"]),
            predefinedquery=source,
            label=label,
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
        "start": SeqvarsQueryExecutionDetailsSerializer,
    }

    @extend_schema(request=serializers.Serializer)
    @action(methods=["post"], detail=False)
    def start(self, *args, **kwargs):
        """Create a new query execution for the given query.

        Also, start the execution of a background job.
        """
        # TODO: check permissions on the source's project
        query = SeqvarsQuery.objects.get(sodar_uuid=self.kwargs["query"])
        with transaction.atomic():
            queryexecution = SeqvarsQueryExecution.objects.create(
                state=SeqvarsQueryExecution.STATE_QUEUED,
                query=query,
                querysettings=query.settings.make_clone(),
            )
            bgjob = SeqvarsQueryExecutionBackgroundJob.objects.create_full(
                seqvarsqueryexecution=queryexecution,
                user=self.request.user,
            )
        run_seqvarsqueryexecutionbackgroundjob.delay(seqvarsqueryexecutionbackgroundjob_pk=bgjob.pk)
        serializer = self.get_serializer(queryexecution)
        return Response(serializer.data)

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
            queryexecution__sodar_uuid=self.kwargs["queryexecution"],
        )
        return result


class SeqvarsResultRowPagination(StandardPagination):
    """Cursor navigation for result rows."""

    ordering = ["chrom_no", "pos"]


class SeqvarsResultRowViewSet(BaseReadOnlyViewSet):
    """ViewSet for retrieving ``ResultRow`` records."""

    #: Define lookup URL kwarg.
    lookup_url_kwarg = "seqvarresultrow"
    #: The default serializer class to use.
    serializer_class = SeqvarsResultRowSerializer
    #: Override pagination as rows do not have ``date_created``.
    pagination_class = SeqvarsResultRowPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name="order_by", type=str),
            OpenApiParameter(name="order_dir", type=str),
        ]
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        """Return queryset with all ``ResultRow`` records for the given result set."""
        result = SeqvarsResultRow.objects.all()
        if sys.argv[:2] == ["manage.py", "spectacular"]:
            return result  # short circuit in schema generation
        result = result.filter(
            resultset__sodar_uuid=self.kwargs["resultset"],
        )
        return result

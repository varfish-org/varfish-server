from django_pydantic_field.rest_framework import AutoSchema
from rest_framework.pagination import CursorPagination
from rest_framework import viewsets

from seqvars.models import (
    SeqvarPresetsColumns,
    SeqvarPresetsConsequence,
    SeqvarPresetsFrequency,
    SeqvarPresetsLocus,
    SeqvarPresetsMisc,
    SeqvarPresetsPhenotypePrio,
    SeqvarPresetsVariantPrio,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarResultRow,
    SeqvarResultSet,
)
from seqvars.serializers import (
    SeqvarPresetsColumnsSerializer,
    SeqvarPresetsConsequenceSerializer,
    SeqvarPresetsFrequencySerializer,
    SeqvarPresetsLocusSerializer,
    SeqvarPresetsMiscSerializer,
    SeqvarPresetsPhenotypePrioSerializer,
    SeqvarPresetsVariantPrioSerializer,
    SeqvarQueryExecutionSerializer,
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


class SeqvarQueryPresetsSetViewSet(viewsets.ModelViewSet):
    queryset = SeqvarQueryPresetsSet.objects.all()
    serializer_class = SeqvarQueryPresetsSetSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsFrequencyViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsFrequency.objects.all()
    serializer_class = SeqvarPresetsFrequencySerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsConsequenceViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsConsequence.objects.all()
    serializer_class = SeqvarPresetsConsequenceSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsLocusViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsLocus.objects.all()
    serializer_class = SeqvarPresetsLocusSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsPhenotypePrioViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsPhenotypePrio.objects.all()
    serializer_class = SeqvarPresetsPhenotypePrioSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsVariantPrioViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsVariantPrio.objects.all()
    serializer_class = SeqvarPresetsVariantPrioSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsColumnsViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsColumns.objects.all()
    serializer_class = SeqvarPresetsColumnsSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


class SeqvarPresetsMiscViewSet(viewsets.ModelViewSet):
    queryset = SeqvarPresetsMisc.objects.all()
    serializer_class = SeqvarPresetsMiscSerializer
    schema = AutoSchema()  # OpenAPI schema generation for pydantic fields
    pagination_class = StandardPagination


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

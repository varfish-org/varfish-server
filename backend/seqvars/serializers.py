from django_pydantic_field.rest_framework import SchemaField
from rest_framework import generics, serializers

from seqvars.models import (
    DataSourceInfos,
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
    SeqvarResultRowPayload,
    SeqvarResultSet,
)


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer for models with sodar_uuid and creation/update time."""

    class Meta:
        fields = [
            "sodar_uuid",
            "date_created",
            "date_modified",
        ]


class SeqvarQueryPresetsSetSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQueryPresetsSet``."""

    #: Serializer ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    class Meta:
        model = SeqvarQueryPresetsSet
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "title",
            "description",
            "project",
        ]
        read_only_fields = fields


class SeqvarPresetsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsBase``.

    Not used directly but as a base class for ``SeqvarPreset*Serializer``.
    """

    class Meta:
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "title",
            "description",
        ]
        read_only_fields = fields


class SeqvarPresetsFrequencySerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsFrequency``."""

    class Meta:
        model = SeqvarPresetsFrequency
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsConsequenceSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsConsequence``."""

    class Meta:
        model = SeqvarPresetsConsequence
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsLocusSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsLocus``."""

    class Meta:
        model = SeqvarPresetsLocus
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsPhenotypePrioSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsPhenotypePrio``."""

    class Meta:
        model = SeqvarPresetsPhenotypePrio
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsVariantPrioSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsVariantPrio``."""

    class Meta:
        model = SeqvarPresetsVariantPrio
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsColumnsSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsColumns``."""

    class Meta:
        model = SeqvarPresetsColumns
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarPresetsMiscSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsMisc``."""

    class Meta:
        model = SeqvarPresetsMisc
        fields = SeqvarPresetsBaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarQuerySettingsSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQuerySettings``."""

    class Meta:
        model = SeqvarQuerySettings
        fields = BaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarQuerySerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQuery``."""

    rank = serializers.IntegerField(default=1, initial=1)
    title = serializers.CharField(max_length=128)

    #: Serializer ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serializer ``settings_buffer`` as its ``sodar_uuid``.
    settings_buffer = serializers.ReadOnlyField(source="settings_buffer.sodar_uuid")

    class Meta:
        model = SeqvarQuery
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "title",
            "session",
            "settings_buffer",
        ]
        read_only_fields = fields


class SeqvarQueryExecutionSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQueryExecution``."""

    #: Serialize ``query`` as its ``sodar_uuid``.
    query = serializers.ReadOnlyField(source="query.sodar_uuid")
    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    class Meta:
        model = SeqvarQueryExecution
        fields = BaseSerializer.Meta.fields + [
            "state",
            "complete_percent",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "query",
            "querysettings",
        ]
        read_only_fields = fields


class SeqvarResultSetSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarResultSet``."""

    #: Serialize ``queryexecution`` as its ``sodar_uuid``.
    queryexecution = serializers.ReadOnlyField(source="queryexecution.sodar_uuid")
    #: Explicitely provide django-pydantic-field schema for ``datasource_infos``.
    datasource_infos = SchemaField(schema=DataSourceInfos)

    class Meta:
        model = SeqvarResultSet
        fields = BaseSerializer.Meta.fields + [
            "queryexecution",
            "datasource_infos",
        ]
        read_only_fields = fields


class SeqvarResultRowSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarResultRow``."""

    #: Serialize ``resultset`` as its ``sodar_uuid``.
    resultset = serializers.ReadOnlyField(source="resultset.sodar_uuid")
    #: Explicitely provide django-pydantic-field schema for ``payload``.
    payload = SchemaField(schema=SeqvarResultRowPayload)

    class Meta:
        model = SeqvarResultRow
        fields = [
            "sodar_uuid",
            "resultset",
            "release",
            "chromosome",
            "chromosome_no",
            "start",
            "stop",
            "reference",
            "alternative",
            "payload",
        ]
        read_only_fields = fields

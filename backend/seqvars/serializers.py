from django_pydantic_field.rest_framework import SchemaField
from rest_framework import generics, serializers

from seqvars.models import (
    DataSourceInfos,
    SeqvarPresetsFrequency,
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


class LabeledSortableBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``LabeledSortableBase``."""

    #: Rank for sorting.
    rank = serializers.IntegerField(default=1, initial=1)
    #: A text label.
    label = serializers.CharField(max_length=128)
    #: An optional description.
    description = serializers.CharField(allow_null=True)

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the project from context."""
        if "project" in self.context:
            attrs["project"] = self.context["project"]
        return attrs

    class Meta:
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "label",
            "description",
        ]
        read_only_fields = fields


class SeqvarPresetsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarPresetsBase``.

    Not used directly but as a base class for ``SeqvarPreset*Serializer``.
    """

    #: Rank for sorting.
    rank = serializers.IntegerField(default=1, initial=1)
    #: A text label.
    label = serializers.CharField(max_length=128)
    #: An optional description.
    description = serializers.CharField(allow_null=True)

    #: Serialize ``presetsset`` as its ``sodar_uuid``.
    presetsset = serializers.ReadOnlyField(source="presetsset.sodar_uuid")

    class Meta:
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "label",
            "description",
        ]
        read_only_fields = fields


class SeqvarPresetsFrequencySerializer(SeqvarPresetsBaseSerializer):
    """Serializer for ``SeqvarPresetsFrequency``."""

    gnomad_exomes_enabled = serializers.BooleanField()
    gnomad_exomes_frequency = serializers.FloatField(allow_null=True)
    gnomad_exomes_homozygous = serializers.IntegerField(allow_null=True)
    gnomad_exomes_heterozygous = serializers.IntegerField(allow_null=True)
    gnomad_exomes_hemizygous = serializers.BooleanField(allow_null=True)

    gnomad_genomes_enabled = serializers.BooleanField()
    gnomad_genomes_frequency = serializers.FloatField(allow_null=True)
    gnomad_genomes_homozygous = serializers.IntegerField(allow_null=True)
    gnomad_genomes_heterozygous = serializers.IntegerField(allow_null=True)
    gnomad_genomes_hemizygous = serializers.BooleanField(allow_null=True)

    helixmtdb_enabled = serializers.BooleanField()
    helixmtdb_heteroplasmic = serializers.IntegerField(allow_null=True)
    helixmtdb_homoplasmic = serializers.IntegerField(allow_null=True)
    helixmtdb_frequency = serializers.FloatField(allow_null=True)

    inhouse_enabled = serializers.BooleanField()
    inhouse_carriers = serializers.IntegerField(allow_null=True)
    inhouse_homozygous = serializers.IntegerField(allow_null=True)
    inhouse_heterozygous = serializers.IntegerField(allow_null=True)
    inhouse_hemizygous = serializers.IntegerField(allow_null=True)

    class Meta:
        model = SeqvarPresetsFrequency
        fields = SeqvarPresetsBaseSerializer.Meta.fields + [
            "gnomad_exomes_enabled",
            "gnomad_exomes_frequency",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_enabled",
            "gnomad_genomes_frequency",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "helixmtdb_enabled",
            "helixmtdb_heteroplasmic",
            "helixmtdb_homoplasmic",
            "helixmtdb_frequency",
            "inhouse_enabled",
            "inhouse_carriers",
            "inhouse_homozygous",
            "inhouse_heterozygous",
            "inhouse_hemizygous",
        ]
        read_only_fields = fields


class SeqvarQuerySettingsSerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQuerySettings``."""

    class Meta:
        model = SeqvarQuerySettings
        fields = BaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarQuerySettingsFrequencySerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQuerySettings``."""

    class Meta:
        model = SeqvarQuerySettings
        fields = BaseSerializer.Meta.fields + []
        read_only_fields = fields


class SeqvarQueryPresetsSetSerializer(LabeledSortableBaseSerializer):
    """Serializer for ``SeqvarQueryPresetsSet``."""

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    class Meta:
        model = SeqvarQueryPresetsSet
        fields = LabeledSortableBaseSerializer.Meta.fields + [
            "rank",
            "label",
            "description",
            "project",
        ]
        read_only_fields = fields


class SeqvarQueryPresetsSetRetrieveSerializer(SeqvarQueryPresetsSetSerializer):
    """Serializer for ``SeqvarQueryPresetsSet`` (retrieve only).

    When retrieving the details of a seqvar query preset set, we also render the
    owned records.
    """

    #: Serialize all frequency presets.
    seqvarpresetsfrequency_set = SeqvarPresetsFrequencySerializer(many=True)

    class Meta:
        model = SeqvarQueryPresetsSet
        fields = SeqvarQueryPresetsSetSerializer.Meta.fields + [
            "rank",
            "label",
            "description",
            "project",
        ]
        read_only_fields = fields


class SeqvarQuerySerializer(serializers.ModelSerializer):
    """Serializer for ``SeqvarQuery``."""

    rank = serializers.IntegerField(default=1, initial=1)
    label = serializers.CharField(max_length=128)

    #: Serializer ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serializer ``settings_buffer`` as its ``sodar_uuid``.
    settings_buffer = serializers.ReadOnlyField(source="settings_buffer.sodar_uuid")

    class Meta:
        model = SeqvarQuery
        fields = BaseSerializer.Meta.fields + [
            "rank",
            "label",
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

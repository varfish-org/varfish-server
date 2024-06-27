from django_pydantic_field.rest_framework import SchemaField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from seqvars.models import (
    DataSourceInfos,
    FrequencySettingsBase,
    Query,
    QueryExecution,
    QueryPresetsFrequency,
    QueryPresetsSet,
    QuerySettings,
    QuerySettingsCategoryBase,
    QuerySettingsFrequency,
    ResultRow,
    ResultRowPayload,
    ResultSet,
    SampleGenotypeChoice,
)


class SampleGenotypeSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``SampleGenotypeSettingsBase``.

    Not used directly but uased as base class.
    """

    sample_genotypes = SchemaField(schema=list[SampleGenotypeChoice])

    class Meta:
        model = FrequencySettingsBase
        fields = [
            "sample_genotypes",
        ]


class FrequencySettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``FrequencySettingsBase``.

    Not used directly but uased as base class.
    """

    gnomad_exomes_enabled = serializers.BooleanField(required=False, default=False)
    gnomad_exomes_frequency = serializers.FloatField(required=False, allow_null=True, default=None)
    gnomad_exomes_homozygous = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    gnomad_exomes_heterozygous = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    gnomad_exomes_hemizygous = serializers.BooleanField(
        required=False, allow_null=True, default=None
    )

    gnomad_genomes_enabled = serializers.BooleanField(required=False, default=False)
    gnomad_genomes_frequency = serializers.FloatField(required=False, allow_null=True, default=None)
    gnomad_genomes_homozygous = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    gnomad_genomes_heterozygous = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    gnomad_genomes_hemizygous = serializers.BooleanField(
        required=False, allow_null=True, default=None
    )

    helixmtdb_enabled = serializers.BooleanField(required=False, default=False)
    helixmtdb_heteroplasmic = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    helixmtdb_homoplasmic = serializers.IntegerField(required=False, allow_null=True, default=None)
    helixmtdb_frequency = serializers.FloatField(required=False, allow_null=True, default=None)

    inhouse_enabled = serializers.BooleanField(required=False, default=False)
    inhouse_carriers = serializers.IntegerField(required=False, allow_null=True, default=None)
    inhouse_homozygous = serializers.IntegerField(required=False, allow_null=True, default=None)
    inhouse_heterozygous = serializers.IntegerField(required=False, allow_null=True, default=None)
    inhouse_hemizygous = serializers.IntegerField(required=False, allow_null=True, default=None)

    class Meta:
        model = FrequencySettingsBase
        fields = [
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


class BaseModelSerializer(serializers.ModelSerializer):
    """Base serializer for models with sodar_uuid and creation/update time.

    Not used directly but used as a base class.
    """

    sodar_uuid = serializers.UUIDField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    date_modified = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = [
            "sodar_uuid",
            "date_created",
            "date_modified",
        ]


class LabeledSortableBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``LabeledSortableBase``.

    Not used directly but used as a base class.
    """

    rank = serializers.IntegerField(default=1, initial=1)
    label = serializers.CharField(max_length=128)
    description = serializers.CharField(allow_null=True, default=None)

    class Meta:
        fields = BaseModelSerializer.Meta.fields + [
            "rank",
            "label",
            "description",
        ]
        read_only_fields = fields


class QueryPresetsBaseSerializer(LabeledSortableBaseSerializer):
    """Serializer for ``QueryPresetsBase``.

    Not used directly but as a base class.
    """

    #: Serialize ``presetsset`` as its ``sodar_uuid``.
    presetsset = serializers.ReadOnlyField(source="presetsset.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the presets set object from context."""
        if "querypresetsset" in self.context:
            attrs["presetsset"] = self.context["querypresetsset"]
        return attrs

    class Meta:
        fields = LabeledSortableBaseSerializer.Meta.fields + [
            "presetsset",
        ]
        read_only_fields = fields


class QueryPresetsFrequencySerializer(FrequencySettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsFrequency``.

    Not used directly but uased as base class.
    """

    class Meta:
        model = QueryPresetsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QueryPresetsSetSerializer(LabeledSortableBaseSerializer):
    """Serializer for ``QueryPresetsSet``."""

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the project from context."""
        if "project" in self.context:
            attrs["project"] = self.context["project"]
        return attrs

    class Meta:
        model = QueryPresetsSet
        fields = LabeledSortableBaseSerializer.Meta.fields + [
            "project",
        ]
        read_only_fields = fields


class QueryPresetsSetDetailsSerializer(QueryPresetsSetSerializer):
    """Serializer for ``QueryPresetsSet`` (for ``*-detail``).

    When retrieving the details of a seqvar query preset set, we also render the
    owned records.
    """

    #: Serialize all frequency presets.
    querypresetsfrequency_set = QueryPresetsFrequencySerializer(many=True, read_only=True)

    class Meta:
        model = QueryPresetsSetSerializer.Meta.model
        fields = QueryPresetsSetSerializer.Meta.fields + [
            "querypresetsfrequency_set",
        ]
        read_only_fields = fields


class QuerySettingsBaseSerializer(BaseModelSerializer):
    """Serializer for ``QuerySettings``."""

    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the query settings object from context."""
        if "querysettings" in self.context:
            attrs["querysettings"] = self.context["querysettings"]
        return attrs

    class Meta:
        model = QuerySettingsCategoryBase
        fields = BaseModelSerializer.Meta.fields + ["querysettings"]
        read_only_fields = fields


class QuerySettingsFrequencySerializer(
    FrequencySettingsBaseSerializer, QuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettings``."""

    class Meta:
        model = QuerySettingsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QuerySettingsSerializer(BaseModelSerializer):
    """Serializer for ``QuerySettings``."""

    #: Serialize ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serialize ``querysettingsfrequency`` as its ``sodar_uuid``.
    querysettingsfrequency = serializers.ReadOnlyField(source="querysettingsfrequency.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "session" in self.context:
            attrs["session"] = self.context["session"]
        return attrs

    class Meta:
        model = QuerySettings
        fields = BaseModelSerializer.Meta.fields + ["session", "querysettingsfrequency"]
        read_only_fields = fields


class QuerySettingsDetailsSerializer(QuerySettingsSerializer, WritableNestedModelSerializer):
    """Serializer for ``QuerySettings`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested
    frequency settings.
    """

    #: Nested serialization of the frequency settings.
    querysettingsfrequency = QuerySettingsFrequencySerializer()

    class Meta:
        model = QuerySettingsSerializer.Meta.model
        fields = QuerySettingsSerializer.Meta.fields + [
            "querysettingsfrequency",
        ]
        read_only_fields = fields


class QuerySerializer(BaseModelSerializer):
    """Serializer for ``Query``."""

    rank = serializers.IntegerField(default=1, initial=1)
    label = serializers.CharField(max_length=128)

    #: Serializer ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serializer ``settings_buffer`` as its ``sodar_uuid``.
    settings_buffer = serializers.ReadOnlyField(source="settings_buffer.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "session" in self.context:
            attrs["session"] = self.context["session"]
        return attrs

    class Meta:
        model = Query
        fields = BaseModelSerializer.Meta.fields + [
            "rank",
            "label",
            "session",
            "settings_buffer",
        ]
        read_only_fields = fields


class QueryDetailsSerializer(QuerySerializer, WritableNestedModelSerializer):
    """Serializer for ``Query`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested query settings
    in detail.
    """

    #: For the details serializer, we use a nested details serializer.
    settings_buffer = QuerySettingsDetailsSerializer()

    class Meta:
        model = Query
        fields = QuerySerializer.Meta.fields
        read_only_fields = fields


class QueryExecutionSerializer(BaseModelSerializer):
    """Serializer for ``QueryExecution``."""

    #: Serialize ``query`` as its ``sodar_uuid``.
    query = serializers.ReadOnlyField(source="query.sodar_uuid")
    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    class Meta:
        model = QueryExecution
        fields = BaseModelSerializer.Meta.fields + [
            "state",
            "complete_percent",
            "start_time",
            "end_time",
            "elapsed_seconds",
            "query",
            "querysettings",
        ]
        read_only_fields = fields


class QueryExecutionDetailsSerializer(QueryExecutionSerializer):
    """Serializer for ``QueryExecution``."""

    #: For the details, serialize ``querysettings`` fully.
    querysettings = QuerySettingsDetailsSerializer()

    class Meta:
        model = QueryExecution
        fields = QueryExecutionSerializer.Meta.fields
        read_only_fields = fields


class ResultSetSerializer(BaseModelSerializer):
    """Serializer for ``ResultSet``."""

    #: Explicitely provide django-pydantic-field schema for ``datasource_infos``.
    datasource_infos = SchemaField(schema=DataSourceInfos)
    #: Serialize ``queryexecution`` as its ``sodar_uuid``.
    queryexecution = serializers.ReadOnlyField(source="queryexecution.sodar_uuid")

    class Meta:
        model = ResultSet
        fields = BaseModelSerializer.Meta.fields + [
            "queryexecution",
            "datasource_infos",
        ]
        read_only_fields = fields


class ResultRowSerializer(serializers.ModelSerializer):
    """Serializer for ``ResultRow``."""

    #: Serialize ``resultset`` as its ``sodar_uuid``.
    resultset = serializers.ReadOnlyField(source="resultset.sodar_uuid")
    #: Explicitely provide django-pydantic-field schema for ``payload``.
    payload = SchemaField(schema=ResultRowPayload)

    class Meta:
        model = ResultRow
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

from django_pydantic_field.rest_framework import SchemaField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from seqvars.models import (
    DataSourceInfos,
    FrequencySettingsBase,
    SampleGenotypeChoice,
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarQuerySettingsCategoryBase,
    SeqvarQuerySettingsFrequency,
    SeqvarResultRow,
    SeqvarResultRowPayload,
    SeqvarResultSet,
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


class SeqvarPresetsBaseSerializer(LabeledSortableBaseSerializer):
    """Serializer for ``SeqvarPresetsBase``.

    Not used directly but as a base class.
    """

    #: Serialize ``presetsset`` as its ``sodar_uuid``.
    presetsset = serializers.ReadOnlyField(source="presetsset.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the presets set object from context."""
        if "seqvarquerypresetsset" in self.context:
            attrs["presetsset"] = self.context["seqvarquerypresetsset"]
        return attrs

    class Meta:
        fields = LabeledSortableBaseSerializer.Meta.fields + [
            "presetsset",
        ]
        read_only_fields = fields


class SeqvarPresetsFrequencySerializer(
    FrequencySettingsBaseSerializer, SeqvarPresetsBaseSerializer
):
    """Serializer for ``SeqvarPresetsFrequency``.

    Not used directly but uased as base class.
    """

    class Meta:
        model = SeqvarPresetsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + SeqvarPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarQueryPresetsSetSerializer(LabeledSortableBaseSerializer):
    """Serializer for ``SeqvarQueryPresetsSet``."""

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the project from context."""
        if "project" in self.context:
            attrs["project"] = self.context["project"]
        return attrs

    class Meta:
        model = SeqvarQueryPresetsSet
        fields = LabeledSortableBaseSerializer.Meta.fields + [
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
            "seqvarpresetsfrequency_set",
        ]
        read_only_fields = fields


class SeqvarQuerySettingsBaseSerializer(BaseModelSerializer):
    """Serializer for ``SeqvarQuerySettings``."""

    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the query settings object from context."""
        if "querysettings" in self.context:
            attrs["querysettings"] = self.context["querysettings"]
        return attrs

    class Meta:
        model = SeqvarQuerySettingsCategoryBase
        fields = BaseModelSerializer.Meta.fields + ["querysettings"]
        read_only_fields = fields


class SeqvarQuerySettingsFrequencySerializer(
    FrequencySettingsBaseSerializer, SeqvarQuerySettingsBaseSerializer
):
    """Serializer for ``SeqvarQuerySettings``."""

    class Meta:
        model = SeqvarQuerySettingsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields
            + SeqvarQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarQuerySettingsSerializer(BaseModelSerializer, WritableNestedModelSerializer):
    """Serializer for ``SeqvarQuerySettings``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    #: Nested serialization of the frequency settings.
    seqvarquerysettingsfrequency = SeqvarQuerySettingsFrequencySerializer()

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "case" in self.context:
            attrs["case"] = self.context["case"]
        return attrs

    class Meta:
        model = SeqvarQuerySettings
        fields = BaseModelSerializer.Meta.fields + ["case", "seqvarquerysettingsfrequency"]
        read_only_fields = fields


class SeqvarQuerySerializer(BaseModelSerializer):
    """Serializer for ``SeqvarQuery``."""

    rank = serializers.IntegerField(default=1, initial=1)
    label = serializers.CharField(max_length=128)

    #: Serializer ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serializer ``settings_buffer`` as its ``sodar_uuid``.
    settings_buffer = serializers.ReadOnlyField(source="settings_buffer.sodar_uuid")

    class Meta:
        model = SeqvarQuery
        fields = BaseModelSerializer.Meta.fields + [
            "rank",
            "label",
            "session",
            "settings_buffer",
        ]
        read_only_fields = fields


class SeqvarQueryExecutionSerializer(BaseModelSerializer):
    """Serializer for ``SeqvarQueryExecution``."""

    #: Serialize ``query`` as its ``sodar_uuid``.
    query = serializers.ReadOnlyField(source="query.sodar_uuid")
    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    class Meta:
        model = SeqvarQueryExecution
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


class SeqvarResultSetSerializer(BaseModelSerializer):
    """Serializer for ``SeqvarResultSet``."""

    #: Explicitely provide django-pydantic-field schema for ``datasource_infos``.
    datasource_infos = SchemaField(schema=DataSourceInfos)
    #: Serialize ``queryexecution`` as its ``sodar_uuid``.
    queryexecution = serializers.ReadOnlyField(source="queryexecution.sodar_uuid")

    class Meta:
        model = SeqvarResultSet
        fields = BaseModelSerializer.Meta.fields + [
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

from django_pydantic_field.rest_framework import SchemaField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from seqvars.models import (
    ClinvarGermlineAggregateDescription,
    ClinvarSettingsBase,
    ColumnConfig,
    ColumnsSettingsBase,
    ConsequenceSettingsBase,
    DataSourceInfos,
    FrequencySettingsBase,
    Gene,
    GenePanel,
    GenomeRegion,
    LocusSettingsBase,
    PhenotypePrioSettingsBase,
    Query,
    QueryColumnsConfig,
    QueryExecution,
    QueryPresetsClinvar,
    QueryPresetsColumns,
    QueryPresetsConsequence,
    QueryPresetsFrequency,
    QueryPresetsLocus,
    QueryPresetsPhenotypePrio,
    QueryPresetsQuality,
    QueryPresetsSet,
    QueryPresetsVariantPrio,
    QuerySettings,
    QuerySettingsCategoryBase,
    QuerySettingsClinvar,
    QuerySettingsConsequence,
    QuerySettingsFrequency,
    QuerySettingsGenotype,
    QuerySettingsLocus,
    QuerySettingsPhenotypePrio,
    QuerySettingsQuality,
    QuerySettingsVariantPrio,
    ResultRow,
    ResultRowPayload,
    ResultSet,
    SampleGenotypeChoice,
    SampleQualityFilter,
    TermPresence,
    TranscriptTypeChoice,
    VariantConsequenceChoice,
    VariantPrioService,
    VariantPrioSettingsBase,
    VariantTypeChoice,
)


class FrequencySettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``FrequencySettingsBase``.

    Not used directly but used as base class.
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


class ConsequenceSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``ConsequenceSettingsBase``.

    Not used directly but used as base class.
    """

    variant_types = SchemaField(schema=list[VariantTypeChoice], default=list)
    transcript_types = SchemaField(schema=list[TranscriptTypeChoice], default=list)
    variant_consequences = SchemaField(schema=list[VariantConsequenceChoice], default=list)
    max_distance_to_exon = serializers.IntegerField(required=False, allow_null=True, default=None)

    class Meta:
        model = ConsequenceSettingsBase
        fields = [
            "variant_types",
            "transcript_types",
            "variant_consequences",
            "max_distance_to_exon",
        ]


class LocusSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``LocusSettingsBase``.

    Not used directly but used as base class.
    """

    genes = SchemaField(schema=list[Gene], default=list)
    gene_panels = SchemaField(schema=list[GenePanel], default=list)
    genome_regions = SchemaField(schema=list[GenomeRegion], default=list)

    class Meta:
        model = LocusSettingsBase
        fields = [
            "genes",
            "gene_panels",
            "genome_regions",
        ]


class PhenotypePrioSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``PhenotypePrioSettingsBase``.

    Not used directly but used as base class.
    """

    phenotype_prio_enabled = serializers.BooleanField(default=False, allow_null=False)
    phenotype_prio_algorithm = serializers.CharField(
        max_length=128, allow_null=True, required=False
    )
    terms = SchemaField(schema=list[TermPresence], default=list)

    class Meta:
        model = PhenotypePrioSettingsBase
        fields = [
            "phenotype_prio_enabled",
            "phenotype_prio_algorithm",
            "terms",
        ]


class VariantPrioSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``VariantPrioSettingsBase``.

    Not used directly but used as base class.
    """

    variant_prio_enabled = serializers.BooleanField(default=False, allow_null=False)
    services = SchemaField(schema=list[VariantPrioService], default=list)

    class Meta:
        model = VariantPrioSettingsBase
        fields = [
            "variant_prio_enabled",
            "services",
        ]


class ClinvarSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``ClinvarSettingsBase``.

    Not used directly but used as base class.
    """

    clinvar_presence_required = serializers.BooleanField(default=False, allow_null=False)
    clinvar_germline_aggregate_description = SchemaField(
        schema=list[ClinvarGermlineAggregateDescription], default=list
    )
    allow_conflicting_interpretations = serializers.BooleanField(default=False, allow_null=False)
    include_legacy_descriptions = serializers.BooleanField(default=False, allow_null=False)

    class Meta:
        model = ClinvarSettingsBase
        fields = [
            "clinvar_presence_required",
            "clinvar_germline_aggregate_description",
            "allow_conflicting_interpretations",
            "include_legacy_descriptions",
        ]


class ColumnsSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``ColumnsSettingsBase``.

    Not used directly but used as base class.
    """

    column_settings = SchemaField(schema=list[ColumnConfig], default=list)

    class Meta:
        model = ColumnsSettingsBase
        fields = [
            "column_settings",
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


class QueryPresetsQualitySerializer(QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsQuality``.

    Not used directly but used as base class.
    """

    #: Minimal depth for het. variants.
    min_dp_het = serializers.IntegerField(allow_null=True, required=False)
    #: Minimal depth for hom. variants.
    min_dp_hom = serializers.IntegerField(allow_null=True, required=False)
    #: Minimal allele balance for het. variants.
    min_ab_het = serializers.FloatField(allow_null=True, required=False)
    #: Minimal genotype quality.
    min_gq = serializers.IntegerField(allow_null=True, required=False)
    #: Minimal alternate allele read depth.
    min_ad = serializers.IntegerField(allow_null=True, required=False)
    #: Maximal alternate allele read depth.
    max_ad = serializers.IntegerField(allow_null=True, required=False)
    #: Behaviour for failing filter.
    on_failure = serializers.CharField(
        max_length=128, default=QueryPresetsQuality.ON_FAILURE_DROP_VARIANT, required=False
    )

    class Meta:
        model = QueryPresetsQuality
        fields = QueryPresetsBaseSerializer.Meta.fields + [
            "min_dp_het",
            "min_dp_hom",
            "min_ab_het",
            "min_gq",
            "min_ad",
            "max_ad",
            "on_failure",
        ]
        read_only_fields = fields


class QueryPresetsFrequencySerializer(FrequencySettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsFrequency``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QueryPresetsConsequenceSerializer(
    ConsequenceSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsConsequence``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsConsequence
        fields = (
            ConsequenceSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QueryPresetsLocusSerializer(LocusSettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsLocus``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsLocus
        fields = LocusSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        read_only_fields = fields


class QueryPresetsPhenotypePrioSerializer(
    PhenotypePrioSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsPhenotypePrio``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsPhenotypePrio
        fields = (
            PhenotypePrioSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QueryPresetsVariantPrioSerializer(
    VariantPrioSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsVariantPrio``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsVariantPrio
        fields = (
            VariantPrioSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QueryPresetsClinvarSerializer(ClinvarSettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsClinvar``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsClinvar
        fields = ClinvarSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        read_only_fields = fields


class QueryPresetsColumnsSerializer(ColumnsSettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsColumns``.

    Not used directly but used as base class.
    """

    class Meta:
        model = QueryPresetsColumns
        fields = ColumnsSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
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


class QuerySettingsGenotypeSerializer(QuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsGenotype``."""

    sample_genotype_choices = SchemaField(schema=list[SampleGenotypeChoice], default=list)

    class Meta:
        model = QuerySettingsGenotype
        fields = QuerySettingsBaseSerializer.Meta.fields + ["sample_genotype_choices"]
        read_only_fields = fields


class QuerySettingsQualitySerializer(QuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsQuality``."""

    sample_quality_filters = SchemaField(schema=list[SampleQualityFilter], default=list)

    class Meta:
        model = QuerySettingsQuality
        fields = QuerySettingsBaseSerializer.Meta.fields + ["sample_quality_filters"]
        read_only_fields = fields


class QuerySettingsConsequenceSerializer(
    ConsequenceSettingsBaseSerializer, QuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsConsequence``."""

    class Meta:
        model = QuerySettingsConsequence
        fields = (
            ConsequenceSettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QuerySettingsLocusSerializer(LocusSettingsBaseSerializer, QuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsLocus``."""

    class Meta:
        model = QuerySettingsLocus
        fields = LocusSettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        read_only_fields = fields


class QuerySettingsFrequencySerializer(
    FrequencySettingsBaseSerializer, QuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsFrequency``."""

    class Meta:
        model = QuerySettingsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QuerySettingsPhenotypePrioSerializer(
    PhenotypePrioSettingsBaseSerializer, QuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsPhenotypePrio``."""

    class Meta:
        model = QuerySettingsPhenotypePrio
        fields = (
            PhenotypePrioSettingsBaseSerializer.Meta.fields
            + QuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QuerySettingsVariantPrioSerializer(
    VariantPrioSettingsBaseSerializer, QuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsVariantPrio``."""

    class Meta:
        model = QuerySettingsVariantPrio
        fields = (
            VariantPrioSettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class QuerySettingsClinvarSerializer(ClinvarSettingsBaseSerializer, QuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsClinvar``."""

    class Meta:
        model = QuerySettingsClinvar
        fields = ClinvarSettingsBaseSerializer.Meta.fields + QuerySettingsBaseSerializer.Meta.fields
        read_only_fields = fields


class QuerySettingsSerializer(BaseModelSerializer):
    """Serializer for ``QuerySettings``."""

    #: Serialize ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serialize ``genotype`` as its ``sodar_uuid``.
    genotype = serializers.ReadOnlyField(source="genotype.sodar_uuid")
    #: Serialize ``quality`` as its ``sodar_uuid``.
    quality = serializers.ReadOnlyField(source="quality.sodar_uuid")
    #: Serialize ``consequence`` as its ``sodar_uuid``.
    consequence = serializers.ReadOnlyField(source="consequence.sodar_uuid")
    #: Serialize ``locus`` as its ``sodar_uuid``.
    locus = serializers.ReadOnlyField(source="locus.sodar_uuid")
    #: Serialize ``frequency`` as its ``sodar_uuid``.
    frequency = serializers.ReadOnlyField(source="frequency.sodar_uuid")
    #: Serialize ``phenotypeprio`` as its ``sodar_uuid``.
    phenotypeprio = serializers.ReadOnlyField(source="phenotypeprio.sodar_uuid")
    #: Serialize ``variantprio`` as its ``sodar_uuid``.
    variantprio = serializers.ReadOnlyField(source="variantprio.sodar_uuid")
    #: Serialize ``clinvar`` as its ``sodar_uuid``.
    clinvar = serializers.ReadOnlyField(source="clinvar.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "session" in self.context:
            attrs["session"] = self.context["session"]
        return attrs

    class Meta:
        model = QuerySettings
        fields = BaseModelSerializer.Meta.fields + [
            "session",
            "genotype",
            "quality",
            "consequence",
            "locus",
            "frequency",
            "phenotypeprio",
            "variantprio",
            "clinvar",
        ]
        read_only_fields = fields


class QuerySettingsDetailsSerializer(QuerySettingsSerializer, WritableNestedModelSerializer):
    """Serializer for ``QuerySettings`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested
    frequency settings.
    """

    #: Nested serialization of the genotype settings.
    genotype = QuerySettingsGenotypeSerializer()
    #: Nested serialization of the quality settings.
    quality = QuerySettingsQualitySerializer()
    #: Nested serialization of the consequence settings.
    consequence = QuerySettingsConsequenceSerializer()
    #: Nested serialization of the locus settings.
    locus = QuerySettingsLocusSerializer()
    #: Nested serialization of the frequency settings.
    frequency = QuerySettingsFrequencySerializer()
    #: Nested serialization of the phenotype prio settings.
    phenotypeprio = QuerySettingsPhenotypePrioSerializer()
    #: Nested serialization of the variant prio settings.
    variantprio = QuerySettingsVariantPrioSerializer()
    #: Nested serialization of the clinvar settings.
    clinvar = QuerySettingsClinvarSerializer()

    class Meta:
        model = QuerySettingsSerializer.Meta.model
        fields = QuerySettingsSerializer.Meta.fields + [
            "genotype",
            "quality",
            "consequence",
            "locus",
            "frequency",
            "phenotypeprio",
            "variantprio",
            "clinvar",
        ]
        read_only_fields = fields


class QueryColumnsConfigSerializer(ColumnsSettingsBaseSerializer, BaseModelSerializer):
    """Serializer for ``QueryColumnsConfig``."""

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "query" in self.context:
            attrs["query"] = self.context["query"]
        return attrs

    class Meta:
        model = QueryColumnsConfig
        fields = BaseModelSerializer.Meta.fields + ColumnsSettingsBaseSerializer.Meta.fields
        read_only_fields = fields


class QuerySerializer(BaseModelSerializer):
    """Serializer for ``Query``."""

    rank = serializers.IntegerField(default=1, initial=1)
    label = serializers.CharField(max_length=128)

    #: Serialize ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")
    #: Serialize ``settings`` as its ``sodar_uuid``.
    settings = serializers.ReadOnlyField(source="settings.sodar_uuid")
    #: Serialize ``columnsconfig`` as its ``sodar_uuid``.
    columnsconfig = serializers.ReadOnlyField(source="columnsconfig.sodar_uuid")

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
            "settings",
            "columnsconfig",
        ]
        read_only_fields = fields


class QueryDetailsSerializer(QuerySerializer, WritableNestedModelSerializer):
    """Serializer for ``Query`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested query settings
    in detail.
    """

    #: For the details serializer, we use a nested details serializer.
    settings = QuerySettingsDetailsSerializer()
    #: Render the columns configuration here.
    columnsconfig = QueryColumnsConfigSerializer()

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

import typing
from typing import Optional

from django_pydantic_field.v2.rest_framework.fields import SchemaField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from projectroles.serializers import SODARUserSerializer
from rest_framework import serializers

from seqvars.models import (
    ClinvarGermlineAggregateDescription,
    DataSourceInfos,
    Gene,
    GenePanel,
    GenomeRegion,
    GnomadMitochondrialFrequencySettings,
    GnomadNuclearFrequencySettings,
    HelixmtDbFrequencySettings,
    InhouseFrequencySettings,
    SeqvarsClinvarSettingsBase,
    SeqvarsColumnConfig,
    SeqvarsColumnsSettingsBase,
    SeqvarsConsequenceSettingsBase,
    SeqvarsFrequencySettingsBase,
    SeqvarsGenotypePresets,
    SeqvarsLocusSettingsBase,
    SeqvarsPhenotypePrioSettingsBase,
    SeqvarsPredefinedQuery,
    SeqvarsPrioService,
    SeqvarsQuery,
    SeqvarsQueryColumnsConfig,
    SeqvarsQueryExecution,
    SeqvarsQueryPresetsClinvar,
    SeqvarsQueryPresetsColumns,
    SeqvarsQueryPresetsConsequence,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsLocus,
    SeqvarsQueryPresetsPhenotypePrio,
    SeqvarsQueryPresetsQuality,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQueryPresetsVariantPrio,
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsCategoryBase,
    SeqvarsQuerySettingsClinvar,
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsPhenotypePrio,
    SeqvarsQuerySettingsQuality,
    SeqvarsQuerySettingsVariantPrio,
    SeqvarsResultRow,
    SeqvarsResultRowPayload,
    SeqvarsResultSet,
    SeqvarsSampleGenotypeChoice,
    SeqvarsSampleQualityFilter,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantPrioSettingsBase,
    SeqvarsVariantTypeChoice,
    TermPresence,
)


class FrequencySettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``FrequencySettingsBase``.

    Not used directly but used as base class.
    """

    gnomad_exomes = SchemaField(
        schema=Optional[GnomadNuclearFrequencySettings], allow_null=True, default=None
    )
    gnomad_genomes = SchemaField(
        schema=Optional[GnomadNuclearFrequencySettings], allow_null=True, default=None
    )
    gnomad_mitochondrial = SchemaField(
        schema=Optional[GnomadMitochondrialFrequencySettings], allow_null=True, default=None
    )
    helixmtdb = SchemaField(
        schema=Optional[HelixmtDbFrequencySettings], allow_null=True, default=None
    )
    inhouse = SchemaField(schema=Optional[InhouseFrequencySettings], allow_null=True, default=None)

    class Meta:
        model = SeqvarsFrequencySettingsBase
        fields = [
            "gnomad_exomes",
            "gnomad_genomes",
            "gnomad_mitochondrial",
            "helixmtdb",
            "inhouse",
        ]


class ConsequenceSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``ConsequenceSettingsBase``.

    Not used directly but used as base class.
    """

    variant_types = SchemaField(schema=list[SeqvarsVariantTypeChoice], default=list)
    transcript_types = SchemaField(schema=list[SeqvarsTranscriptTypeChoice], default=list)
    variant_consequences = SchemaField(schema=list[SeqvarsVariantConsequenceChoice], default=list)
    max_distance_to_exon = serializers.IntegerField(required=False, allow_null=True, default=None)

    class Meta:
        model = SeqvarsConsequenceSettingsBase
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
        model = SeqvarsLocusSettingsBase
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
        model = SeqvarsPhenotypePrioSettingsBase
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
    services = SchemaField(schema=list[SeqvarsPrioService], default=list)

    class Meta:
        model = SeqvarsVariantPrioSettingsBase
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

    class Meta:
        model = SeqvarsClinvarSettingsBase
        fields = [
            "clinvar_presence_required",
            "clinvar_germline_aggregate_description",
            "allow_conflicting_interpretations",
        ]


class ColumnsSettingsBaseSerializer(serializers.ModelSerializer):
    """Serializer for ``ColumnsSettingsBase``.

    Not used directly but used as base class.
    """

    column_settings = SchemaField(schema=list[SeqvarsColumnConfig], default=list)

    class Meta:
        model = SeqvarsColumnsSettingsBase
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


class LabeledSortableBaseModelSerializer(serializers.ModelSerializer):
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


class QueryPresetsBaseSerializer(LabeledSortableBaseModelSerializer):
    """Serializer for ``QueryPresetsBase``.

    Not used directly but as a base class.
    """

    #: Serialize ``presetssetversion`` as its ``sodar_uuid``.
    presetssetversion = serializers.ReadOnlyField(source="presetssetversion.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the presets set object from context."""
        if "presetssetversion" in self.context:
            attrs["presetssetversion"] = self.context["presetssetversion"]
        return attrs

    class Meta:
        fields = LabeledSortableBaseModelSerializer.Meta.fields + [
            "presetssetversion",
        ]
        read_only_fields = fields


class SeqvarsQueryPresetsQualitySerializer(QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsQuality``.

    Not used directly but used as base class.
    """

    #: Whether the filter is active or not.
    filter_active = serializers.BooleanField(required=False, default=False)
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

    class Meta:
        model = SeqvarsQueryPresetsQuality
        fields = QueryPresetsBaseSerializer.Meta.fields + [
            "filter_active",
            "min_dp_het",
            "min_dp_hom",
            "min_ab_het",
            "min_gq",
            "min_ad",
            "max_ad",
        ]
        read_only_fields = fields


class SeqvarsQueryPresetsFrequencySerializer(
    FrequencySettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsFrequency``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQueryPresetsConsequenceSerializer(
    ConsequenceSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsConsequence``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsConsequence
        fields = (
            ConsequenceSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQueryPresetsLocusSerializer(LocusSettingsBaseSerializer, QueryPresetsBaseSerializer):
    """Serializer for ``QueryPresetsLocus``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsLocus
        fields = LocusSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        read_only_fields = fields


class SeqvarsQueryPresetsPhenotypePrioSerializer(
    PhenotypePrioSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsPhenotypePrio``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsPhenotypePrio
        fields = (
            PhenotypePrioSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQueryPresetsVariantPrioSerializer(
    VariantPrioSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsVariantPrio``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsVariantPrio
        fields = (
            VariantPrioSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQueryPresetsClinvarSerializer(
    ClinvarSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsClinvar``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsClinvar
        fields = ClinvarSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        read_only_fields = fields


class SeqvarsQueryPresetsColumnsSerializer(
    ColumnsSettingsBaseSerializer, QueryPresetsBaseSerializer
):
    """Serializer for ``QueryPresetsColumns``.

    Not used directly but used as base class.
    """

    class Meta:
        model = SeqvarsQueryPresetsColumns
        fields = ColumnsSettingsBaseSerializer.Meta.fields + QueryPresetsBaseSerializer.Meta.fields
        read_only_fields = fields


class SeqvarsPredefinedQuerySerializer(QueryPresetsBaseSerializer):
    """Serializer for ``PredefinedQuery``."""

    included_in_sop = serializers.BooleanField(required=False, default=False)

    genotype = SchemaField(
        schema=Optional[SeqvarsGenotypePresets],
        required=False,
        allow_null=True,
        default=None,
    )

    quality = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsQuality.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    frequency = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsFrequency.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    consequence = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsConsequence.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    locus = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsLocus.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    phenotypeprio = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsPhenotypePrio.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    variantprio = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsVariantPrio.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    clinvar = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsClinvar.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    columns = serializers.SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=SeqvarsQueryPresetsColumns.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )

    def validate(self, data):
        if "project" not in self.context:
            raise ValueError("Project is required in serializer context")

        result = super().validate(data)

        keys = (
            "quality",
            "frequency",
            "consequence",
            "locus",
            "phenotypeprio",
            "variantprio",
            "clinvar",
            "columns",
        )
        for key in keys:
            if result.get(key):
                if result[key].presetssetversion.presetsset.project != self.context["project"]:
                    raise ValueError(f"Predefined query {key} does not belong to the same project")

        return result

    class Meta:
        model = SeqvarsPredefinedQuery
        fields = QueryPresetsBaseSerializer.Meta.fields + [
            "included_in_sop",
            "genotype",
            "quality",
            "frequency",
            "consequence",
            "locus",
            "phenotypeprio",
            "variantprio",
            "clinvar",
            "columns",
        ]
        read_only_fields = QueryPresetsBaseSerializer.Meta.read_only_fields


class SeqvarsQueryPresetsSetSerializer(LabeledSortableBaseModelSerializer):
    """Serializer for ``QueryPresetsSet``."""

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the project from context."""
        if "project" in self.context:
            attrs["project"] = self.context["project"]
        return attrs

    class Meta:
        model = SeqvarsQueryPresetsSet
        fields = LabeledSortableBaseModelSerializer.Meta.fields + [
            "project",
        ]
        read_only_fields = fields


class SeqvarsQueryPresetsSetVersionSerializer(BaseModelSerializer):
    """Serializer for ``QueryPresetsSetVersion``."""

    #: Serialize ``presetsset`` as its ``sodar_uuid``.
    presetsset = serializers.ReadOnlyField(source="presetsset.sodar_uuid")

    version_major = serializers.IntegerField(
        required=False,
        allow_null=False,
        default=1,
    )
    version_minor = serializers.IntegerField(
        required=False,
        allow_null=False,
        default=0,
    )
    status = serializers.CharField(
        required=False, allow_null=False, default=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT
    )
    signed_off_by = SODARUserSerializer(read_only=True)

    def validate(self, attrs):
        """Augment the attributes by the presetsset from context."""
        if "presetsset" in self.context:
            attrs["presetsset"] = self.context["presetsset"]
        if self.context.get("current_user"):
            attrs["signed_off_by"] = self.context["current_user"]
        return attrs

    class Meta:
        model = SeqvarsQueryPresetsSetVersion
        fields = BaseModelSerializer.Meta.fields + [
            "presetsset",
            "version_major",
            "version_minor",
            "status",
            "signed_off_by",
        ]
        read_only_fields = fields


class SeqvarsQueryPresetsSetVersionDetailsSerializer(SeqvarsQueryPresetsSetVersionSerializer):
    """Serializer for ``QueryPresetsSetVersion`` (for ``*-detail``).

    When retrieving the details of a seqvar query preset set version, we also render the
    owned records as well as the presetsset.
    """

    #: Serialize ``presetsset`` in full.
    presetsset = SeqvarsQueryPresetsSetSerializer(read_only=True)

    #: Serialize all quality presets.
    seqvarsquerypresetsquality_set = SeqvarsQueryPresetsQualitySerializer(many=True, read_only=True)
    #: Serialize all frequency presets.
    seqvarsquerypresetsfrequency_set = SeqvarsQueryPresetsFrequencySerializer(
        many=True, read_only=True
    )
    #: Serialize all consequence presets.
    seqvarsquerypresetsconsequence_set = SeqvarsQueryPresetsConsequenceSerializer(
        many=True, read_only=True
    )
    #: Serialize all locus presets.
    seqvarsquerypresetslocus_set = SeqvarsQueryPresetsLocusSerializer(many=True, read_only=True)
    #: Serialize all phenotype prio presets.
    seqvarsquerypresetsphenotypeprio_set = SeqvarsQueryPresetsPhenotypePrioSerializer(
        many=True, read_only=True
    )
    #: Serialize all variant prio presets.
    seqvarsquerypresetsvariantprio_set = SeqvarsQueryPresetsVariantPrioSerializer(
        many=True, read_only=True
    )
    #: Serialize all clinvar presets.
    seqvarsquerypresetsclinvar_set = SeqvarsQueryPresetsClinvarSerializer(many=True, read_only=True)
    #: Serialize all columns presets.
    seqvarsquerypresetscolumns_set = SeqvarsQueryPresetsColumnsSerializer(many=True, read_only=True)
    #: Serialize all predefined queries.
    seqvarspredefinedquery_set = SeqvarsPredefinedQuerySerializer(many=True, read_only=True)

    class Meta:
        model = SeqvarsQueryPresetsSetVersionSerializer.Meta.model
        fields = SeqvarsQueryPresetsSetVersionSerializer.Meta.fields + [
            "seqvarsquerypresetsquality_set",
            "seqvarsquerypresetsfrequency_set",
            "seqvarsquerypresetsconsequence_set",
            "seqvarsquerypresetslocus_set",
            "seqvarsquerypresetsphenotypeprio_set",
            "seqvarsquerypresetsvariantprio_set",
            "seqvarsquerypresetsclinvar_set",
            "seqvarsquerypresetscolumns_set",
            "seqvarspredefinedquery_set",
        ]
        read_only_fields = fields


class SeqvarsQueryPresetsSetDetailsSerializer(SeqvarsQueryPresetsSetSerializer):
    """Serializer for ``QueryPresetsSet`` that renders all nested versions."""

    #: Serialize all versions of the presets set.
    versions = SeqvarsQueryPresetsSetVersionDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = SeqvarsQueryPresetsSet
        fields = SeqvarsQueryPresetsSetSerializer.Meta.fields + [
            "versions",
        ]
        read_only_fields = fields


class SeqvarsQuerySettingsBaseSerializer(BaseModelSerializer):
    """Serializer for ``QuerySettings``."""

    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    def validate(self, attrs):
        """Augment the attributes by the query settings object from context."""
        if "querysettings" in self.context:
            attrs["querysettings"] = self.context["querysettings"]
        return attrs

    class Meta:
        model = SeqvarsQuerySettingsCategoryBase
        fields = BaseModelSerializer.Meta.fields + ["querysettings"]
        read_only_fields = fields


class SeqvarsQuerySettingsGenotypeSerializer(SeqvarsQuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsGenotype``."""

    sample_genotype_choices = SchemaField(schema=list[SeqvarsSampleGenotypeChoice], default=list)

    class Meta:
        model = SeqvarsQuerySettingsGenotype
        fields = SeqvarsQuerySettingsBaseSerializer.Meta.fields + ["sample_genotype_choices"]
        read_only_fields = fields


class SeqvarsQuerySettingsQualitySerializer(SeqvarsQuerySettingsBaseSerializer):
    """Serializer for ``QuerySettingsQuality``."""

    sample_quality_filters = SchemaField(schema=list[SeqvarsSampleQualityFilter], default=list)

    class Meta:
        model = SeqvarsQuerySettingsQuality
        fields = SeqvarsQuerySettingsBaseSerializer.Meta.fields + ["sample_quality_filters"]
        read_only_fields = fields


class SeqvarsQuerySettingsConsequenceSerializer(
    ConsequenceSettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsConsequence``."""

    class Meta:
        model = SeqvarsQuerySettingsConsequence
        fields = (
            ConsequenceSettingsBaseSerializer.Meta.fields
            + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsLocusSerializer(
    LocusSettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsLocus``."""

    class Meta:
        model = SeqvarsQuerySettingsLocus
        fields = (
            LocusSettingsBaseSerializer.Meta.fields + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsFrequencySerializer(
    FrequencySettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsFrequency``."""

    class Meta:
        model = SeqvarsQuerySettingsFrequency
        fields = (
            FrequencySettingsBaseSerializer.Meta.fields
            + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsPhenotypePrioSerializer(
    PhenotypePrioSettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsPhenotypePrio``."""

    class Meta:
        model = SeqvarsQuerySettingsPhenotypePrio
        fields = (
            PhenotypePrioSettingsBaseSerializer.Meta.fields
            + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsVariantPrioSerializer(
    VariantPrioSettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsVariantPrio``."""

    class Meta:
        model = SeqvarsQuerySettingsVariantPrio
        fields = (
            VariantPrioSettingsBaseSerializer.Meta.fields
            + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsClinvarSerializer(
    ClinvarSettingsBaseSerializer, SeqvarsQuerySettingsBaseSerializer
):
    """Serializer for ``QuerySettingsClinvar``."""

    class Meta:
        model = SeqvarsQuerySettingsClinvar
        fields = (
            ClinvarSettingsBaseSerializer.Meta.fields
            + SeqvarsQuerySettingsBaseSerializer.Meta.fields
        )
        read_only_fields = fields


class SeqvarsQuerySettingsSerializer(BaseModelSerializer):
    """Serializer for ``QuerySettings``."""

    #: Serialize ``session`` as its ``sodar_uuid``.
    session = serializers.ReadOnlyField(source="session.sodar_uuid")

    #: Serialize ``presetssetversion`` as its ``sodar_uuid``.
    presetssetversion = serializers.ReadOnlyField(source="presetssetversion.sodar_uuid")
    #: Serialize ``predefinedquery`` as its ``sodar_uuid``.
    predefinedquery = serializers.ReadOnlyField(source="predefinedquery.sodar_uuid")

    #: Serialize ``genotypepresets`` as its ``sodar_uuid``.
    genotypepresets = SchemaField(
        schema=typing.Optional[SeqvarsGenotypePresets],
        required=False,
        allow_null=True,
        default=None,
    )
    #: Serialize ``qualitypresets`` as its ``sodar_uuid``.
    qualitypresets = serializers.ReadOnlyField(
        source="qualitypresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``consequencepresets`` as its ``sodar_uuid``.
    consequencepresets = serializers.ReadOnlyField(
        source="consequencepresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``locuspresets`` as its ``sodar_uuid``.
    locuspresets = serializers.ReadOnlyField(
        source="locuspresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``frequencypresets`` as its ``sodar_uuid``.
    frequencypresets = serializers.ReadOnlyField(
        source="frequencypresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``phenotypepriopresets`` as its ``sodar_uuid``.
    phenotypepriopresets = serializers.ReadOnlyField(
        source="phenotypepriopresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``variantpriopresets`` as its ``sodar_uuid``.
    variantpriopresets = serializers.ReadOnlyField(
        source="variantpriopresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``clinvarpresets`` as its ``sodar_uuid``.
    clinvarpresets = serializers.ReadOnlyField(
        source="clinvarpresets.sodar_uuid", required=False, allow_null=True, default=None
    )

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
        model = SeqvarsQuerySettings
        fields = BaseModelSerializer.Meta.fields + [
            "session",
            "presetssetversion",
            "predefinedquery",
            "genotypepresets",
            "qualitypresets",
            "consequencepresets",
            "locuspresets",
            "frequencypresets",
            "phenotypepriopresets",
            "variantpriopresets",
            "clinvarpresets",
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


class SeqvarsQuerySettingsDetailsSerializer(
    SeqvarsQuerySettingsSerializer, WritableNestedModelSerializer
):
    """Serializer for ``QuerySettings`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested
    owned category settings.
    """

    #: Serialize ``qualitypresets`` as its ``sodar_uuid``.
    qualitypresets = serializers.UUIDField(
        source="qualitypresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``consequencepresets`` as its ``sodar_uuid``.
    consequencepresets = serializers.UUIDField(
        source="consequencepresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``locuspresets`` as its ``sodar_uuid``.
    locuspresets = serializers.UUIDField(
        source="locuspresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``frequencypresets`` as its ``sodar_uuid``.
    frequencypresets = serializers.UUIDField(
        source="frequencypresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``phenotypepriopresets`` as its ``sodar_uuid``.
    phenotypepriopresets = serializers.UUIDField(
        source="phenotypepriopresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``variantpriopresets`` as its ``sodar_uuid``.
    variantpriopresets = serializers.UUIDField(
        source="variantpriopresets.sodar_uuid", required=False, allow_null=True, default=None
    )
    #: Serialize ``clinvarpresets`` as its ``sodar_uuid``.
    clinvarpresets = serializers.UUIDField(
        source="clinvarpresets.sodar_uuid", required=False, allow_null=True, default=None
    )

    #: Nested serialization of the genotype settings.
    genotype = SeqvarsQuerySettingsGenotypeSerializer()
    #: Nested serialization of the quality settings.
    quality = SeqvarsQuerySettingsQualitySerializer()
    #: Nested serialization of the consequence settings.
    consequence = SeqvarsQuerySettingsConsequenceSerializer()
    #: Nested serialization of the locus settings.
    locus = SeqvarsQuerySettingsLocusSerializer()
    #: Nested serialization of the frequency settings.
    frequency = SeqvarsQuerySettingsFrequencySerializer()
    #: Nested serialization of the phenotype prio settings.
    phenotypeprio = SeqvarsQuerySettingsPhenotypePrioSerializer()
    #: Nested serialization of the variant prio settings.
    variantprio = SeqvarsQuerySettingsVariantPrioSerializer()
    #: Nested serialization of the clinvar settings.
    clinvar = SeqvarsQuerySettingsClinvarSerializer()

    def validate(self, data):
        data = super().validate(data)

        if "qualitypresets" in data:
            qualitypresets_uuid = data.pop("qualitypresets")["sodar_uuid"]
            if qualitypresets_uuid:
                data["qualitypresets"] = SeqvarsQueryPresetsQuality.objects.get(
                    sodar_uuid=qualitypresets_uuid
                )
        if "consequencepresets" in data:
            consequencepresets_uuid = data.pop("consequencepresets")["sodar_uuid"]
            if consequencepresets_uuid:
                data["consequencepresets"] = SeqvarsQueryPresetsConsequence.objects.get(
                    sodar_uuid=consequencepresets_uuid
                )
        if "locuspresets" in data:
            locuspresets_uuid = data.pop("locuspresets")["sodar_uuid"]
            if locuspresets_uuid:
                data["locuspresets"] = SeqvarsQueryPresetsLocus.objects.get(
                    sodar_uuid=locuspresets_uuid
                )
        if "frequencypresets" in data:
            frequencypresets_uuid = data.pop("frequencypresets")["sodar_uuid"]
            if frequencypresets_uuid:
                data["frequencypresets"] = SeqvarsQueryPresetsFrequency.objects.get(
                    sodar_uuid=frequencypresets_uuid
                )
        if "phenotypepriopresets" in data:
            phenotypepriopresets_uuid = data.pop("phenotypepriopresets")["sodar_uuid"]
            if phenotypepriopresets_uuid:
                data["phenotypepriopresets"] = SeqvarsQueryPresetsPhenotypePrio.objects.get(
                    sodar_uuid=phenotypepriopresets_uuid
                )
        if "variantpriopresets" in data:
            variantpriopresets_uuid = data.pop("variantpriopresets")["sodar_uuid"]
            if variantpriopresets_uuid:
                data["variantpriopresets"] = SeqvarsQueryPresetsVariantPrio.objects.get(
                    sodar_uuid=variantpriopresets_uuid
                )
        if "clinvarpresets" in data:
            clinvarpresets_uuid = data.pop("clinvarpresets")["sodar_uuid"]
            if clinvarpresets_uuid:
                data["clinvarpresets"] = SeqvarsQueryPresetsClinvar.objects.get(
                    sodar_uuid=clinvarpresets_uuid
                )

        return data

    class Meta:
        model = SeqvarsQuerySettingsSerializer.Meta.model
        fields = SeqvarsQuerySettingsSerializer.Meta.fields + [
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


class SeqvarsQueryColumnsConfigSerializer(ColumnsSettingsBaseSerializer, BaseModelSerializer):
    """Serializer for ``QueryColumnsConfig``."""

    def validate(self, attrs):
        """Augment the attributes by the case from context."""
        if "query" in self.context:
            attrs["query"] = self.context["query"]
        return attrs

    class Meta:
        model = SeqvarsQueryColumnsConfig
        fields = BaseModelSerializer.Meta.fields + ColumnsSettingsBaseSerializer.Meta.fields
        read_only_fields = fields


class SeqvarsQuerySerializer(BaseModelSerializer):
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
        model = SeqvarsQuery
        fields = BaseModelSerializer.Meta.fields + [
            "rank",
            "label",
            "session",
            "settings",
            "columnsconfig",
        ]
        read_only_fields = fields


class SeqvarsQueryDetailsSerializer(SeqvarsQuerySerializer, WritableNestedModelSerializer):
    """Serializer for ``Query`` (for ``*-detail``).

    For retrieve, update, or delete operations, we also render the nested query settings
    in detail.
    """

    #: For the details serializer, we use a nested details serializer.
    settings = SeqvarsQuerySettingsDetailsSerializer()
    #: Render the columns configuration here.
    columnsconfig = SeqvarsQueryColumnsConfigSerializer()

    class Meta:
        model = SeqvarsQuery
        fields = SeqvarsQuerySerializer.Meta.fields
        read_only_fields = fields


class SeqvarsQueryExecutionSerializer(BaseModelSerializer):
    """Serializer for ``QueryExecution``."""

    #: Serialize ``query`` as its ``sodar_uuid``.
    query = serializers.ReadOnlyField(source="query.sodar_uuid")
    #: Serialize ``querysettings`` as its ``sodar_uuid``.
    querysettings = serializers.ReadOnlyField(source="querysettings.sodar_uuid")

    class Meta:
        model = SeqvarsQueryExecution
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


class SeqvarsQueryExecutionDetailsSerializer(SeqvarsQueryExecutionSerializer):
    """Serializer for ``QueryExecution``."""

    #: For the details, serialize ``querysettings`` fully.
    querysettings = SeqvarsQuerySettingsDetailsSerializer()

    class Meta:
        model = SeqvarsQueryExecution
        fields = SeqvarsQueryExecutionSerializer.Meta.fields
        read_only_fields = fields


class SeqvarsResultSetSerializer(BaseModelSerializer):
    """Serializer for ``ResultSet``."""

    #: Explicitely provide django-pydantic-field schema for ``datasource_infos``.
    datasource_infos = SchemaField(schema=DataSourceInfos)
    #: Serialize ``queryexecution`` as its ``sodar_uuid``.
    queryexecution = serializers.ReadOnlyField(source="queryexecution.sodar_uuid")

    class Meta:
        model = SeqvarsResultSet
        fields = BaseModelSerializer.Meta.fields + [
            "queryexecution",
            "datasource_infos",
        ]
        read_only_fields = fields


class SeqvarsResultRowSerializer(serializers.ModelSerializer):
    """Serializer for ``ResultRow``."""

    #: Serialize ``resultset`` as its ``sodar_uuid``.
    resultset = serializers.ReadOnlyField(source="resultset.sodar_uuid")
    #: Explicitely provide django-pydantic-field schema for ``payload``.
    payload = SchemaField(schema=SeqvarsResultRowPayload)

    class Meta:
        model = SeqvarsResultRow
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

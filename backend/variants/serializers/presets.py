from django.db import transaction
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import CharField, ListField, ModelSerializer, ValidationError

from variants.models import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
    QuickPresets,
)


class FrequencyPresetsSerializer(ModelSerializer):
    """Serializer for ``FrequencyPresets``."""

    presetset = SlugRelatedField(slug_field="sodar_uuid", read_only=True)

    def to_internal_value(self, data):
        """Convert empty strings to None for integer and float fields, but validate non-empty strings."""
        # List of integer and float fields that should accept None
        integer_fields = [
            "thousand_genomes_homozygous",
            "thousand_genomes_heterozygous",
            "thousand_genomes_hemizygous",
            "exac_homozygous",
            "exac_heterozygous",
            "exac_hemizygous",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "inhouse_homozygous",
            "inhouse_heterozygous",
            "inhouse_hemizygous",
            "inhouse_carriers",
            "mtdb_count",
            "helixmtdb_hom_count",
            "helixmtdb_het_count",
            "mitomap_count",
        ]
        float_fields = [
            "thousand_genomes_frequency",
            "exac_frequency",
            "gnomad_exomes_frequency",
            "gnomad_genomes_frequency",
            "mtdb_frequency",
            "helixmtdb_frequency",
            "mitomap_frequency",
        ]

        # Create a mutable copy of the data
        data_copy = data.copy() if hasattr(data, "copy") else dict(data)

        # Convert empty strings to None, but validate non-empty strings
        for field in integer_fields:
            if field in data_copy:
                value = data_copy[field]
                if value == "" or value is None:
                    data_copy[field] = None
                elif isinstance(value, str):
                    # Validate that non-empty strings can be converted to integers
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        # Let DRF handle the validation error
                        pass

        # Convert empty strings to None for float fields
        for field in float_fields:
            if field in data_copy:
                value = data_copy[field]
                if value == "" or value is None:
                    data_copy[field] = None
                elif isinstance(value, str):
                    # Validate that non-empty strings can be converted to floats
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        # Let DRF handle the validation error
                        pass

        return super().to_internal_value(data_copy)

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = FrequencyPresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class ImpactPresetsSerializer(ModelSerializer):
    """Serializer for ``ImpactPresets``."""

    presetset = SlugRelatedField(slug_field="sodar_uuid", read_only=True)

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = ImpactPresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class QualityPresetsSerializer(ModelSerializer):
    """Serializer for ``QualityPresets``."""

    presetset = SlugRelatedField(slug_field="sodar_uuid", read_only=True)

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = QualityPresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class ChromosomePresetsSerializer(ModelSerializer):
    """Serializer for ``ChromosomePresets``."""

    presetset = SlugRelatedField(slug_field="sodar_uuid", read_only=True)
    genomic_region = ListField(
        child=CharField(max_length=64, required=False), allow_empty=True, default=list
    )
    gene_allowlist = ListField(
        child=CharField(max_length=64, required=False), allow_empty=True, default=list
    )
    gene_blocklist = ListField(
        child=CharField(max_length=64, required=False), allow_empty=True, default=list
    )

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = ChromosomePresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class FlagsEtcPresetsSerializer(ModelSerializer):
    """Serializer for ``FlagsEtcPresets``."""

    presetset = SlugRelatedField(slug_field="sodar_uuid", read_only=True)

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = FlagsEtcPresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class QuickPresetsSerializer(ModelSerializer):
    """Serializer for ``QuickPresets``.

    The ``presetset`` must be given in the context.
    """

    presetset = SlugRelatedField(
        slug_field="sodar_uuid",
        read_only=True,
    )
    frequency = SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=FrequencyPresets.objects.all(),
        allow_null=True,
    )
    impact = SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=ImpactPresets.objects.all(),
        allow_null=True,
    )
    quality = SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=QualityPresets.objects.all(),
        allow_null=True,
    )
    chromosome = SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=ChromosomePresets.objects.all(),
        allow_null=True,
    )
    flagsetc = SlugRelatedField(
        slug_field="sodar_uuid",
        queryset=FlagsEtcPresets.objects.all(),
        allow_null=True,
    )

    def validate(self, data):
        field_names = (
            "frequency",
            "impact",
            "quality",
            "chromosome",
            "flagsetc",
        )
        presetset = self.context["presetset"]
        for field_name in field_names:
            if data.get(field_name) and data[field_name].presetset.id != presetset.id:
                raise ValidationError(f"The {field_name} is not in the same PresetSet.")
        return data

    def create(self, validated_data):
        """Allow setting the presetset on creation only."""
        validated_data["presetset"] = self.context["presetset"]
        return super().create(validated_data)

    class Meta:
        model = QuickPresets
        exclude = ("id",)
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "presetset",
        )


class PresetSetSerializer(ModelSerializer):
    """Serializer for ``PresetSet``.

    We will serialize the nested values read-only.
    """

    project = SlugRelatedField(slug_field="sodar_uuid", read_only=True)
    quickpresets_set = QuickPresetsSerializer(many=True, read_only=True)
    frequencypresets_set = FrequencyPresetsSerializer(many=True, read_only=True)
    impactpresets_set = ImpactPresetsSerializer(many=True, read_only=True)
    qualitypresets_set = QualityPresetsSerializer(many=True, read_only=True)
    chromosomepresets_set = ChromosomePresetsSerializer(many=True, read_only=True)
    flagsetcpresets_set = FlagsEtcPresetsSerializer(many=True, read_only=True)

    def _reset_default_presetset(self):
        """Reset the default presetset for the project."""
        for presetset in self.instance.project.presetset_set.filter(default_presetset=True):
            presetset.default_presetset = False
            presetset.save()

    @transaction.atomic
    def create(self, validated_data):
        """Allow setting the project on creation only."""
        validated_data["project"] = self.context["project"]
        if validated_data.get("default_presetset", False):
            self._reset_default_presetset()
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        """Allow setting the project on update only."""
        if validated_data.get("default_presetset", False):
            self._reset_default_presetset()
        return super().update(instance, validated_data)

    class Meta:
        model = PresetSet
        exclude = ("id", "state", "version_major", "version_minor", "signed_off_by")
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "project",
            "quickpresets_set",
            "frequencypresets_set",
            "impactpresets_set",
            "qualitypresets_set",
            "chromosomepresets_set",
            "flagsetcpresets_set",
        )

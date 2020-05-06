"""Serializers for the importer app."""
from django.db.models import Q
from rest_framework import serializers

from projectroles.serializers import SODARProjectModelSerializer
from variants.serializers import CoreCaseSerializerMixin
from .models import (
    BamQcFile,
    CaseImportInfo,
    DatabaseInfoFile,
    EffectFile,
    GenotypeFile,
    VariantSetImportInfo,
)


class CommonFileSerializerMixin:
    """Validation for variant set files."""

    related_class = None
    related_field_name = None

    def create(self, validated_data):
        validated_data[self.related_field_name] = self.context[self.related_field_name]
        return super().create(validated_data)

    def validate(self, value):
        """Validate the whole object."""

        # The unique-together validation must be done here as only here, project has been set.
        if self.related_field_name in value:
            qs = self.related_class.objects.filter(
                variant_set_import_info=self.context[self.related_field_name], md5=value["md5"]
            )
            if self.instance:
                qs = qs.filter(~Q(sodar_uuid=self.instance.sodar_uuid))
            if qs.exists():
                raise serializers.ValidationError(
                    "Checksum %s must be unique in variant set." % repr(value["md5"])
                )

        return value


class BamQcFileSerializer(CommonFileSerializerMixin, serializers.ModelSerializer):
    """Serializer for the BamQcFile model."""

    case_import_info = serializers.ReadOnlyField(source="case_import_info.sodar_uuid")

    related_class = CaseImportInfo
    related_field_name = "case_import_info"

    class Meta:
        model = BamQcFile
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case_import_info",
            "file",
            "name",
            "md5",
        )
        extra_kwargs = {"file": {"write_only": True}}


IMPORT_VARIANT_SET_URL_FIELDS = (
    "sodar_uuid",
    "date_created",
    "date_modified",
    "variant_set_import_info",
    "file",
    "name",
    "md5",
)


class GenotypeFileSerializer(CommonFileSerializerMixin, serializers.ModelSerializer):
    """Serializer for the GenotypeFile model."""

    variant_set_import_info = serializers.ReadOnlyField(source="variant_set_import_info.sodar_uuid")

    related_class = VariantSetImportInfo
    related_field_name = "variant_set_import_info"

    class Meta:
        model = GenotypeFile
        fields = IMPORT_VARIANT_SET_URL_FIELDS
        extra_kwargs = {"file": {"write_only": True}}


class EffectFileSerializer(CommonFileSerializerMixin, serializers.ModelSerializer):
    """Serializer for the EffectsFile model."""

    variant_set_import_info = serializers.ReadOnlyField(source="variant_set_import_info.sodar_uuid")

    related_class = VariantSetImportInfo
    related_field_name = "variant_set_import_info"

    class Meta:
        model = EffectFile
        fields = IMPORT_VARIANT_SET_URL_FIELDS
        extra_kwargs = {"file": {"write_only": True}}


class DatabaseInfoFileSerializer(CommonFileSerializerMixin, serializers.ModelSerializer):
    """Serializer for the DatabaseInfoFile model."""

    variant_set_import_info = serializers.ReadOnlyField(source="variant_set_import_info.sodar_uuid")

    related_class = VariantSetImportInfo
    related_field_name = "variant_set_import_info"

    class Meta:
        model = DatabaseInfoFile
        fields = IMPORT_VARIANT_SET_URL_FIELDS
        extra_kwargs = {"file": {"write_only": True}}


class VariantSetImportInfoSerializer(serializers.ModelSerializer):
    """Serializer for the ``ImportVariantSetInfo`` model."""

    case_import_info = serializers.ReadOnlyField(source="case_import_info.sodar_uuid")
    genotype_files = GenotypeFileSerializer(many=True, read_only=True, source="genotypefile_set")
    effect_files = EffectFileSerializer(many=True, read_only=True, source="effectfile_set")
    db_info_files = DatabaseInfoFileSerializer(
        many=True, read_only=True, source="databaseinfofile_set"
    )

    def update(self, instance, validated_data):
        validated_data["case_import_info"] = self.context["case_import_info"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data["case_import_info"] = self.context["case_import_info"]
        return super().create(validated_data)

    class Meta:
        model = VariantSetImportInfo
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "genomebuild",
            "case_import_info",
            "variant_type",
            "genotype_files",
            "effect_files",
            "db_info_files",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
        )


class CaseImportInfoSerializer(CoreCaseSerializerMixin, SODARProjectModelSerializer):
    """Serializer for the ``CaseImportInfo`` model."""

    pedigree = serializers.JSONField()
    owner = serializers.ReadOnlyField(source="owner.username")
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    project = serializers.ReadOnlyField(source="project.sodar_uuid")

    bam_qc_files = BamQcFileSerializer(many=True, read_only=True, source="bamqcfile_set")
    variant_sets = VariantSetImportInfoSerializer(
        many=True, read_only=True, source="variantsetimportinfo_set"
    )

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, values):
        # Ensure draft state on creation and valid transition otherwise.
        if "state" in values:
            if self.instance:
                allowed_transitions = (
                    ("draft", "submitted"),
                    ("imported", "submitted"),
                    ("evicted", "submitted"),
                    ("failed", "submitted"),
                    ("submitted", "draft"),  # only necessary on uncaught import error
                )
                if (self.instance.state, values["state"]) not in allowed_transitions:
                    raise serializers.ValidationError(
                        "Requested invalid transition from %s to %s."
                        % (repr(self.instance.state), repr(values["state"]))
                    )
            elif values["state"] != "draft":
                raise serializers.ValidationError(
                    'Can only create in "draft" state but is: %s' % repr(values["state"])
                )
        return values

    class Meta:
        model = CaseImportInfo
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "owner",
            "case",
            "project",
            "name",
            "index",
            "pedigree",
            "notes",
            "state",
            "tags",
            "bam_qc_files",
            "variant_sets",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "project",
        )

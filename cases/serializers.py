from projectroles.app_settings import AppSettingAPI
from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from variants.models import (
    Case,
    CaseAlignmentStats,
    CaseComments,
    CaseGeneAnnotationEntry,
    PedigreeRelatedness,
    PresetSet,
    SampleVariantStatistics,
)
from variants.serializers import CoreCaseSerializerMixin

_app_settings = AppSettingAPI()


class CaseSerializer(CoreCaseSerializerMixin, SODARProjectModelSerializer):
    """Serializer for the ``Case`` model.

    In contrast to the old (legacy) ``CaseSerializer`` from ``variants.serializers.case``, this class does not
    perform serialization of nested attributes and thus does not trigger a large query cascade.
    """

    #: Serialize ``project`` as its ``sodar_uuid``.
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    #: Serialize ``presetset`` as its ``sodar_uuid``.
    presetset = serializers.ReadOnlyField(source="presetset.sodar_uuid")
    #: Serialize sex errors from method call.
    sex_errors = serializers.SerializerMethodField("get_sex_errors")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: Cache value for app setting to reduce number of queries.
        self.disable_pedigree_sex_check = None

    def to_internal_value(self, data):
        """Override to make 'presetset' writable."""
        result = super().to_internal_value(data)
        if "presetset" not in data:
            pass
        elif not data.get("presetset"):
            result["presetset"] = None
        else:
            presetsets = PresetSet.objects.filter(sodar_uuid=data.get("presetset"))
            if not presetsets:
                raise ValidationError({"presetsets": "PresetSet not found."})
            result["presetset"] = presetsets[0]
        return result

    def get_sex_errors(self, obj):
        if self.disable_pedigree_sex_check is None:
            self.disable_pedigree_sex_check = _app_settings.get_app_setting(
                "variants", "disable_pedigree_sex_check", project=obj.project
            )
        return obj.sex_errors(disable_pedigree_sex_check=self.disable_pedigree_sex_check)

    class Meta:
        model = Case
        exclude = (
            "id",
            "search_tokens",
            "latest_variant_set",
            "latest_structural_variant_set",
        )
        read_only_fields = (
            "sodar_uuid",
            "project",
            "date_created",
            "date_modified",
            "num_small_vars",
            "num_svs",
            "project",
            "release",
            "presetset",  # made writable in to_internal_value
            "state",
        )


class CaseCommentSerializer(SODARProjectModelSerializer):
    """Serializer for ``CaseComments``."""

    #: Serialize the case as its SODAR UUID.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: Serializer the user as its name.
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    def create(self, validated_data):
        """Make case and user writeable (only) on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = CaseComments
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
            "comment",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
        )


class CaseGeneAnnotationSerializer(SODARProjectModelSerializer):
    """Serializer for ``CaseGeneAnnotationEntry``."""

    #: Serialize the case as its SODAR UUID.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = CaseGeneAnnotationEntry
        fields = (
            "sodar_uuid",
            "case",
            "gene_symbol",
            "entrez_id",
            "ensembl_gene_id",
            "annotation",
        )
        read_only_fields = fields


class CaseAlignmentStatsSerializer(serializers.ModelSerializer):
    """Serializer for ``CaseAlignmentStats``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: Serialize ``variantset`` as its ``sodar_uuid``.
    variantset = serializers.ReadOnlyField(source="variant_set.sodar_uuid")

    class Meta:
        model = CaseAlignmentStats
        fields = (
            "case",
            "variantset",
            "bam_stats",
        )
        read_only_fields = fields


class SampleVariantStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for ``SampleVariantStatistics``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="stats.variant_set.case.sodar_uuid")
    # #: Serialize ``ontarget_ts_tv_ratio`` from method call.
    # ontarget_ts_tv_ratio = serializers.SerializerMethodField("ontarget_ts_tv_ratio")

    class Meta:
        model = SampleVariantStatistics
        fields = (
            "case",
            "sample_name",
            "ontarget_transitions",
            "ontarget_transversions",
            "ontarget_snvs",
            "ontarget_indels",
            "ontarget_mnvs",
            "ontarget_effect_counts",
            "ontarget_indel_sizes",
            "ontarget_dps",
            "ontarget_dp_quantiles",
            "het_ratio",
            "chrx_het_hom",
            "ontarget_ts_tv_ratio",
        )
        read_only_fields = fields


class PedigreeRelatednessSerializer(serializers.ModelSerializer):
    """Serializer for ``PedigreeRelatedness``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="stats.variant_set.case.sodar_uuid")
    # #: Serialize ``ontarget_ts_tv_ratio`` from method call.
    # relatedness = serializers.SerializerMethodField("relatedness")

    class Meta:
        model = PedigreeRelatedness
        fields = (
            "case",
            "sample1",
            "sample2",
            "het_1_2",
            "het_1",
            "het_2",
            "n_ibs0",
            "n_ibs1",
            "n_ibs2",
            "relatedness",
        )
        read_only_fields = fields

from projectroles.app_settings import AppSettingAPI
from projectroles.serializers import SODARProjectModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cases.models import (
    CaseAnalysis,
    CaseAnalysisSession,
    Disease,
    Individual,
    Pedigree,
    PhenotypicFeature,
)
from cases_qc.models import CaseQc
from cases_qc.serializers import CaseQcSerializer
from svs.serializers import SvQueryResultSetSerializer
from variants.models import (
    Case,
    CaseAlignmentStats,
    CaseComments,
    CaseGeneAnnotationEntry,
    PedigreeRelatedness,
    PresetSet,
    SampleVariantStatistics,
)
from variants.serializers import CoreCaseSerializerMixin, SmallVariantQueryResultSetSerializer

_app_settings = AppSettingAPI()


class CaseSerializerNg(CoreCaseSerializerMixin, SODARProjectModelSerializer):
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
    #: Serialize ``smallvariantqueryresultset`` as its ``sodar_uuid``.
    smallvariantqueryresultset = serializers.SerializerMethodField()
    #: Serialize ``svqueryresultset`` as its ``sodar_uuid``.
    svqueryresultset = serializers.SerializerMethodField()
    #: Serialize latest ``CaseQc`` in active state.
    caseqc = serializers.SerializerMethodField()

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

    def get_sex_errors(self, obj) -> dict[str, list[str]]:
        if self.disable_pedigree_sex_check is None:
            self.disable_pedigree_sex_check = _app_settings.get(
                "variants", "disable_pedigree_sex_check", project=obj.project
            )
        return obj.sex_errors(disable_pedigree_sex_check=self.disable_pedigree_sex_check)

    def get_smallvariantqueryresultset(self, obj) -> dict[str, int | float | str | None]:
        return SmallVariantQueryResultSetSerializer(
            obj.smallvariantqueryresultset_set.filter(smallvariantquery=None).first()
        ).data

    def get_svqueryresultset(self, obj) -> dict[str, int | float | str | None]:
        return SvQueryResultSetSerializer(
            obj.svqueryresultset_set.filter(svquery=None).first()
        ).data

    def get_caseqc(self, obj) -> dict[str, int | float | str | None] | None:
        """Obtain the latest CaseQC for this in active state and serialize it.

        If there is no such record then return ``None``.
        """
        caseqc = obj.caseqc_set.filter(state=CaseQc.STATE_ACTIVE).first()
        if caseqc:
            return CaseQcSerializer(caseqc).data
        else:
            return None

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
            "caseqc",
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


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer for models with sodar_uuid and creation/update time."""

    class Meta:
        fields = [
            "sodar_uuid",
            "date_created",
            "date_modified",
        ]


class TermCoreSerializer(BaseSerializer):
    """Serializer for ``TermCore``.

    Not used directly but as a base class for ``DiseaseSerializer`` and ``PhenotypicFeatureSerializer``.
    """

    #: Serialize ``individual`` as its ``sodar_uuid``.
    individual = serializers.ReadOnlyField(source="individual.sodar_uuid")

    class Meta:
        fields = BaseSerializer.Meta.fields + [
            "individual",
            "term_id",
            "term_label",
            "excluded",
        ]
        read_only_fields = fields


class DiseaseSerializer(TermCoreSerializer):
    """Serializer for ``Disease``."""

    class Meta:
        model = Disease
        fields = TermCoreSerializer.Meta.fields
        read_only_fields = TermCoreSerializer.Meta.read_only_fields


class PhenotypicFeatureSerializer(TermCoreSerializer):
    """Serializer for ``PhenotypicFeature``."""

    class Meta:
        model = PhenotypicFeature
        fields = TermCoreSerializer.Meta.fields
        read_only_fields = TermCoreSerializer.Meta.read_only_fields


class IndividualSerializer(BaseSerializer):
    """Serializer for ``Individual``."""

    #: Serialize ``pedigree`` as its ``sodar_uuid``.
    pedigree = serializers.ReadOnlyField(source="pedigree.sodar_uuid")
    #: Serialize ``case`` as its ``sodar_uuid`` (via ``pedigree``).
    case = serializers.ReadOnlyField(source="pedigree.case.sodar_uuid")
    #: Serialize ``enrichmentkit`` as its ``sodar_uuid``.
    enrichmentkit = serializers.ReadOnlyField(source="enrichmentkit.sodar_uuid")
    #: Serialize diseases.
    disease_set = DiseaseSerializer(many=True, read_only=True)
    #: Serialize phenotypic features.
    phenotypicfeature_set = PhenotypicFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Individual
        fields = BaseSerializer.Meta.fields + [
            "pedigree",
            "case",
            "name",
            "father",
            "mother",
            "affected",
            "sex",
            "karyotypic_sex",
            "assay",
            "enrichmentkit",
            "disease_set",
            "phenotypicfeature_set",
        ]
        read_only_fields = fields


class PedigreeSerializer(BaseSerializer):
    """Serializer for ``Pedigree``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: Serialize the individuals from the pedigree.
    individual_set = IndividualSerializer(many=True, read_only=True)

    class Meta:
        model = Pedigree
        fields = BaseSerializer.Meta.fields + [
            "case",
            "individual_set",
        ]
        read_only_fields = fields


class CaseAnalysisSerializer(BaseSerializer):
    """Serializer for ``CaseAnalysis``."""

    #: Serialize ``case`` as its ``sodar_uuid``.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = CaseAnalysis
        fields = BaseSerializer.Meta.fields + [
            "case",
            "name",
        ]
        read_only_fields = fields


class CaseAnalysisSessionSerializer(BaseSerializer):
    """Serializer for ``CaseAnalysisSession``."""

    #: Serialize ``caseanalysis`` as its ``sodar_uuid``.
    caseanalysis = serializers.ReadOnlyField(source="caseanalysis.sodar_uuid")
    #: Serialize ``case`` as its ``sodar_uuid`` (via ``caseanalysis``)
    case = serializers.ReadOnlyField(source="caseanalysis.case.sodar_uuid")
    #: Serialize ``user`` as its ``sodar_uuid``.
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    class Meta:
        model = CaseAnalysisSession
        fields = BaseSerializer.Meta.fields + [
            "caseanalysis",
            "case",
            "user",
        ]
        read_only_fields = fields

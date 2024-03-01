from typing import Any, Dict, List
from django.db.models import Q
from projectroles.serializers import SODARModelSerializer, SODARProjectModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from svs.models import SvAnnotationReleaseInfo
from variants.models import (
    AnnotationReleaseInfo,
    Case,
    CasePhenotypeTerms,
    ExportFileBgJob,
    PresetSet,
    SmallVariantSet,
)


class AnnotationReleaseInfoSerializer(SODARModelSerializer):
    class Meta:
        model = AnnotationReleaseInfo
        fields = (
            "genomebuild",
            "table",
            "timestamp",
            "release",
        )
        read_only_fields = fields


class SvAnnotationReleaseInfoSerializer(SODARModelSerializer):
    class Meta:
        model = SvAnnotationReleaseInfo
        fields = (
            "genomebuild",
            "table",
            "timestamp",
            "release",
        )
        read_only_fields = fields


class CoreCaseSerializerMixin:
    """Validation functions for core case fields."""

    def to_representation(self, instance):
        """Convert 'patient' fields back into 'name' in pedigree."""
        # TODO: can go away after renaming
        ret = super().to_representation(instance)
        ret["pedigree"] = [
            {{"patient": "name"}.get(k, k): v for k, v in m.items()} for m in ret["pedigree"]
        ]
        return ret

    def validate(self, value):
        """Validate the whole object."""
        # This is called after the calls to ``self.validate_*()``.
        if "index" in value:
            for entry in value.get("pedigree", getattr(self.instance, "pedigree", ())):
                if entry["patient"] == value["index"]:
                    break
            else:  # no break above
                raise serializers.ValidationError(
                    "Index name %s not found in pedigree members." % repr(value["index"])
                )

        # The unique-together validation must be done here as only here, project has been set.
        if "name" in value:
            qs = self.Meta.model.objects.filter(project=self.context["project"], name=value["name"])
            if self.instance:
                qs = qs.filter(~Q(sodar_uuid=self.instance.sodar_uuid))
            if qs.exists():
                raise serializers.ValidationError(
                    "Case name %s must be unique in project." % repr(value["name"])
                )

        return value

    def validate_tags(self, value):
        """Validate tags field."""
        # TODO: compare to project's allowed tags from settings
        return value or []

    def validate_pedigree(self, pedigree):
        """Validate pedigree JSON field.

        Also, rename "name" in JSON field to "patient" for internal usage.
        """
        if not isinstance(pedigree, list):
            raise serializers.ValidationError("pedigree must be a list")
        names = [e.get("patient", e["name"]) for e in pedigree]
        for i, entry in enumerate(pedigree):
            if not isinstance(entry, dict):
                raise serializers.ValidationError(
                    "pedigree entries must be objects but no. %d is not" % (i + 1)
                )
            all_keys = {"name", "father", "mother", "sex", "affected", "has_gt_entries"}
            if entry.keys() != all_keys:
                left = entry.keys() - all_keys
                right = all_keys - entry.keys()
                raise serializers.ValidationError(
                    "pedigree entry no. %d keys mismatch, incorrect: %s, missing: %s"
                    % (i + 1, list(sorted(left)), list(sorted(right)))
                )
            for key in ("father", "mother"):
                if entry[key] != "0" and entry[key] not in names:
                    raise serializers.ValidationError(
                        "%s of pedigree entry no. %d points to invalid name: %s"
                        % (key, i + 1, repr(entry[key]))
                    )
            if entry["sex"] not in (0, 1, 2):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong sex value %s" % (i + 1, entry["sex"])
                )
            if entry["affected"] not in (0, 1, 2):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong sex value %s" % (i + 1, entry["affected"])
                )
            if not isinstance(entry["has_gt_entries"], bool):
                raise serializers.ValidationError(
                    "pedigree entry no. %d has wrong has_gt_entries value %s"
                    % (i + 1, entry["has_gt_entries"])
                )
        # TODO: can go away after renaming
        return [{{"name": "patient"}.get(k, k): v for k, v in m.items()} for m in pedigree]


class CasePhenotypeTermsSerializer(SODARModelSerializer):
    #: Serialize the case as its SODAR UUID.
    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    #: The phenotype terms.
    terms = serializers.JSONField()

    def create(self, validated_data):
        """Make case writeable (only) on creation."""
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = CasePhenotypeTerms
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "individual",
            "terms",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
        )


class CaseSerializer(CoreCaseSerializerMixin, SODARProjectModelSerializer):
    """Serializer for the ``Case`` model."""

    pedigree = serializers.models.JSONField()
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    annotationreleaseinfo_set = AnnotationReleaseInfoSerializer(many=True, read_only=True)
    svannotationreleaseinfo_set = SvAnnotationReleaseInfoSerializer(many=True, read_only=True)
    phenotype_terms = CasePhenotypeTermsSerializer(many=True, read_only=True)
    casealignmentstats = serializers.SerializerMethodField("get_casealignmentstats")
    casevariantstats = serializers.SerializerMethodField("get_casevariantstats")
    relatedness = serializers.SerializerMethodField("get_relatedness")
    sex_errors = serializers.SerializerMethodField("get_sex_errors")
    presetset = serializers.ReadOnlyField(source="presetset.sodar_uuid")
    smallvariantqueryresultset = serializers.SerializerMethodField()
    svqueryresultset = serializers.SerializerMethodField()

    def get_smallvariantqueryresultset(self, obj) -> Dict[str, Any]:
        from variants.serializers import SmallVariantQueryResultSetSerializer

        return SmallVariantQueryResultSetSerializer(
            obj.smallvariantqueryresultset_set.filter(smallvariantquery=None).first()
        ).data

    def get_svqueryresultset(self, obj) -> Dict[str, Any]:
        from svs.serializers import SvQueryResultSetSerializer

        return SvQueryResultSetSerializer(
            obj.svqueryresultset_set.filter(svquery=None).first()
        ).data

    def create(self, validated_data):
        """Make project and release writeable on creation."""
        validated_data["project"] = self.context["project"]
        validated_data["release"] = self.context["release"]
        return super().create(validated_data)

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

    def get_casealignmentstats(self, obj) -> Dict[str, Any]:
        variant_set = obj.latest_variant_set
        if variant_set:
            try:
                return variant_set.casealignmentstats.bam_stats
            except SmallVariantSet.casealignmentstats.RelatedObjectDoesNotExist:
                return None
        else:
            return None

    def get_casevariantstats(self, obj) -> Dict[str, Any]:
        keys = [
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
        ]
        result = {}
        variant_set = obj.latest_variant_set
        if variant_set:
            try:
                for var_stats in variant_set.variant_stats.sample_variant_stats.all():
                    result[var_stats.sample_name] = {key: getattr(var_stats, key) for key in keys}
            except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
                pass
        return result

    def get_relatedness(self, obj) -> Dict[str, Any]:
        keys = [
            "sample1",
            "sample2",
            "het_1_2",
            "het_1",
            "het_2",
            "n_ibs0",
            "n_ibs1",
            "n_ibs2",
        ]
        result = []
        variant_set = obj.latest_variant_set
        if variant_set:
            try:
                for relatedness in variant_set.variant_stats.relatedness.all():
                    result.append({key: getattr(relatedness, key) for key in keys})
            except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
                pass
        return result

    def get_sex_errors(self, obj) -> Dict[str, List[str]]:
        return obj.sex_errors()

    class Meta:
        model = Case
        fields = (
            "sodar_uuid",
            "project",
            "date_created",
            "date_modified",
            "release",
            "name",
            "index",
            "pedigree",
            "num_small_vars",
            "num_svs",
            "project",
            "notes",
            "status",
            "tags",
            "annotationreleaseinfo_set",
            "svannotationreleaseinfo_set",
            "phenotype_terms",
            "casealignmentstats",
            "casevariantstats",
            "relatedness",
            "sex_errors",
            "presetset",
            "case_version",
            "smallvariantqueryresultset",
            "svqueryresultset",
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
            "annotationreleaseinfo_set",
            "svannotationreleaseinfo_set",
            "phenotype_terms",
            "casealignmentstats",
            "casevariantstats",
            "relatedness",
            "sex_errors",
            "presetset",  # made writable in to_internal_value
        )


class ExportFileBgJobSerializer(SODARModelSerializer):
    """Sparse serialization of the ``ExportFileBgJob`` model."""

    # Fetch the status of the underlying ``BackgroundJob`` model.
    status = serializers.ReadOnlyField(source="bg_job.status")

    class Meta:
        model = ExportFileBgJob
        fields = ("sodar_uuid", "file_type", "status")

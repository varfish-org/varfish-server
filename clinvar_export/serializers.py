from typing import Dict, List, Literal, Optional
from django.shortcuts import get_object_or_404
from projectroles.serializers import SODARModelSerializer, SODARProjectModelSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import Serializer

from geneinfo.models import Hgnc, Hpo, HpoName
from variants.models import (
    AcmgCriteriaRating,
    Case,
    CasePhenotypeTerms,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
)

from .models import (
    AssertionMethod,
    ClinVarReport,
    Family,
    Individual,
    Organisation,
    Submission,
    SubmissionIndividual,
    SubmissionSet,
    Submitter,
    SubmittingOrg,
)


def resolve_term_id(term_id: str) -> Dict[Literal["term_id", "term_name"], str]:
    """Resolve phenotype/disease term ID ``term_id``."""
    term_name = term_id
    if term_id.startswith("HP"):
        hpo_name = HpoName.objects.filter(hpo_id=term_id).first()
        if hpo_name:
            term_name = hpo_name.name
    else:
        res = Hpo.objects.filter(database_id=term_id).values("name").order_by("name").first()
        if res:
            term_name = res["name"]
    return {"term_id": term_id, "term_name": term_name}


class WriteOnceMixin:
    """Adds support for write once fields to serializers.

    To use it, specify a list of fields as `write_once_fields` on the serializer's Meta::

        class Meta:
            model = SomeModel
            fields = '__all__'
            write_once_fields = ('collection', )

    Now the fields in `write_once_fields` can be set during POST (create), but cannot be changed afterwards via PUT or
    PATCH (update).  Inspired by http://stackoverflow.com/a/37487134/627411.
    """

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()

        # We're only interested in PATCH/PUT.
        if "update" in getattr(self.context.get("view"), "action", ""):
            return self._set_write_once_fields(extra_kwargs)

        return extra_kwargs

    def _set_write_once_fields(self, extra_kwargs):
        """Set all fields in `Meta.write_once_fields` to read_only."""
        write_once_fields = getattr(self.Meta, "write_once_fields", None)
        if not write_once_fields:
            return extra_kwargs

        if not isinstance(write_once_fields, (list, tuple)):
            raise TypeError(
                "The `write_once_fields` option must be a list or tuple. "
                "Got {}.".format(type(write_once_fields).__name__)
            )

        for field_name in write_once_fields:
            kwargs = extra_kwargs.get(field_name, {})
            kwargs["read_only"] = True
            extra_kwargs[field_name] = kwargs

        return extra_kwargs


class FamilySerializer(SODARProjectModelSerializer):
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    class Meta:
        model = Family
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "project",
            "case",
            "case_name",
            "pedigree",
        )
        read_only_fields = fields


class IndividualSerializer(SODARProjectModelSerializer):
    family = serializers.ReadOnlyField(source="family.sodar_uuid")
    phenotype_terms = serializers.SerializerMethodField()

    def get_phenotype_terms(self, obj) -> Optional[List[str]]:
        """Return related phenotypes."""

        # TODO: speedup
        if obj.family.case:
            record = CasePhenotypeTerms.objects.filter(
                case=obj.family.case, individual=obj.name
            ).first()
            if record:
                return list(map(resolve_term_id, record.terms or []))
        return None

    class Meta:
        model = Individual
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "family",
            "name",
            "affected",
            "taxonomy_id",
            "sex",
            "phenotype_terms",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "family",
        )


class SubmissionIndividualSerializer(SODARProjectModelSerializer):
    individual = serializers.CharField(source="individual.sodar_uuid")
    submission = serializers.CharField(source="submission.sodar_uuid")

    def create(self, validated_data):
        project = self.context["project"]
        validated_data["individual"] = get_object_or_404(
            Individual.objects.filter(family__project=project),
            sodar_uuid=validated_data.pop("individual")["sodar_uuid"],
        )
        validated_data["submission"] = get_object_or_404(
            Submission.objects.filter(submission_set__project=project),
            sodar_uuid=validated_data.pop("submission")["sodar_uuid"],
        )
        return SubmissionIndividual.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("individual", None)
        validated_data.pop("submission", None)
        return super().update(instance, validated_data)

    class Meta:
        model = SubmissionIndividual
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "sort_order",
            "individual",
            "submission",
            "phenotypes",
            "source",
            "tissue",
            "citations",
            "variant_origin",
            "variant_allele_count",
            "variant_zygosity",
        )
        read_only_fields = ("sodar_uuid", "date_created", "date_modified")


class AssertionMethodSerializer(SODARModelSerializer):
    class Meta:
        model = AssertionMethod
        fields = ("sodar_uuid", "date_created", "date_modified", "is_builtin", "title", "reference")
        read_only_fields = fields


class SubmitterSerializer(SODARModelSerializer):
    class Meta:
        model = Submitter
        fields = ("sodar_uuid", "date_created", "date_modified", "clinvar_id", "name")
        read_only_fields = fields


class OrganisationSerializer(SODARModelSerializer):
    class Meta:
        model = Organisation
        fields = ("sodar_uuid", "date_created", "date_modified", "clinvar_id", "name")
        read_only_fields = fields


class ProjectLimitedSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        if "project" in self.context:
            return self.queryset.filter(project=self.context["project"])
        else:
            return self.queryset.none()


class SubmissionSerializer(SODARProjectModelSerializer):
    submission_set = serializers.CharField(source="submission_set.sodar_uuid")
    assertion_method = serializers.CharField(source="assertion_method.sodar_uuid")
    submission_individuals = serializers.SlugRelatedField(
        slug_field="sodar_uuid", many=True, read_only=True
    )

    def create(self, validated_data):
        project = self.context["project"]
        validated_data["submission_set"] = get_object_or_404(
            SubmissionSet.objects.filter(project=project),
            sodar_uuid=validated_data.pop("submission_set", {}).get("sodar_uuid"),
        )
        validated_data["assertion_method"] = get_object_or_404(
            AssertionMethod.objects.all(),
            sodar_uuid=validated_data.pop("assertion_method", {}).get("sodar_uuid"),
        )
        return Submission.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("submission_set", None)
        if "assertion_method" in validated_data:
            validated_data["assertion_method"] = get_object_or_404(
                AssertionMethod.objects.all(),
                sodar_uuid=validated_data.pop("assertion_method", {}).get("sodar_uuid"),
            )
        return super().update(instance, validated_data)

    class Meta:
        model = Submission
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "submission_set",
            "sort_order",
            "record_status",
            "release_status",
            "assertion_method",
            "significance_status",
            "significance_description",
            "significance_last_evaluation",
            "assertion_method",
            "inheritance",
            "age_of_onset",
            "variant_type",
            "variant_assembly",
            "variant_chromosome",
            "variant_start",
            "variant_stop",
            "variant_reference",
            "variant_alternative",
            "variant_gene",
            "variant_hgvs",
            "submission_individuals",
            "diseases",
            "clinvar_submitter_report",
            "clinvar_error_report",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "clinvar_submitter_report",
            "clinvar_error_report",
        )


class SubmissionSetSerializer(SODARProjectModelSerializer):
    project = serializers.ReadOnlyField(source="project.sodar_uuid")
    submitter = serializers.SlugRelatedField(
        slug_field="sodar_uuid", queryset=Submitter.objects.all()
    )
    submitting_orgs = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="sodar_uuid"
    )
    submissions = serializers.SlugRelatedField(many=True, read_only=True, slug_field="sodar_uuid")

    def create(self, validated_data):
        validated_data["project"] = self.context["project"]
        return super().create(validated_data)

    class Meta:
        model = SubmissionSet
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "project",
            "submitter",
            "title",
            "submitting_orgs",
            "submissions",
            "state",
        )
        read_only_fields = ("sodar_uuid", "data_created", "date_modified", "project", "submissions")


class SubmittingOrgSerializer(SODARModelSerializer):
    organisation = serializers.SlugRelatedField(
        slug_field="sodar_uuid", queryset=Organisation.objects.all()
    )
    submission_set = ProjectLimitedSlugRelatedField(
        slug_field="sodar_uuid", queryset=SubmissionSet.objects.all()
    )

    class Meta:
        model = SubmittingOrg
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "sort_order",
            "organisation",
            "submission_set",
        )
        read_only_fields = ("sodar_uuid", "data_created", "date_modified")


#: Genomic coordinate fields.
GENOMIC_COORDINATES = [
    "release",
    "chromosome",
    "start",
    "end",
    "reference",
    "alternative",
]


class SmallVariantSerializer(SODARModelSerializer):
    refseq_gene_symbol = SerializerMethodField()
    ensembl_gene_symbol = SerializerMethodField()
    case_name = SerializerMethodField()

    def get_refseq_gene_symbol(self, obj):
        hgnc = Hgnc.objects.filter(entrez_id=obj.refseq_gene_id).first()
        if hgnc:
            return hgnc.symbol
        else:
            return None

    def get_ensembl_gene_symbol(self, obj):
        hgnc = Hgnc.objects.filter(ensembl_gene_id=obj.ensembl_gene_id).first()
        if hgnc:
            return hgnc.symbol
        else:
            return None

    def get_case_name(self, instance):
        case = Case.objects.get(id=instance.case_id)
        if case:
            return case.name
        else:
            return None

    class Meta:
        model = SmallVariant
        fields = GENOMIC_COORDINATES + [
            "case_name",
            "chromosome_no",
            "genotype",
            "refseq_gene_id",
            "refseq_gene_symbol",
            "refseq_transcript_id",
            "refseq_transcript_coding",
            "refseq_hgvs_c",
            "refseq_hgvs_p",
            "refseq_effect",
            "refseq_exon_dist",
            "ensembl_gene_id",
            "ensembl_gene_symbol",
            "ensembl_transcript_id",
            "ensembl_transcript_coding",
            "ensembl_hgvs_c",
            "ensembl_hgvs_p",
            "ensembl_effect",
            "ensembl_exon_dist",
        ]
        read_only_fields = fields


class SmallVariantFlagsSerializer(SODARModelSerializer):
    case_name = serializers.ReadOnlyField(source="case.name")

    class Meta:
        model = SmallVariantFlags
        fields = (
            ["sodar_uuid"]
            + GENOMIC_COORDINATES
            + [
                "case_name",
                "flag_bookmarked",
                "flag_candidate",
                "flag_final_causative",
                "flag_for_validation",
                "flag_no_disease_association",
                "flag_segregates",
                "flag_doesnt_segregate",
                "flag_visual",
                "flag_molecular",
                "flag_validation",
                "flag_phenotype_match",
                "flag_summary",
            ]
        )
        read_only_fields = fields


class SmallVariantCommentsSerializer(SODARModelSerializer):
    case_name = serializers.ReadOnlyField(source="case.name")
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = SmallVariantComment
        fields = ["sodar_uuid"] + GENOMIC_COORDINATES + ["text", "user", "case_name"]
        read_only_fields = fields


class AcmgCriteriaRatingSerializer(SODARModelSerializer):
    case_name = serializers.ReadOnlyField(source="case.name")
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = AcmgCriteriaRating
        fields = (
            ["sodar_uuid"]
            + GENOMIC_COORDINATES
            + [
                "case_name",
                "user",
                "pvs1",
                "ps1",
                "ps2",
                "ps3",
                "ps4",
                "pm1",
                "pm2",
                "pm3",
                "pm4",
                "pm5",
                "pm6",
                "pp1",
                "pp2",
                "pp3",
                "pp4",
                "pp5",
                "ba1",
                "bs2",
                "bs3",
                "bs4",
                "bp1",
                "bp2",
                "bp3",
                "bp4",
                "bp6",
                "bp7",
                "class_auto",
                "class_override",
            ]
        )
        read_only_fields = fields


class AnnotatedSmallVariantsSerializer(Serializer):
    """Serialization of ``clinvar_export.queries.AnnotatedSmallVariants``."""

    small_variants = SmallVariantSerializer(read_only=True, many=True)
    small_variant_flags = SmallVariantFlagsSerializer(read_only=True, many=True)
    small_variant_comments = SmallVariantCommentsSerializer(read_only=True, many=True)
    acmg_criteria_rating = AcmgCriteriaRatingSerializer(read_only=True, many=True)


class ClinVarReportSerializer(SODARModelSerializer):
    """Serializer for ``ClinVarReport``."""

    #: Serialize the SubmissionSet as its SODAR UUID.
    submission_set = serializers.ReadOnlyField(source="submission_set.sodar_uuid")

    class Meta:
        model = ClinVarReport
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "submission_set",
            "report_type",
            "source_url",
            "payload_md5",
            "payload",
        )
        read_only_fields = fields

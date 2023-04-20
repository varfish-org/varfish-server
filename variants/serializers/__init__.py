"""Serializers for the variants app."""

# TODO: rename pedigree entry field "patient" also internally to name and get rid of translation below
import copy
import typing

import attrs
from django.db.models import Q
from projectroles.serializers import SODARModelSerializer
from rest_framework import serializers

from clinvar.models import Clinvar
from extra_annos.models import ExtraAnno
from geneinfo.models import Hgnc, Hpo, HpoName
from geneinfo.serializers import GeneSerializer
from genepanels.models import expand_panels_in_gene_list
from variants.forms import FilterForm
from variants.models import (
    AcmgCriteriaRating,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantQueryGeneScores,
    SmallVariantQueryVariantScores,
)
from variants.query_schemas import (
    SCHEMA_QUERY_V1,
    DefaultValidatingDraft7Validator,
    convert_query_json_to_small_variant_filter_form_v1,
)
from variants.serializers.case import *  # noqa: F401 F403
from variants.serializers.presets import *  # noqa: F401 F403


def create_only_validator(value, serializer_field):
    """https://github.com/encode/django-rest-framework/issues/5745"""
    instance = serializer_field.parent.instance
    if instance is not None:
        initial = serializer_field.get_attribute(instance)
        if initial != value:
            raise serializers.ValidationError("Can only be set when creating")


# https://www.django-rest-framework.org/api-guide/validators/#accessing-the-context
create_only_validator.requires_context = True


def query_settings_validator(value):
    """Validate query settings using JSON schema as well as gene and HPO term lookup."""

    def _check_gene_list_found(gene_list, label):
        """Helper that checks whether all ENSEMBL/Entrez gene IDs or HGNC symbols in gene_list can be found."""
        if not gene_list:
            return
        # Extend gene list with those from genepanels app.
        proc_gene_list = expand_panels_in_gene_list(gene_list)
        records = Hgnc.objects.filter(
            Q(ensembl_gene_id__in=proc_gene_list)
            | Q(entrez_id__in=proc_gene_list)
            | Q(symbol__in=proc_gene_list)
        )
        result = []
        for record in records:
            result += [record.ensembl_gene_id, record.entrez_id, record.symbol]
        given_set = set(proc_gene_list)
        found_set = set(result)
        not_found = given_set - found_set
        if not_found:
            raise serializers.ValidationError(f"Could not find gene(s) in {label}: {not_found}")

    # Validate query settings.
    query_settings = copy.deepcopy(value)
    DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(query_settings)
    # Validate gene lists.
    _check_gene_list_found(query_settings["gene_allowlist"], "gene_allowlist")
    _check_gene_list_found(query_settings["gene_blocklist"], "gene_blocklist")
    # Validate HPO term list.
    if "prio_hpo_terms" in query_settings:
        missing = []
        for term in query_settings["prio_hpo_terms"]:
            if term.startswith("HP"):
                if not HpoName.objects.filter(hpo_id=term).exists():
                    missing.append(term)
            else:
                if not Hpo.objects.filter(database_id=term).exists():
                    missing.append(term)
        if missing:
            raise serializers.ValidationError(f"Used invalid ids: {','.join(missing)}")


class SmallVariantQuerySerializer(SODARModelSerializer):
    """Serializer for the ``SmallVariant`` model."""

    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    user = serializers.ReadOnlyField(source="user.sodar_uuid")

    query_settings = serializers.JSONField(
        validators=[create_only_validator, query_settings_validator]
    )

    def create(self, validated_data):
        """Make case and user writeable on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        validated_data["form_version"] = FilterForm.form_version
        validated_data["form_id"] = FilterForm.form_id
        return super().create(validated_data)

    def validate(self, attrs):
        # validation succeeded up to here, now convert to form data's "query_settings" if necessary.
        if "database_select" not in attrs.get("query_settings", {}) and "query_settings" in attrs:
            attrs["query_settings"] = convert_query_json_to_small_variant_filter_form_v1(
                self.context["case"], attrs["query_settings"]
            )
        return attrs

    class Meta:
        model = SmallVariantQuery
        fields = (
            "sodar_uuid",
            "date_created",
            "case",
            "user",
            "form_id",
            "form_version",
            "query_settings",
            "name",
            "public",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "case",
            "user",
            "form_id",
            "form_version",
        )


class SmallVariantQueryUpdateSerializer(SmallVariantQuerySerializer):
    """Serializer that makes query_settings read-only."""

    query_settings = serializers.JSONField(read_only=True)


class SmallVariantForResultSerializer(serializers.ModelSerializer):
    """Serialization of ``SmallVariant`` for fetching results."""

    class Meta:
        model = SmallVariant
        fields = (
            "release",
            "chromosome",
            "start",
            "reference",
            "alternative",
            "var_type",
            "info",
            "genotype",
            "num_hom_alt",
            "num_hom_ref",
            "num_het",
            "num_hemi_alt",
            "num_hemi_ref",
            "in_clinvar",
            "exac_frequency",
            "exac_homozygous",
            "exac_heterozygous",
            "exac_hemizygous",
            "thousand_genomes_frequency",
            "thousand_genomes_homozygous",
            "thousand_genomes_heterozygous",
            "thousand_genomes_hemizygous",
            "gnomad_exomes_frequency",
            "gnomad_exomes_homozygous",
            "gnomad_exomes_heterozygous",
            "gnomad_exomes_hemizygous",
            "gnomad_genomes_frequency",
            "gnomad_genomes_homozygous",
            "gnomad_genomes_heterozygous",
            "gnomad_genomes_hemizygous",
            "refseq_gene_id",
            "refseq_transcript_id",
            "refseq_transcript_coding",
            "refseq_hgvs_c",
            "refseq_hgvs_p",
            "refseq_effect",
            "refseq_exon_dist",
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "ensembl_transcript_coding",
            "ensembl_hgvs_c",
            "ensembl_hgvs_p",
            "ensembl_effect",
            "ensembl_exon_dist",
        )


class SmallVariantForExtendedResultSerializer(serializers.Serializer):
    """Serializer for fetching extended query results."""

    # SmallVariant model fields
    release = serializers.CharField()
    chromosome = serializers.CharField()
    chromosome_no = serializers.IntegerField()
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    bin = serializers.IntegerField()
    reference = serializers.CharField()
    alternative = serializers.CharField()
    var_type = serializers.CharField()
    info = serializers.JSONField(default=dict)
    genotype = serializers.JSONField()
    num_hom_alt = serializers.IntegerField(default=0)
    num_hom_ref = serializers.IntegerField(default=0)
    num_het = serializers.IntegerField(default=0)
    num_hemi_alt = serializers.IntegerField(default=0)
    num_hemi_ref = serializers.IntegerField(default=0)
    in_clinvar = serializers.BooleanField(allow_null=True)
    exac_frequency = serializers.FloatField(allow_null=True)
    exac_homozygous = serializers.IntegerField(allow_null=True)
    exac_heterozygous = serializers.IntegerField(allow_null=True)
    exac_hemizygous = serializers.IntegerField(allow_null=True)
    thousand_genomes_frequency = serializers.FloatField(allow_null=True)
    thousand_genomes_homozygous = serializers.IntegerField(allow_null=True)
    thousand_genomes_heterozygous = serializers.IntegerField(allow_null=True)
    thousand_genomes_hemizygous = serializers.IntegerField(allow_null=True)
    gnomad_exomes_frequency = serializers.FloatField(allow_null=True)
    gnomad_exomes_homozygous = serializers.IntegerField(allow_null=True)
    gnomad_exomes_heterozygous = serializers.IntegerField(allow_null=True)
    gnomad_exomes_hemizygous = serializers.IntegerField(allow_null=True)
    gnomad_genomes_frequency = serializers.FloatField(allow_null=True)
    gnomad_genomes_homozygous = serializers.IntegerField(allow_null=True)
    gnomad_genomes_heterozygous = serializers.IntegerField(allow_null=True)
    gnomad_genomes_hemizygous = serializers.IntegerField(allow_null=True)
    refseq_gene_id = serializers.CharField(allow_null=True)
    refseq_transcript_id = serializers.CharField(allow_null=True)
    ensembl_gene_id = serializers.CharField(allow_null=True)
    ensembl_transcript_id = serializers.CharField(allow_null=True)
    # SmallVariant fields computed on the fly
    gene_id = serializers.CharField(allow_null=True)
    transcript_id = serializers.CharField(allow_null=True)
    transcript_coding = serializers.BooleanField(allow_null=True)
    hgvs_c = serializers.CharField(allow_null=True)
    hgvs_p = serializers.CharField(allow_null=True)
    effect = serializers.ListField(allow_null=True)
    effect_ambiguity = serializers.BooleanField(allow_null=True)
    exon_dist = serializers.IntegerField(allow_null=True)

    # Joined fields (ExtendQueryPartsCaseJoinAndFilter)
    case_uuid = serializers.CharField()
    family_name = serializers.CharField()

    # Joined fields (ExtendQueryPartsMitochondrialFrequenciesJoin)
    mtdb_count = serializers.IntegerField()
    mtdb_frequency = serializers.FloatField()
    mtdb_dloop = serializers.BooleanField()
    helixmtdb_het_count = serializers.IntegerField()
    helixmtdb_hom_count = serializers.IntegerField()
    helixmtdb_frequency = serializers.FloatField()
    helixmtdb_is_triallelic = serializers.BooleanField()
    mitomap_count = serializers.IntegerField()
    mitomap_frequency = serializers.FloatField()

    # Joined fields (ExtendQueryPartsDbsnpJoin)
    rsid = serializers.CharField()

    # Joined fields (ExtendQueryPartsHgncJoin)
    symbol = serializers.CharField()
    gene_name = serializers.CharField()
    gene_family = serializers.CharField()
    pubmed_id = serializers.CharField()
    hgnc_id = serializers.CharField()
    uniprot_ids = serializers.CharField()

    # Joined fields (ExtendQueryPartsGeneSymbolJoin)
    gene_symbol = serializers.CharField()

    # Joined fields (ExtendQueryPartsAcmgJoin)
    acmg_symbol = serializers.CharField()

    # Joined fields (ExtendQueryPartsMgiJoin)
    mgi_id = serializers.CharField()

    # Joined fields (ExtendQueryPartsFlagsJoinAndFilter)
    flag_count = serializers.IntegerField()
    flag_bookmarked = serializers.BooleanField()
    flag_candidate = serializers.BooleanField()
    flag_segregates = serializers.BooleanField()
    flag_doesnt_segregate = serializers.BooleanField()
    flag_final_causative = serializers.BooleanField()
    flag_for_validation = serializers.BooleanField()
    flag_no_disease_association = serializers.BooleanField()
    flag_molecular = serializers.CharField()
    flag_visual = serializers.CharField()
    flag_validation = serializers.CharField()
    flag_phenotype_match = serializers.CharField()
    flag_summary = serializers.CharField()

    # Joined fields (ExtendQueryPartsCommentsJoin)
    comment_count = serializers.IntegerField()

    # Joined fields (ExtendQueryPartsCommentsExtraAnnoJoin)
    extra_annos = serializers.ListField()

    # Joined fields (ExtendQueryPartsAcmgCriteriaJoin)
    acmg_class_auto = serializers.IntegerField()
    acmg_class_override = serializers.IntegerField()

    # Joined fields (ExtendQueryPartsModesOfInheritanceJoin)
    modes_of_inheritance = serializers.ListField()

    # Joined fields (ExtendQueryPartsDiseaseGeneJoin)
    disease_gene = serializers.CharField()

    # Joined fields (ExtendQueryPartsGnomadConstraintsJoin)
    gnomad_pLI = serializers.FloatField()
    gnomad_mis_z = serializers.FloatField()
    gnomad_syn_z = serializers.FloatField()
    gnomad_oe_lof = serializers.FloatField()
    gnomad_oe_lof_upper = serializers.FloatField()
    gnomad_oe_lof_lower = serializers.FloatField()
    gnomad_loeuf = serializers.FloatField()

    # Joined fields (ExtendQueryPartsExacConstraintsJoin)
    exac_pLI = serializers.FloatField()
    exac_mis_z = serializers.FloatField()
    exac_syn_z = serializers.FloatField()

    # Joined fields (ExtendQueryPartsExacConstraintsJoin)
    inhouse_hom_ref = serializers.IntegerField()
    inhouse_het = serializers.IntegerField()
    inhouse_hom_alt = serializers.IntegerField()
    inhouse_hemi_ref = serializers.IntegerField()
    inhouse_hemi_alt = serializers.IntegerField()
    inhouse_carriers = serializers.IntegerField()

    # Joined fields (ExtendQueryPartsClinvarJoin)
    variation_type = serializers.CharField()
    vcv = serializers.CharField()
    summary_review_status_label = serializers.CharField()
    summary_pathogenicity_label = serializers.CharField()
    summary_pathogenicity = serializers.ListField()
    summary_gold_stars = serializers.IntegerField()
    details = serializers.ListField()


class CaddPrioritizationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pathogenicity_score"] = serializers.SerializerMethodField()
        self._pathogenicity_scores = {
            (row.chromosome, row.start, row.reference, row.alternative): row.score
            for row in SmallVariantQueryVariantScores.objects.filter(
                query__sodar_uuid=self.context["request"].parser_context["kwargs"][
                    "smallvariantquery"
                ],
            )
        }

    def get_pathogenicity_score(self, obj):
        """Corresponds to the ``pathogenicity_score`` field defined above.

        The purpose is to add the pathogenicity score (if available) as they are not part of the query.
        TODO This solution is very inefficient. It should be moved to the query itself.
        """
        return self._pathogenicity_scores[
            (obj.chromosome, obj.start, obj.reference, obj.alternative)
        ]


class PhenoPrioritizationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phenotype_score"] = serializers.SerializerMethodField()
        self._phenotype_scores = {
            row.gene_id: row.score
            for row in SmallVariantQueryGeneScores.objects.filter(
                query__sodar_uuid=self.context["request"].parser_context["kwargs"][
                    "smallvariantquery"
                ],
            )
        }

    def get_phenotype_score(self, obj):
        """Corresponds to the ``phenotype_score`` field defined above.

        The purpose is to add the phenotype score (if available) as they are not part of the query.
        TODO This solution is very inefficient. It should be moved to the query itself.
        """
        return self._phenotype_scores[obj.entrez_id]


class SmallVariantForExtendedResultsCaddPriorizationSerializer(
    CaddPrioritizationMixin, SmallVariantForExtendedResultSerializer
):
    """Serializer for fetching extended query results."""


class SmallVariantForExtendedResultsPhenoPriorizationSerializer(
    PhenoPrioritizationMixin, SmallVariantForExtendedResultSerializer
):
    """Serializer for fetching extended query results."""


class SmallVariantForExtendedResultsCaddPhenoPriorizationSerializer(
    CaddPrioritizationMixin, PhenoPrioritizationMixin, SmallVariantForExtendedResultSerializer
):
    """Serializer for fetching extended query results."""

    #: Serialize the cases that reference the project
    patho_pheno_score = serializers.SerializerMethodField()

    def get_patho_pheno_score(self, obj):
        return self.get_phenotype_score(obj) * self.get_pathogenicity_score(obj)


@attrs.define
class HpoTerms:

    hpoterms: typing.Dict[str, typing.Any]


class SmallVariantQueryHpoTermSerializer(serializers.Serializer):
    """Serializer for fetching HPO terms of a query."""

    hpoterms = serializers.JSONField()


@attrs.define
class SettingsShortcuts:
    """Helper class that contains the results of the settings shortcuts"""

    presets: typing.Dict[str, str]
    query_settings: typing.Dict[str, typing.Any]


class SettingsShortcutsSerializer(serializers.Serializer):
    """Serializer for ``SettingsShortcut``"""

    presets = serializers.JSONField()
    query_settings = serializers.JSONField()


@attrs.define
class JobStatus:
    status: typing.Optional[str] = None
    logs: typing.List[str] = None


class SmallVariantQueryStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)
    logs = serializers.ListField()


class ClinvarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinvar
        fields = (
            "release",
            "chromosome",
            "start",
            "end",
            "bin",
            "reference",
            "alternative",
            "clinvar_version",
            "set_type",
            "variation_type",
            "symbols",
            "hgnc_ids",
            "vcv",
            "summary_clinvar_review_status_label",
            "summary_clinvar_pathogenicity_label",
            "summary_clinvar_pathogenicity",
            "summary_clinvar_gold_stars",
            "summary_paranoid_review_status_label",
            "summary_paranoid_pathogenicity_label",
            "summary_paranoid_pathogenicity",
            "summary_paranoid_gold_stars",
            "details",
        )


class ExtraAnnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraAnno
        fields = (
            "release",
            "chromosome",
            "start",
            "end",
            "bin",
            "reference",
            "alternative",
            "anno_data",
        )


class AcmgCriteriaRatingSerializer(serializers.ModelSerializer):

    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    def create(self, validated_data):
        """Make case and user writeable on creation."""
        validated_data["user"] = self.context["request"].user
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = AcmgCriteriaRating
        fields = (
            "user",
            "case",
            "date_created",
            "date_modified",
            "sodar_uuid",
            "release",
            "chromosome",
            "start",
            "end",
            "bin",
            "reference",
            "alternative",
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
            "bs1",
            "bs2",
            "bs3",
            "bs4",
            "bp1",
            "bp2",
            "bp3",
            "bp4",
            "bp5",
            "bp6",
            "bp7",
            "class_auto",
            "class_override",
            "acmg_class",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
        )


@attrs.define
class SmallVariantDetails:
    clinvar: typing.Dict[str, typing.Any] = None
    knowngeneaa: typing.List[typing.Dict[str, typing.Any]] = None
    effect_details: typing.Dict[str, typing.Any] = None
    extra_annos: typing.Dict[str, typing.Any] = None
    pop_freqs: typing.Dict[str, typing.Any] = None
    populations: typing.List[str] = None
    inhouse_freq: typing.Dict[str, typing.Any] = None
    mitochondrial_freqs: typing.Dict[str, typing.Any] = None
    gene: typing.Dict[str, typing.Any] = None
    flags: typing.Dict[str, typing.Any] = None
    acmg_rating: typing.Dict[str, typing.Any] = None


class SmallVariantCommentSerializer(SODARModelSerializer):
    """Serializer for the ``SmallVariantComment`` model."""

    case = serializers.ReadOnlyField(source="case.sodar_uuid")
    user_can_edit = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    def create(self, validated_data):
        """Make case and user writeable on creation."""
        validated_data["user"] = self.context["request"].user
        keys = ("case", "release", "chromosome", "start", "end", "reference", "alternative")
        for key in keys:
            validated_data[key] = self.context[key]
        return super().create(validated_data)

    def get_user_can_edit(self, instance):
        return (
            self.context["request"].user.is_superuser
            or self.context["request"].user == instance.user
        )

    class Meta:
        model = SmallVariantComment
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
            "release",
            "chromosome",
            "chromosome_no",
            "start",
            "end",
            "bin",
            "reference",
            "alternative",
            "text",
            "user_can_edit",
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "user",
        )


class SmallVariantFlagsSerializer(SODARModelSerializer):
    """Serializer for the ``SmallVariantFlags`` model."""

    case = serializers.ReadOnlyField(source="case.sodar_uuid")

    def create(self, validated_data):
        """Make case writeable on creation."""
        validated_data["case"] = self.context["case"]
        return super().create(validated_data)

    class Meta:
        model = SmallVariantFlags
        fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
            "release",
            "chromosome",
            "chromosome_no",
            "start",
            "end",
            "bin",
            "reference",
            "alternative",
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
        )
        read_only_fields = (
            "sodar_uuid",
            "date_created",
            "date_modified",
            "case",
        )


class SmallVariantDetailsSerializer(serializers.Serializer):
    clinvar = ClinvarSerializer(many=True)
    knowngeneaa = serializers.JSONField()
    effect_details = serializers.JSONField()
    extra_annos = ExtraAnnoSerializer()
    pop_freqs = serializers.JSONField()
    populations = serializers.JSONField()
    inhouse_freq = serializers.JSONField()
    mitochondrial_freqs = serializers.JSONField()
    gene = GeneSerializer()
    acmg_rating = AcmgCriteriaRatingSerializer()


class QuickPresetSerializer(serializers.BaseSerializer):
    inheritance = serializers.CharField()
    frequency = serializers.CharField()
    impact = serializers.CharField()
    chromosomes = serializers.CharField()
    flagsetc = serializers.CharField()

    def to_representation(self, instance):
        return {
            "inheritance": instance.inheritance,
            "frequency": instance.frequency,
            "impact": instance.impact,
            "chromosomes": instance.chromosomes,
            "flagsetc": instance.flagsetc,
        }

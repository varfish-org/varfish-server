from functools import lru_cache

from django import forms
from genomicfeatures.models import TadSet
from svs.models import StructuralVariantFlags, StructuralVariantComment

from variants.forms import VariantGeneListFilterFormMixin, FAIL, only_source_name


FILTER_FORM_TRANSLATE_EFFECTS = {
    "effect_coding_sequence_variant": "coding_sequence_variant",
    "effect_coding_transcript_intron_variant": "coding_transcript_intron_variant",
    "effect_coding_transcript_variant": "coding_transcript_variant",
    "effect_copy_number_change": "copy_number_change",
    "effect_direct_tandem_duplication": "direct_tandem_duplication",
    "effect_downstream_gene_variant": "downstream_gene_variant",
    "effect_exon_loss_variant": "exon_loss_variant",
    "effect_feature_truncation": "feature_truncation",
    "effect_five_prime_UTR_exon_variant": "5_prime_UTR_exon_variant",
    "effect_five_prime_UTR_intron_variant": "5_prime_UTR_intron_variant",
    "effect_five_prime_UTR_truncation": "5_prime_UTR_truncation",
    "effect_frameshift_truncation": "frameshift_truncation",
    "effect_insertion": "insertion",
    "effect_intron_variant": "intron_variant",
    "effect_inversion": "inversion",
    "effect_mobile_element_deletion": "mobile_element_deletion",
    "effect_mobile_element_insertion": "mobile_element_insertion",
    "effect_non_coding_transcript_exon_variant": "non_coding_transcript_exon_variant",
    "effect_non_coding_transcript_intron_variant": "non_coding_transcript_intron_variant",
    "effect_non_coding_transcript_variant": "non_coding_transcript_variant",
    "effect_sequence_variant": "sequence_variant",
    "effect_start_lost": "start_lost",
    "effect_stop_lost": "stop_lost",
    "effect_structural_variant": "structural_variant",
    "effect_three_prime_UTR_exon_variant": "3_prime_UTR_exon_variant",
    "effect_three_prime_UTR_intron_variant": "3_prime_UTR_intron_variant",
    "effect_three_prime_UTR_truncation": "3_prime_UTR_truncation",
    "effect_transcript_ablation": "transcript_ablation",
    "effect_transcript_amplification": "transcript_amplification",
    "effect_translocation": "translocation",
    "effect_upstream_gene_variant": "upstream_gene_variant",
}

FILTER_FORM_TRANSLATE_SV_TYPES = {
    "sv_type_del": "DEL",
    "sv_type_dup": "DUP",
    "sv_type_inv": "INV",
    "sv_type_ins": "INS",
    "sv_type_bnd": "BND",
    "sv_type_cnv": "CNV",
}


FILTER_FORM_TRANSLATE_SV_SUB_TYPES = {
    "sv_sub_type_del": "DEL",
    "sv_sub_type_del_me": "DEL:ME",
    "sv_sub_type_del_me_sva": "DEL:ME:SVA",
    "sv_sub_type_del_me_l1": "DEL:ME:L1",
    "sv_sub_type_del_me_alu": "DEL:ME:ALU",
    "sv_sub_type_dup": "DUP",
    "sv_sub_type_dup_tandem": "DUP:TANDEM",
    "sv_sub_type_inv": "INV",
    "sv_sub_type_ins": "INS",
    "sv_sub_type_ins_me": "INS:ME",
    "sv_sub_type_ins_me_sva": "INS:ME:SVA",
    "sv_sub_type_ins_me_l1": "INS:ME:L1",
    "sv_sub_type_ins_me_alu": "INS:ME:ALU",
    "sv_sub_type_bnd": "BND",
    "sv_sub_type_cnv": "CNV",
}


INHERITANCE = [
    ("any", "any"),
    ("ref", "0/0"),
    ("het", "0/1"),
    ("hom", "1/1"),
    ("variant", "variant"),
    ("non-variant", "non-variant"),
    ("non-reference", "non-reference"),
]


FILTER_FORM_TRANSLATE_REGULATORY = {
    "regulatory_ensembl_any_feature": "any_feature",
    "regulatory_ensembl_ctcf_binding_site": "CTCF_binding_site",
    "regulatory_ensembl_enhancer": "enhancer",
    "regulatory_ensembl_open_chromatin_region": "open_chromatin_region",
    "regulatory_ensembl_promoter": "promoter",
    "regulatory_ensembl_promoter_flanking_region": "promoter_flanking_region",
    "regulatory_ensembl_tf_binding_site": "TF_binding_site",
    "regulatory_vista_any_validation": "any_validation",
    "regulatory_vista_positive": "positive",
    "regulatory_vista_negative": "negative",
}


class SvAnalysisCollectiveFrequencyMixin:
    """Mixin for the frequency fields of the structural variant filtration form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["collective_enabled"] = forms.BooleanField(
            label="", required=False, initial=True
        )
        self.fields["cohort_background_carriers_min"] = forms.IntegerField(
            label="",
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Minimal background carriers in analysis collective"}
            ),
        )
        self.fields["cohort_background_carriers_max"] = forms.IntegerField(
            label="",
            initial=0,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal background carriers in analysis collective"}
            ),
        )
        self.fields["cohort_affected_carriers_min"] = forms.IntegerField(
            label="",
            initial=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(attrs={"placeholder": "Minimal affected carriers in pedigree"}),
        )
        self.fields["cohort_affected_carriers_max"] = forms.IntegerField(
            label="",
            min_value=0,
            required=False,
            widget=forms.TextInput(attrs={"placeholder": "Maximal affected carriers in pedigree"}),
        )
        self.fields["cohort_unaffected_carriers_min"] = forms.IntegerField(
            label="",
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Minimal unaffected carriers in pedigree"}
            ),
        )
        self.fields["cohort_unaffected_carriers_max"] = forms.IntegerField(
            label="",
            initial=0,
            min_value=0,
            required=False,
            widget=forms.TextInput(attrs={"placeholder": "Maximal affected carriers in pedigree"}),
        )


class SvDatabaseFrequencyMixin:
    """Mixin with fields for filtering based on databases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("DGV", "DGV GS", "ExAC", "gnomAD", "dbVar", "G1K"):
            key = name.lower().replace(" ", "_")
            entity = "alleles" if key == "g1k" else "carriers"
            self.fields["%s_enabled" % key] = forms.BooleanField(
                label="", required=False, initial=True
            )
            self.fields["%s_min_overlap" % key] = forms.DecimalField(
                label="",
                initial=0.75,
                min_value=0,
                required=True,
                widget=forms.TextInput(
                    attrs={"placeholder": "Minimal reciprocal overlap with %s (fraction)" % name}
                ),
            )
            self.fields["%s_max_%s" % (key, entity)] = forms.IntegerField(
                label="",
                initial=None,
                min_value=0,
                required=False,
                widget=forms.TextInput(attrs={"placeholder": "Maximal %s in %s" % (entity, name)}),
            )


class SvGenotypeFilterFormMixin:
    """Form mixin for inheritance/genotype fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_genotype_fields()

    @lru_cache()
    def get_member_roles(self):
        """Return mapping from donor name to trio role.

        Used for comp. het. filter.
        """
        # Build mapping from member to role, used for rendering the form
        member_roles = {}
        for member in self.get_pedigree():
            if member["patient"] == self.get_trio_roles().get("index"):
                member_roles[member["patient"]] = "index"
                member_roles[member["father"]] = "father"
                member_roles[member["mother"]] = "mother"
            elif member["patient"] not in member_roles:
                member_roles[member["patient"]] = "N/A"
        return member_roles

    @lru_cache()
    def get_genotype_field_names(self):
        """Return mapping from patient and key to field name."""
        field_names = {}
        for member in self.get_pedigree_with_samples():
            field_names.setdefault(member["patient"], {})["gt"] = "%s_gt" % member["patient"]
        return field_names

    def update_genotype_fields(self):
        """Dynamically add the fields based on the pedigree."""
        for member in self.get_pedigree_with_samples():
            name = member["patient"]
            self.fields[self.get_genotype_field_names()[name]["gt"]] = forms.CharField(
                label="",
                required=True,
                widget=forms.Select(choices=INHERITANCE, attrs={"class": "genotype-field-gt"}),
            )

    def get_pedigree(self):
        """Return ``list`` of ``dict`` with pedigree information."""
        return self.case.pedigree

    def get_pedigree_with_samples(self):
        """Return ``list`` of ``dict`` with pedigree information of samples that have variants."""
        return self.case.get_filtered_pedigree_with_samples()

    @lru_cache()
    def get_trio_roles(self):
        """Get trior ole to member mapping"""
        return self.case.get_trio_roles()


class SvVariantEffectFilterFormMixin:
    """Form mixin with variant effect etc. fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["effect_coding_sequence_variant"] = forms.BooleanField(
            label="coding sequence variant", required=False, initial=True
        )
        self.fields["effect_coding_transcript_intron_variant"] = forms.BooleanField(
            label="coding transcript intron variant", required=False, initial=True
        )
        self.fields["effect_coding_transcript_variant"] = forms.BooleanField(
            label="coding transcript variant", required=False, initial=True
        )
        self.fields["effect_copy_number_change"] = forms.BooleanField(
            label="copy number change", required=False, initial=True
        )
        self.fields["effect_direct_tandem_duplication"] = forms.BooleanField(
            label="direct tandem duplication", required=False, initial=True
        )
        self.fields["effect_downstream_gene_variant"] = forms.BooleanField(
            label="downstream gene variant", required=False, initial=True
        )
        self.fields["effect_exon_loss_variant"] = forms.BooleanField(
            label="exon loss variant", required=False, initial=True
        )
        self.fields["effect_feature_truncation"] = forms.BooleanField(
            label="feature truncation", required=False, initial=True
        )
        self.fields["effect_five_prime_UTR_exon_variant"] = forms.BooleanField(
            label="5' UTR exon variant", required=False, initial=True
        )
        self.fields["effect_five_prime_UTR_intron_variant"] = forms.BooleanField(
            label="5' UTR intron variant", required=False, initial=True
        )
        self.fields["effect_five_prime_UTR_truncation"] = forms.BooleanField(
            label="5' UTR truncation", required=False, initial=True
        )
        self.fields["effect_frameshift_truncation"] = forms.BooleanField(
            label="frameshift truncation", required=False, initial=True
        )
        self.fields["effect_insertion"] = forms.BooleanField(
            label="insertion", required=False, initial=True
        )
        self.fields["effect_intron_variant"] = forms.BooleanField(
            label="intron variant", required=False, initial=True
        )
        self.fields["effect_inversion"] = forms.BooleanField(
            label="inversions", required=False, initial=True
        )
        self.fields["effect_mobile_element_deletion"] = forms.BooleanField(
            label="mobile element deletion", required=False, initial=True
        )
        self.fields["effect_mobile_element_insertion"] = forms.BooleanField(
            label="mobile element insertion", required=False, initial=True
        )
        self.fields["effect_non_coding_transcript_exon_variant"] = forms.BooleanField(
            label="non-coding transcript exon variant", required=False, initial=True
        )
        self.fields["effect_non_coding_transcript_intron_variant"] = forms.BooleanField(
            label="non-coding transcript intron variant", required=False, initial=True
        )
        self.fields["effect_non_coding_transcript_variant"] = forms.BooleanField(
            label="non-coding transcript variant", required=False, initial=True
        )
        self.fields["effect_sequence_variant"] = forms.BooleanField(
            label="sequence variant", required=False, initial=True
        )
        self.fields["effect_start_lost"] = forms.BooleanField(
            label="start lost", required=False, initial=True
        )
        self.fields["effect_stop_lost"] = forms.BooleanField(
            label="stop lost", required=False, initial=True
        )
        self.fields["effect_structural_variant"] = forms.BooleanField(
            label="structural variant", required=False
        )
        self.fields["effect_three_prime_UTR_exon_variant"] = forms.BooleanField(
            label="3' UTR exon variant", required=False, initial=True
        )
        self.fields["effect_three_prime_UTR_intron_variant"] = forms.BooleanField(
            label="3' UTR intron variant", required=False, initial=True
        )
        self.fields["effect_three_prime_UTR_truncation"] = forms.BooleanField(
            label="3' UTR truncation", required=False, initial=True
        )
        self.fields["effect_transcript_ablation"] = forms.BooleanField(
            label="transcript ablation", required=False, initial=True
        )
        self.fields["effect_transcript_amplification"] = forms.BooleanField(
            label="transcript amplification", required=False, initial=True
        )
        self.fields["effect_translocation"] = forms.BooleanField(
            label="translocation", required=False, initial=True
        )
        self.fields["effect_upstream_gene_variant"] = forms.BooleanField(
            label="upstream gene variant", required=False, initial=True
        )

        self.fields["transcripts_coding"] = forms.BooleanField(
            label="coding transcripts", required=False, initial=True
        )
        self.fields["transcripts_noncoding"] = forms.BooleanField(
            label="non-coding transcripts", required=False, initial=True
        )
        self.fields["require_transcript_overlap"] = forms.BooleanField(
            label="require transcript overlap", required=False, initial=False
        )

        self.fields["sv_type_del"] = forms.BooleanField(label="DEL", required=False, initial=True)
        self.fields["sv_type_dup"] = forms.BooleanField(label="DUP", required=False, initial=True)
        self.fields["sv_type_inv"] = forms.BooleanField(label="INV", required=False, initial=True)
        self.fields["sv_type_ins"] = forms.BooleanField(label="INS", required=False, initial=True)
        self.fields["sv_type_bnd"] = forms.BooleanField(label="BND", required=False, initial=True)
        self.fields["sv_type_cnv"] = forms.BooleanField(label="CNV", required=False, initial=True)

        self.fields["sv_size_min"] = forms.IntegerField(label="min SV size", required=False)
        self.fields["sv_size_max"] = forms.IntegerField(label="max SV size", required=False)

        self.fields["sv_sub_type_del"] = forms.BooleanField(
            label="DEL", required=False, initial=True
        )
        self.fields["sv_sub_type_del_me"] = forms.BooleanField(
            label="DEL:ME", required=False, initial=True
        )
        self.fields["sv_sub_type_del_me_sva"] = forms.BooleanField(
            label="DEL:ME:SVA", required=False, initial=True
        )
        self.fields["sv_sub_type_del_me_l1"] = forms.BooleanField(
            label="DEL:ME:L1", required=False, initial=True
        )
        self.fields["sv_sub_type_del_me_alu"] = forms.BooleanField(
            label="DEL:ME:ALU", required=False, initial=True
        )
        self.fields["sv_sub_type_dup"] = forms.BooleanField(
            label="DUP", required=False, initial=True
        )
        self.fields["sv_sub_type_dup_tandem"] = forms.BooleanField(
            label="DUP:TANDEM", required=False, initial=True
        )
        self.fields["sv_sub_type_inv"] = forms.BooleanField(
            label="INV", required=False, initial=True
        )
        self.fields["sv_sub_type_ins"] = forms.BooleanField(
            label="INS", required=False, initial=True
        )
        self.fields["sv_sub_type_ins_me"] = forms.BooleanField(
            label="INS:ME", required=False, initial=True
        )
        self.fields["sv_sub_type_ins_me_sva"] = forms.BooleanField(
            label="INS:ME:SVA", required=False, initial=True
        )
        self.fields["sv_sub_type_ins_me_l1"] = forms.BooleanField(
            label="INS:ME:L1", required=False, initial=True
        )
        self.fields["sv_sub_type_ins_me_alu"] = forms.BooleanField(
            label="INS:ME:ALU", required=False, initial=True
        )
        self.fields["sv_sub_type_bnd"] = forms.BooleanField(
            label="BND", required=False, initial=True
        )
        self.fields["sv_sub_type_cnv"] = forms.BooleanField(
            label="CNV", required=False, initial=True
        )

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["effects"] = [
            effect for name, effect in FILTER_FORM_TRANSLATE_EFFECTS.items() if cleaned_data[name]
        ]
        cleaned_data["sv_type"] = [
            sv_type
            for name, sv_type in FILTER_FORM_TRANSLATE_SV_TYPES.items()
            if cleaned_data[name]
        ]
        cleaned_data["sv_sub_type"] = [
            sv_sub_type
            for name, sv_sub_type in FILTER_FORM_TRANSLATE_SV_SUB_TYPES.items()
            if cleaned_data[name]
        ]
        return cleaned_data


class SvQualityFilterFormMixin:
    """Form mixin for inheritance/genotype fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_quality_fields()

    @lru_cache()
    def get_quality_field_names(self):
        """Return mapping from patient and key to field name."""
        field_names = {}
        for member in self.get_pedigree_with_samples():
            for key in (
                "gq_min",
                "src_min",
                "srv_min",
                "srv_max",
                "pec_min",
                "pev_min",
                "pev_max",
                "cov_min",
                "var_min",
                "var_max",
                "fail",
            ):
                field_names.setdefault(member["patient"], {})[key] = "%s_%s" % (
                    member["patient"],
                    key,
                )
        return field_names

    def update_quality_fields(self):
        """Add and update pedigree fields."""
        # Dynamically add the fields based on the pedigree
        for member in self.get_pedigree_with_samples():
            name = member["patient"]
            self.fields[self.get_quality_field_names()[name]["gq_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-gq-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["src_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-src-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["srv_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-srv-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["srv_max"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-srv-max"}),
            )
            self.fields[self.get_quality_field_names()[name]["pec_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-pec-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["pev_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-pev-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["pev_max"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-pev-max"}),
            )
            self.fields[self.get_quality_field_names()[name]["cov_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=2,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-cov-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["var_min"]] = forms.IntegerField(
                label="",
                required=False,
                initial=2,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-var-min"}),
            )
            self.fields[self.get_quality_field_names()[name]["var_max"]] = forms.IntegerField(
                label="",
                required=False,
                initial=None,
                min_value=0,
                widget=forms.NumberInput(attrs={"class": "quality-field-var-max"}),
            )
            self.fields[self.get_quality_field_names()[name]["fail"]] = forms.CharField(
                label="",
                widget=forms.Select(choices=FAIL, attrs={"class": "quality-field-fail"}),
                required=False,
                initial="drop-variant",
            )


class SvIntervalsFilterFormMixin:
    """Form mixin for annotation based on intervals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_intervals_fields()

    def add_intervals_fields(self):
        """Add and update pedigree fields."""
        tad_sets = list(TadSet.objects.all())
        choices = [(x.sodar_uuid, x.title) for x in tad_sets]
        self.fields["tad_set_uuid"] = forms.ChoiceField(
            label="TAD set to use for annotation",
            required=False,
            initial=tad_sets[0].sodar_uuid if tad_sets else "",
            choices=[("", "-- none --")] + choices,
        )


class RegulatoryFilterFormMixin:
    """Form mixin with regulatory region mixins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["regulatory_ensembl_any_feature"] = forms.BooleanField(
            label="any feature", required=False, initial=False
        )
        self.fields["regulatory_ensembl_ctcf_binding_site"] = forms.BooleanField(
            label="CTCF binding site", required=False, initial=False
        )
        self.fields["regulatory_ensembl_enhancer"] = forms.BooleanField(
            label="enhancer", required=False, initial=False
        )
        self.fields["regulatory_ensembl_open_chromatin_region"] = forms.BooleanField(
            label="open chromatin region", required=False, initial=False
        )
        self.fields["regulatory_ensembl_promoter"] = forms.BooleanField(
            label="promoter", required=False, initial=False
        )
        self.fields["regulatory_ensembl_promoter_flanking_region"] = forms.BooleanField(
            label="promoter flanking region", required=False, initial=False
        )
        self.fields["regulatory_ensembl_tf_binding_site"] = forms.BooleanField(
            label="TF binding site", required=False, initial=False
        )

        self.fields["regulatory_vista_any_validation"] = forms.BooleanField(
            label="any feature", required=False, initial=False
        )
        self.fields["regulatory_vista_positive"] = forms.BooleanField(
            label="CTCF binding site", required=False, initial=False
        )
        self.fields["regulatory_vista_negative"] = forms.BooleanField(
            label="enhancer", required=False, initial=False
        )

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["regulatory_ensembl"] = [
            feature_type
            for name, feature_type in FILTER_FORM_TRANSLATE_REGULATORY.items()
            if cleaned_data[name] and "ensembl" in name
        ]
        cleaned_data["regulatory_vista"] = [
            feature_type
            for name, feature_type in FILTER_FORM_TRANSLATE_REGULATORY.items()
            if cleaned_data[name] and "vista" in name
        ]
        return cleaned_data


class FilterForm(
    SvDatabaseFrequencyMixin,
    SvAnalysisCollectiveFrequencyMixin,
    SvVariantEffectFilterFormMixin,
    SvGenotypeFilterFormMixin,
    SvQualityFilterFormMixin,
    VariantGeneListFilterFormMixin,
    SvIntervalsFilterFormMixin,
    RegulatoryFilterFormMixin,
    forms.Form,
):
    """This form is used for filtering structural variants of a single case."""

    #: Version of the form, used for versioning saved queries.
    form_version = 1
    #: Identifier of the form in database.
    form_id = "svs.sv_filter_form"

    #: A form field for the submit button.
    submit = forms.ChoiceField(choices=(("display", "Display results in table"),))

    DATABASE_SELECT_CHOICES = [("refseq", "RefSeq"), ("ensembl", "EnsEMBL")]
    database_select = forms.ChoiceField(
        choices=DATABASE_SELECT_CHOICES,
        widget=forms.RadioSelect(),
        initial=DATABASE_SELECT_CHOICES[0],
    )

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        super().__init__(*args, **kwargs)


class StructuralVariantFlagsForm(forms.ModelForm):
    """Form for validating structural variant flags."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = StructuralVariantFlags
        fields = (
            "flag_bookmarked",
            "flag_candidate",
            "flag_final_causative",
            "flag_for_validation",
            "flag_visual",
            "flag_validation",
            "flag_phenotype_match",
            "flag_summary",
        )


class StructuralVariantCommentForm(forms.ModelForm):
    """Form for validating structural variant comments."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = StructuralVariantComment
        fields = ("text",)

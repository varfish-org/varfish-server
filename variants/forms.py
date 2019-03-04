from functools import lru_cache
from django import forms
from .models import SmallVariantComment, SmallVariantFlags, CaseAwareProject
from .templatetags.variants_tags import only_source_name

INHERITANCE = [
    ("any", "any"),
    ("ref", "0/0"),
    ("het", "0/1"),
    ("hom", "1/1"),
    ("variant", "variant"),
    ("non-variant", "non-variant"),
    ("non-reference", "non-reference"),
]

FAIL = [("ignore", "ignore"), ("drop-variant", "drop variant"), ("no-call", "no-call")]


FILTER_FORM_TRANSLATE_EFFECTS = {
    "effect_coding_transcript_intron_variant": "coding_transcript_intron_variant",
    "effect_complex_substitution": "complex_substitution",
    "effect_direct_tandem_duplication": "direct_tandem_duplication",
    "effect_disruptive_inframe_deletion": "disruptive_inframe_deletion",
    "effect_disruptive_inframe_insertion": "disruptive_inframe_insertion",
    "effect_downstream_gene_variant": "downstream_gene_variant",
    "effect_feature_truncation": "feature_truncation",
    "effect_five_prime_UTR_exon_variant": "5_prime_UTR_exon_variant",
    "effect_five_prime_UTR_intron_variant": "5_prime_UTR_intron_variant",
    "effect_frameshift_elongation": "frameshift_elongation",
    "effect_frameshift_truncation": "frameshift_truncation",
    "effect_frameshift_variant": "frameshift_variant",
    "effect_inframe_deletion": "inframe_deletion",
    "effect_inframe_insertion": "inframe_insertion",
    "effect_intergenic_variant": "intergenic_variant",
    "effect_internal_feature_elongation": "internal_feature_elongation",
    "effect_missense_variant": "missense_variant",
    "effect_mnv": "mnv",
    "effect_non_coding_transcript_exon_variant": "non_coding_transcript_exon_variant",
    "effect_non_coding_transcript_intron_variant": "non_coding_transcript_intron_variant",
    "effect_splice_acceptor_variant": "splice_acceptor_variant",
    "effect_splice_donor_variant": "splice_donor_variant",
    "effect_splice_region_variant": "splice_region_variant",
    "effect_start_lost": "start_lost",
    "effect_stop_gained": "stop_gained",
    "effect_stop_lost": "stop_lost",
    "effect_stop_retained_variant": "stop_retained_variant",
    "effect_structural_variant": "structural_variant",
    "effect_synonymous_variant": "synonymous_variant",
    "effect_three_prime_UTR_exon_variant": "3_prime_UTR_exon_variant",
    "effect_three_prime_UTR_intron_variant": "3_prime_UTR_intron_variant",
    "effect_transcript_ablation": "transcript_ablation",
    "effect_upstream_gene_variant": "upstream_gene_variant",
}

FILTER_FORM_TRANSLATE_INHERITANCE = {
    "any": None,
    "ref": ("0/0",),
    "het": ("0/1", "1/0"),
    "hom": ("1/1",),
    "variant": ("1/0", "0/1", "1/1"),
    "non-variant": ("0/0", "./."),
    "non-reference": ("1/0", "0/1", "1/1", "./."),
}


#: Mapping from form ``BooleanField`` to value in database for Clinvar status.
FILTER_FORM_TRANSLATE_CLINVAR_STATUS = {
    "clinvar_status_practice_guideline": "practice guideline",
    "clinvar_status_expert_panel": "reviewed by expert panel",
    "clinvar_status_multiple_no_conflict": "criteria provided, multiple submitters, no conflicts",
    "clinvar_status_conflict": "criteria provided, conflicting interpretations",
    "clinvar_status_single": "criteria provided, single submitter",
    "clinvar_status_no_criteria": "no assertion criteria provided",
    "clinvar_status_no_assertion": "no assertion provided",
}


#: Mapping from form ``BooleanField`` to value in database for Clinvar significance.
FILTER_FORM_TRANSLATE_SIGNIFICANCE = {
    "clinvar_include_pathogenic": "pathogenic",
    "clinvar_include_likely_pathogenic": "likely pathogenic",
    "clinvar_include_uncertain_significance": "uncertain significance",
    "clinvar_include_likely_benign": "likely benign",
    "clinvar_include_benign": "benign",
}


class SmallVariantFlagsFilterFormMixin:
    """Fields for filtering to ``SmallVariantFlags``."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Simple, boolean-valued flags.
        self.fields["flag_bookmarked"] = forms.BooleanField(
            label="bookmarked", required=False, initial=True
        )
        self.fields["flag_candidate"] = forms.BooleanField(
            label="candidate", required=False, initial=True
        )
        self.fields["flag_final_causative"] = forms.BooleanField(
            label="final causative", required=False, initial=True
        )
        self.fields["flag_for_validation"] = forms.BooleanField(
            label="for validation", required=False, initial=True
        )
        self.fields["flag_simple_empty"] = forms.BooleanField(
            label="no simple flag", required=False, initial=True
        )

        # Flags with value positive/uncertain/negative

        # Visual inspection
        self.fields["flag_visual_positive"] = forms.BooleanField(
            label="positive", required=False, initial=True
        )
        self.fields["flag_visual_uncertain"] = forms.BooleanField(
            label="uncertain", required=False, initial=True
        )
        self.fields["flag_visual_negative"] = forms.BooleanField(
            label="negative", required=False, initial=True
        )
        self.fields["flag_visual_empty"] = forms.BooleanField(
            label="empty", required=False, initial=True
        )

        # Validation
        self.fields["flag_validation_positive"] = forms.BooleanField(
            label="positive", required=False, initial=True
        )
        self.fields["flag_validation_uncertain"] = forms.BooleanField(
            label="uncertain", required=False, initial=True
        )
        self.fields["flag_validation_negative"] = forms.BooleanField(
            label="negative", required=False, initial=True
        )
        self.fields["flag_validation_empty"] = forms.BooleanField(
            label="empty", required=False, initial=True
        )

        # Phenotype match / clinical
        self.fields["flag_phenotype_match_positive"] = forms.BooleanField(
            label="positive", required=False, initial=True
        )
        self.fields["flag_phenotype_match_uncertain"] = forms.BooleanField(
            label="uncertain", required=False, initial=True
        )
        self.fields["flag_phenotype_match_negative"] = forms.BooleanField(
            label="negative", required=False, initial=True
        )
        self.fields["flag_phenotype_match_empty"] = forms.BooleanField(
            label="empty", required=False, initial=True
        )

        # Summary flag, overrides other multi-valued flags
        self.fields["flag_summary_positive"] = forms.BooleanField(
            label="positive", required=False, initial=True
        )
        self.fields["flag_summary_uncertain"] = forms.BooleanField(
            label="uncertain", required=False, initial=True
        )
        self.fields["flag_summary_negative"] = forms.BooleanField(
            label="negative", required=False, initial=True
        )
        self.fields["flag_summary_empty"] = forms.BooleanField(
            label="empty", required=False, initial=True
        )


class SmallVariantGenotypeFilterFormMixin:
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
        """Add and update genotype fields."""
        self.fields["compound_recessive_enabled"] = forms.BooleanField(
            label="enable comp. het. mode",
            required=False,
            help_text=(
                "Compound recessive filtration only works for complete trios. "
                "Enabling the comp. het. filter disables the individual genotype filter settings above but quality "
                "settings still apply. "
                "Filters for variants that are present in one gene (identified by transcript database gene identifier) "
                "with the following constraints: "
                "(1) at least one variant is heterozygous in mother and index and homozygous reference in the father, "
                "and (2) at least one variant is heterozygous in father and index and homozygous in the mother."
            ),
        )

        # Disable compound recessive checkbox if no full trio present.
        if len(set(("index", "father", "mother")) & set(self.get_trio_roles().keys())) != 3:
            self.fields["compound_recessive_enabled"].disabled = True

        # Dynamically add the fields based on the pedigree
        for member in self.get_pedigree_with_samples():
            name = member["patient"]
            self.fields[self.get_genotype_field_names()[name]["gt"]] = forms.CharField(
                label="",
                required=True,
                widget=forms.Select(choices=INHERITANCE, attrs={"class": "genotype-field-gt"}),
            )


class SmallVariantQualityFilterFormMixin:
    """Form mixin for inheritance/genotype fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_quality_fields()

    @lru_cache()
    def get_quality_field_names(self):
        """Return mapping from patient and key to field name."""
        field_names = {}
        for member in self.get_pedigree_with_samples():
            for key in ("gt", "dp_het", "dp_hom", "ab", "gq", "ad", "fail", "export"):
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
            self.fields[self.get_quality_field_names()[name]["dp_het"]] = forms.IntegerField(
                label="",
                required=True,
                initial=10,
                min_value=0,
                widget=forms.TextInput(attrs={"class": "quality-field-dp-het numberInteger"}),
            )
            self.fields[self.get_quality_field_names()[name]["dp_hom"]] = forms.IntegerField(
                label="",
                required=True,
                initial=5,
                min_value=0,
                widget=forms.TextInput(attrs={"class": "quality-field-dp-hom numberInteger"}),
            )
            self.fields[self.get_quality_field_names()[name]["ab"]] = forms.FloatField(
                label="",
                required=True,
                initial=0.3,
                min_value=0,
                max_value=1,
                widget=forms.TextInput(attrs={"class": "quality-field-ab numberDecimal"}),
            )
            self.fields[self.get_quality_field_names()[name]["gq"]] = forms.IntegerField(
                label="",
                required=True,
                initial=30,
                min_value=0,
                widget=forms.TextInput(attrs={"class": "quality-field-gq numberInteger"}),
            )
            self.fields[self.get_quality_field_names()[name]["ad"]] = forms.IntegerField(
                label="",
                required=True,
                initial=3,
                min_value=0,
                widget=forms.TextInput(attrs={"class": "quality-field-ad numberInteger"}),
            )
            self.fields[self.get_quality_field_names()[name]["fail"]] = forms.CharField(
                label="",
                widget=forms.Select(choices=FAIL, attrs={"class": "quality-field-fail"}),
                required=True,
                initial="drop-variant",
            )
            self.fields[self.get_quality_field_names()[name]["export"]] = forms.BooleanField(
                label=only_source_name(name), required=False, initial=True
            )


class ClinvarForm(
    SmallVariantGenotypeFilterFormMixin, SmallVariantFlagsFilterFormMixin, forms.Form
):
    """Form used for creating Clinvar report."""

    #: Version of the form, used for versioning saved queries.
    form_version = 1
    #: Identifier of the form in database.
    form_id = "variants.clinvar_form"

    result_rows_limit = forms.IntegerField(
        label="Result row limit",
        required=True,
        initial=500,
        help_text=(
            "Currently hard-coded limit when querying Clinvar. Report a bug if you need more than 500 rows."
        ),
        widget=forms.HiddenInput(),
    )

    clinvar_include_benign = forms.BooleanField(label="benign", required=False, initial=False)
    clinvar_include_likely_benign = forms.BooleanField(
        label="likely benign", required=False, initial=False
    )
    clinvar_include_uncertain_significance = forms.BooleanField(
        label="uncertain significance", required=False, initial=True
    )
    clinvar_include_likely_pathogenic = forms.BooleanField(
        label="likely pathogenic", required=False, initial=True
    )
    clinvar_include_pathogenic = forms.BooleanField(
        label="pathogenic", required=False, initial=True
    )

    clinvar_origin_germline = forms.BooleanField(label="germline", required=False, initial=True)
    clinvar_origin_somatic = forms.BooleanField(label="somatic", required=False, initial=False)

    clinvar_status_practice_guideline = forms.BooleanField(
        label="practice guideline (4 stars)", required=False, initial=True
    )
    clinvar_status_expert_panel = forms.BooleanField(
        label="reviewed by expert panel (3 stars)", required=False, initial=True
    )
    clinvar_status_multiple_no_conflict = forms.BooleanField(
        label="criteria provided, multiple submitters, no conflicts (2 stars)",
        required=False,
        initial=True,
    )
    clinvar_status_conflict = forms.BooleanField(
        label="criteria provided, conflicting interpretations (1 stars)",
        required=False,
        initial=True,
    )
    clinvar_status_single = forms.BooleanField(
        label="criteria provided, single submitter (1 stars)", required=False, initial=True
    )
    clinvar_status_no_criteria = forms.BooleanField(
        label="no assertion criteria provided (0 stars)", required=False, initial=True
    )
    clinvar_status_no_assertion = forms.BooleanField(
        label="no assertion provided (0 stars)", required=False, initial=True
    )

    require_in_clinvar = forms.BooleanField(
        label="Clinvar membership required", required=False, initial=False
    )

    require_in_hgmd_public = forms.BooleanField(
        label="HGMD public membership required",
        required=False,
        initial=False,
        help_text=(
            "Require variant to be present in HGMD public (ENSEMBL track).  "
            "Please note that this data is several years old!"
        ),
    )

    DATABASE_SELECT_CHOICES = [("refseq", "RefSeq"), ("ensembl", "EnsEMBL")]
    database_select = forms.ChoiceField(
        choices=DATABASE_SELECT_CHOICES,
        widget=forms.RadioSelect(),
        initial=DATABASE_SELECT_CHOICES[0],
    )

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        super().__init__(*args, **kwargs)
        # Dynamically add the fields based on the pedigree
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

    def clean(self):
        result = super().clean()
        result["display_hgmd_public_membership"] = True
        return result


class ExportFileResubmitForm(forms.Form):
    file_type = forms.ChoiceField(
        initial="xlsx",
        choices=(("xlsx", "Excel (.xlsx)"), ("tsv", "TSV (.tsv)"), ("vcf", "VCF (.vcf.gz)")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class ExportProjectCasesFileResubmitForm(forms.Form):
    file_type = forms.ChoiceField(
        initial="xlsx",
        choices=(
            ("xlsx", "Excel (.xlsx)"),
            ("tsv", "TSV (.tsv)"),
            # ("vcf", "VCF (.vcf.gz)"),
        ),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class EmptyForm(forms.Form):
    pass


class SmallVariantExportFilterFormMixin:
    """Form mixin with fields for export-to-file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["file_type"] = forms.ChoiceField(
            initial="xlsx",
            choices=(("xlsx", "Excel (.xlsx)"), ("tsv", "TSV (.tsv)"), ("vcf", "VCF (.vcf.gz)")),
            widget=forms.Select(attrs={"class": "form-control"}),
        )

        self.fields["export_flags"] = forms.BooleanField(
            label="Export flags",
            initial=True,
            required=False,
            help_text="Export flags and label rows by summary.",
        )
        self.fields["export_comments"] = forms.BooleanField(
            label="Export comments",
            initial=True,
            required=False,
            help_text="Include comments in export.",
        )


class SmallVariantFrequencyFilterFormMixin:
    """Form mixin with frequency filtration fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["exac_enabled"] = forms.BooleanField(label="", required=False, initial=True)
        self.fields["exac_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in one ExAC population",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["exac_homozygous"] = forms.IntegerField(
            label="",
            initial=20,
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal hom. count in ExAC", "class": "numberInteger"}
            ),
        )
        self.fields["exac_heterozygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal het. count in ExAC", "class": "numberInteger"}
            ),
        )

        self.fields["gnomad_exomes_enabled"] = forms.BooleanField(
            label="", required=False, initial=False
        )
        self.fields["gnomad_exomes_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in one gnomAD exomes population",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["gnomad_exomes_homozygous"] = forms.IntegerField(
            label="",
            initial=30,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hom. count in gnomAD exomes",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["gnomad_exomes_heterozygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal het. count in gnomAD exomes",
                    "class": "numberInteger",
                }
            ),
        )

        self.fields["gnomad_genomes_enabled"] = forms.BooleanField(
            label="", required=False, initial=False
        )
        self.fields["gnomad_genomes_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in one gnomAD genomes population",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["gnomad_genomes_homozygous"] = forms.IntegerField(
            label="",
            initial=20,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hom. count in gnomAD genomes",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["gnomad_genomes_heterozygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal het. count in gnomAD genomes",
                    "class": "numberInteger",
                }
            ),
        )

        self.fields["thousand_genomes_enabled"] = forms.BooleanField(
            label="", required=False, initial=True
        )
        self.fields["thousand_genomes_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in one 1000 genomes population",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["thousand_genomes_homozygous"] = forms.IntegerField(
            label="",
            initial=10,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hom. count in 1000 genomes",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["thousand_genomes_heterozygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal het. count in 1000 genomes",
                    "class": "numberInteger",
                }
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class SmallVariantVariantEffectFilterFormMixin:
    """Form mixin with variant effect etc. fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["effect_coding_transcript_intron_variant"] = forms.BooleanField(
            label="coding intron variant", required=False
        )
        self.fields["effect_complex_substitution"] = forms.BooleanField(
            label="complex substitution", required=False, initial=True
        )
        self.fields["effect_direct_tandem_duplication"] = forms.BooleanField(
            label="direct tandem duplication", required=False, initial=True
        )
        self.fields["effect_disruptive_inframe_deletion"] = forms.BooleanField(
            label="disruptive inframe deletion", required=False, initial=True
        )
        self.fields["effect_disruptive_inframe_insertion"] = forms.BooleanField(
            label="disruptive inframe insertion", required=False, initial=True
        )
        self.fields["effect_downstream_gene_variant"] = forms.BooleanField(
            label="downstream gene variant", required=False
        )
        self.fields["effect_feature_truncation"] = forms.BooleanField(
            label="feature truncation", required=False, initial=True
        )
        self.fields["effect_five_prime_UTR_exon_variant"] = forms.BooleanField(
            label="5' UTR exon variant", required=False, initial=True
        )
        self.fields["effect_five_prime_UTR_intron_variant"] = forms.BooleanField(
            label="5' UTR intron variant", required=False
        )
        self.fields["effect_frameshift_elongation"] = forms.BooleanField(
            label="frameshift elongation", required=False, initial=True
        )
        self.fields["effect_frameshift_truncation"] = forms.BooleanField(
            label="frameshift truncation", required=False, initial=True
        )
        self.fields["effect_frameshift_variant"] = forms.BooleanField(
            label="frameshift variant", required=False, initial=True
        )
        self.fields["effect_inframe_deletion"] = forms.BooleanField(
            label="inframe deletion", required=False, initial=True
        )
        self.fields["effect_inframe_insertion"] = forms.BooleanField(
            label="inframe insertion", required=False, initial=True
        )
        self.fields["effect_intergenic_variant"] = forms.BooleanField(
            label="intergenic variant", required=False
        )
        self.fields["effect_internal_feature_elongation"] = forms.BooleanField(
            label="internal feature elongation", required=False, initial=True
        )
        self.fields["effect_missense_variant"] = forms.BooleanField(
            label="missense variant", required=False, initial=True
        )
        self.fields["effect_mnv"] = forms.BooleanField(label="mnv", required=False, initial=True)
        self.fields["effect_non_coding_transcript_exon_variant"] = forms.BooleanField(
            label="non-coding exon variant", required=False
        )
        self.fields["effect_non_coding_transcript_intron_variant"] = forms.BooleanField(
            label="non-coding intron variant", required=False
        )
        self.fields["effect_splice_acceptor_variant"] = forms.BooleanField(
            label="splice acceptor variant", required=False, initial=True
        )
        self.fields["effect_splice_donor_variant"] = forms.BooleanField(
            label="splice donor variant", required=False, initial=True
        )
        self.fields["effect_splice_region_variant"] = forms.BooleanField(
            label="splice region variant", required=False, initial=True
        )
        self.fields["effect_start_lost"] = forms.BooleanField(
            label="start lost", required=False, initial=True
        )
        self.fields["effect_stop_gained"] = forms.BooleanField(
            label="stop gained", required=False, initial=True
        )
        self.fields["effect_stop_lost"] = forms.BooleanField(
            label="stop lost", required=False, initial=True
        )
        self.fields["effect_stop_retained_variant"] = forms.BooleanField(
            label="stop retained variant", required=False, initial=True
        )
        self.fields["effect_structural_variant"] = forms.BooleanField(
            label="structural variant", required=False, initial=True
        )
        self.fields["effect_synonymous_variant"] = forms.BooleanField(
            label="synonymous variant", required=False
        )
        self.fields["effect_three_prime_UTR_exon_variant"] = forms.BooleanField(
            label="3' UTR exon variant", required=False, initial=True
        )
        self.fields["effect_three_prime_UTR_intron_variant"] = forms.BooleanField(
            label="3' UTR intron variant", required=False
        )
        self.fields["effect_transcript_ablation"] = forms.BooleanField(
            label="transcript ablation", required=False, initial=True
        )
        self.fields["effect_upstream_gene_variant"] = forms.BooleanField(
            label="upstream gene variant", required=False
        )

        self.fields["transcripts_coding"] = forms.BooleanField(
            label="coding transcripts", required=False, initial=True
        )
        self.fields["transcripts_noncoding"] = forms.BooleanField(
            label="non-coding transcripts", required=False, initial=True
        )

        self.fields["var_type_snv"] = forms.BooleanField(label="SNV", required=False, initial=True)
        self.fields["var_type_indel"] = forms.BooleanField(
            label="InDel", required=False, initial=True
        )
        self.fields["var_type_mnv"] = forms.BooleanField(label="MNV", required=False, initial=True)

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["effects"] = [
            effect for name, effect in FILTER_FORM_TRANSLATE_EFFECTS.items() if cleaned_data[name]
        ]
        return cleaned_data


class SmallVariantMiscFilterFormMixin:
    """Form mixin with misc. fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["result_rows_limit"] = forms.IntegerField(
            label="Result row limit",
            required=True,
            initial=80,
            help_text=(
                "Maximal number of rows displayed <b>when rendering on the website</b>.  "
                "This setting is <b>not</b> used when creating a file for export."
            ),
            widget=forms.TextInput(attrs={"class": "numberInteger"}),
        )


class SmallVariantClinvarHgmdFilterFormMixin:
    """Form mixin with Clinvar/HGMD Public Fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["require_in_clinvar"] = forms.BooleanField(
            label="Clinvar membership required", required=False, initial=False
        )

        self.fields["require_in_hgmd_public"] = forms.BooleanField(
            label="HGMD public membership required",
            required=False,
            initial=False,
            help_text=(
                "Require variant to be present in HGMD public (ENSEMBL track).  "
                "Please note that this data is several years old!"
            ),
        )

        self.fields["clinvar_include_benign"] = forms.BooleanField(
            label="benign", required=False, initial=False
        )

        self.fields["clinvar_include_likely_benign"] = forms.BooleanField(
            label="likely benign", required=False, initial=False
        )

        self.fields["clinvar_include_uncertain_significance"] = forms.BooleanField(
            label="uncertain significance", required=False, initial=False
        )

        self.fields["clinvar_include_likely_pathogenic"] = forms.BooleanField(
            label="likely pathogenic", required=False, initial=False
        )

        self.fields["clinvar_include_pathogenic"] = forms.BooleanField(
            label="pathogenic", required=False, initial=False
        )

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["display_hgmd_public_membership"] = True
        return cleaned_data


class SmallVariantGeneListFilterFormMixin:
    """Form mixin with gene blacklist/whitelist fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["gene_blacklist"] = forms.CharField(
            label="Gene Blacklist",
            help_text="Enter a list of HGNC symbols, Entrez IDs, or ENSEMBL gene IDs separated by spaces or line break",
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter genes to black-list here",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            required=False,
            max_length=5000,
        )

        self.fields["gene_whitelist"] = forms.CharField(
            label="Gene Whitelist",
            help_text="Enter a list of HGNC symbols, Entrez IDs, or ENSEMBL gene IDs separated by spaces or line break",
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter genes to white-list here",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            required=False,
            max_length=5000,
        )

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["gene_blacklist"] = [
            s.strip() for s in cleaned_data["gene_blacklist"].strip().split() if s.strip()
        ]
        cleaned_data["gene_whitelist"] = [
            s.strip() for s in cleaned_data["gene_whitelist"].strip().split() if s.strip()
        ]
        return cleaned_data


class SmallVariantTranscriptSourceFilterFormMixin:
    """Form mixin for selecting transcript source."""

    DATABASE_SELECT_CHOICES = [("refseq", "RefSeq"), ("ensembl", "EnsEMBL")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["database_select"] = forms.ChoiceField(
            choices=self.DATABASE_SELECT_CHOICES,
            widget=forms.RadioSelect(),
            initial=self.DATABASE_SELECT_CHOICES[0],
        )


class FilterForm(
    SmallVariantFlagsFilterFormMixin,
    SmallVariantExportFilterFormMixin,
    SmallVariantFrequencyFilterFormMixin,
    SmallVariantVariantEffectFilterFormMixin,
    SmallVariantMiscFilterFormMixin,
    SmallVariantClinvarHgmdFilterFormMixin,
    SmallVariantGeneListFilterFormMixin,
    SmallVariantTranscriptSourceFilterFormMixin,
    SmallVariantQualityFilterFormMixin,
    SmallVariantGenotypeFilterFormMixin,
    forms.Form,
):
    """This form is used for filtering a single case."""

    #: Version of the form, used for versioning saved queries.
    form_version = 1
    #: Identifier of the form in database.
    form_id = "variants.small_variant_filter_form"

    submit = forms.ChoiceField(
        choices=(
            ("display", "Display results in table"),
            ("download", "Generate downloadable file in background"),
            ("submit-mutationdistiller", "Submit to MutationDistiller"),
        )
    )

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        super().__init__(*args, **kwargs)

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

    def clean(self):
        """Perform data cleaning and cross-field validation.

        Currently, ensures only that only one sample is selected for export in case of MutationDistiller submission.
        """
        cleaned_data = super().clean()
        # If submit is "submit-mutationdistiller" then only one sample can be checked for export.
        if cleaned_data["submit"] == "submit-mutationdistiller":
            seen_first = False
            for member in self.get_pedigree_with_samples():
                if cleaned_data[self.get_quality_field_names()[member["patient"]]["export"]]:
                    if seen_first:
                        raise forms.ValidationError(
                            "MutationDistiller only supports export of a single individual. "
                            'Please only select on sample the in "Configure Downloads" tab.'
                        )
                    seen_first = True
        return cleaned_data


class ProjectCasesFilterForm(
    SmallVariantFlagsFilterFormMixin,
    SmallVariantExportFilterFormMixin,
    SmallVariantFrequencyFilterFormMixin,
    SmallVariantVariantEffectFilterFormMixin,
    SmallVariantMiscFilterFormMixin,
    SmallVariantClinvarHgmdFilterFormMixin,
    SmallVariantGeneListFilterFormMixin,
    SmallVariantTranscriptSourceFilterFormMixin,
    SmallVariantQualityFilterFormMixin,
    SmallVariantGenotypeFilterFormMixin,
    forms.Form,
):
    """Form for filtering multiple cases at once."""

    #: Version of the form, used for versioning saved queries.
    form_version = 1
    #: Identifier of the form in database.
    form_id = "variants.project_cases_small_variant_filter_form"

    submit = forms.ChoiceField(
        choices=(
            ("display", "Display results in table"),
            ("download", "Generate downloadable file in background"),
        )
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super().__init__(*args, **kwargs)

    def get_pedigree(self):
        """Return ``list`` of ``dict`` with pedigree information."""
        return self.project.pedigree()

    def get_pedigree_with_samples(self):
        """Return ``list`` of ``dict`` with pedigree information of samples that have variants."""
        return self.project.get_filtered_pedigree_with_samples()

    def get_trio_roles(self):
        """Return empty dict as there is no trio role assignment when querying across project."""
        return {}

    def clean(self):
        """Perform data cleaning and cross-field validation.

        Currently, ensures only that only one sample is selected for export in case of MutationDistiller submission.
        """
        cleaned_data = super().clean()
        # Check that only the download file type is not VCF for project-wide queries.
        if cleaned_data["submit"] == "download":
            if cleaned_data["file_type"] == "vcf":
                raise forms.ValidationError(
                    "VCF export for project-wide queries not implemented yet!"
                )
        return cleaned_data


class SmallVariantFlagsForm(forms.ModelForm):
    """Form for validating small variant flags."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = SmallVariantFlags
        exclude = ("case", "sodar_uuid")


class SmallVariantCommentForm(forms.ModelForm):
    """Form for validating small variant comments."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = SmallVariantComment
        exclude = ("case", "sodar_uuid", "user")


class ProjectStatsJobForm(forms.Form):
    """Form class used for confirmation of recomputing project-wide statistics."""

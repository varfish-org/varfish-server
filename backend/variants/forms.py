from django import forms

FAIL = [("ignore", "ignore"), ("drop-variant", "drop variant"), ("no-call", "no-call")]


FILTER_FORM_TRANSLATE_EFFECTS = {
    "effect_coding_transcript_intron_variant": "coding_transcript_intron_variant",
    "effect_complex_substitution": "complex_substitution",
    "effect_direct_tandem_duplication": "direct_tandem_duplication",
    "effect_disruptive_inframe_deletion": "disruptive_inframe_deletion",
    "effect_disruptive_inframe_insertion": "disruptive_inframe_insertion",
    "effect_downstream_gene_variant": "downstream_gene_variant",
    "effect_exon_loss_variant": "exon_loss_variant",
    "effect_feature_elongation": "feature_elongation",
    "effect_feature_truncation": "feature_truncation",
    "effect_5_prime_UTR_exon_variant": "5_prime_UTR_exon_variant",
    "effect_5_prime_UTR_intron_variant": "5_prime_UTR_intron_variant",
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
    "effect_3_prime_UTR_exon_variant": "3_prime_UTR_exon_variant",
    "effect_3_prime_UTR_intron_variant": "3_prime_UTR_intron_variant",
    "effect_transcript_ablation": "transcript_ablation",
    "effect_upstream_gene_variant": "upstream_gene_variant",
    "effect_coding_sequence_variant": "coding_sequence_variant",
    "effect_conservative_inframe_deletion": "conservative_inframe_deletion",
    "effect_conservative_inframe_insertion": "conservative_inframe_insertion",
    "effect_intron_variant": "intron_variant",
    "effect_splice_donor_5th_base_variant": "splice_donor_5th_base_variant",
    "effect_splice_donor_region_variant": "splice_donor_region_variant",
    "effect_splice_polypyrimidine_tract_variant": "splice_polypyrimidine_tract_variant",
    "effect_start_retained_variant": "start_retained_variant",
    "effect_transcript_amplification": "transcript_amplification",
    "effect_protein_altering_variant": "protein_altering_variant",
    "effect_rare_amino_acid_variant": "rare_amino_acid_variant",
}


#: The following effects are might be used by mehari but are not really considered in the filter form.
EFFECTS_NOT_IN_FILTER_FORM = {
    "gene_variant",
    "mature_miRNA_variant",
    "regulatory_region_ablation",
    "regulatory_region_amplification",
    "regulatory_region_variant",
    "TF_binding_site_variant",
    "TFBS_ablation",
    "TFBS_amplification",
}


FILTER_FORM_TRANSLATE_INHERITANCE = {
    "any": None,
    "ref": ("0/0", "0|0", "0"),
    "het": ("0/1", "0|1", "1/0", "1|0", "1"),
    "hom": ("1/1", "1|1", "1"),
    "non-hom": ("0/0", "0|0", "0", "0/1", "0|1", "1/0", "1|0", "1"),
    "reference": ("0/0", "0|0", "0"),
    "variant": ("1/0", "1|0", "0/1", "0|1", "1/1", "1|1", "1"),
    "non-variant": ("0/0", "./.", "0"),
    "non-reference": ("1/0", "1|0", "0/1", "0|1", "1/1", "1|1", "./.", ".|.", "1"),
}

#: CADD score value.
PATHO_CADD = "cadd"
#: CADD score label.
PATHO_CADD_LABEL = "CADD"
#: MutationTaster score value.
PATHO_MUTATIONTASTER = "mutationtaster"
#: MutationTaster score label.
PATHO_MUTATIONTASTER_LABEL = "MutationTaster"
#: UMD score value.
PATHO_UMD = "umd"
#: UMD score label.
PATHO_UMD_LABEL = "UMD-Predictor"

#: The actual choices are defined in the form directly as they are dependent on the current user.
PATHO_SCORES_MAPPING = {
    PATHO_CADD: PATHO_CADD_LABEL,
    PATHO_MUTATIONTASTER: PATHO_MUTATIONTASTER_LABEL,
    PATHO_UMD: PATHO_UMD_LABEL,
}


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
            ("vcf", "VCF (.vcf.gz)"),
        ),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class EmptyForm(forms.Form):
    pass

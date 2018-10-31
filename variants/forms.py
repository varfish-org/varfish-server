from django import forms


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


class FilterForm(forms.Form):
    exac_enabled = forms.BooleanField(label="", required=False, initial=True)
    exac_frequency = forms.DecimalField(
        label="",
        initial=0.01,
        max_value=1,
        min_value=0,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Maximal frequency in one ExAC population"}),
    )
    exac_homozygous = forms.IntegerField(
        label="",
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal hom. count in ExAC"}),
    )
    exac_heterozygous = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal het. count in ExAC"}),
    )

    gnomad_exomes_enabled = forms.BooleanField(label="", required=False, initial=False)
    gnomad_exomes_frequency = forms.DecimalField(
        label="",
        initial=0.01,
        max_value=1,
        min_value=0,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Maximal frequency in one gnomAD exomes population"}
        ),
    )
    gnomad_exomes_homozygous = forms.IntegerField(
        label="",
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal hom. count in gnomAD exomes"}),
    )
    gnomad_exomes_heterozygous = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal het. count in gnomAD exomes"}),
    )

    gnomad_genomes_enabled = forms.BooleanField(label="", required=False, initial=False)
    gnomad_genomes_frequency = forms.DecimalField(
        label="",
        initial=0.01,
        max_value=1,
        min_value=0,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Maximal frequency in one gnomAD genomes population"}
        ),
    )
    gnomad_genomes_homozygous = forms.IntegerField(
        label="",
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal hom. count in gnomAD genomes"}),
    )
    gnomad_genomes_heterozygous = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal het. count in gnomAD genomes"}),
    )

    thousand_genomes_enabled = forms.BooleanField(label="", required=False, initial=True)
    thousand_genomes_frequency = forms.DecimalField(
        label="",
        initial=0.01,
        max_value=1,
        min_value=0,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Maximal frequency in one 1000 genomes population"}
        ),
    )
    thousand_genomes_homozygous = forms.IntegerField(
        label="",
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal hom. count in 1000 genomes"}),
    )
    thousand_genomes_heterozygous = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Maximal het. count in 1000 genomes"}),
    )

    effect_coding_transcript_intron_variant = forms.BooleanField(
        label="coding intron variant", required=False
    )
    effect_complex_substitution = forms.BooleanField(
        label="complex substitution", required=False, initial=True
    )
    effect_direct_tandem_duplication = forms.BooleanField(
        label="direct tandem duplication", required=False, initial=True
    )
    effect_disruptive_inframe_deletion = forms.BooleanField(
        label="disruptive inframe deletion", required=False, initial=True
    )
    effect_disruptive_inframe_insertion = forms.BooleanField(
        label="disruptive inframe insertion", required=False, initial=True
    )
    effect_downstream_gene_variant = forms.BooleanField(
        label="downstream gene variant", required=False
    )
    effect_feature_truncation = forms.BooleanField(
        label="feature truncation", required=False, initial=True
    )
    effect_five_prime_UTR_exon_variant = forms.BooleanField(
        label="5' UTR exon variant", required=False
    )
    effect_five_prime_UTR_intron_variant = forms.BooleanField(
        label="5' UTR intron variant", required=False
    )
    effect_frameshift_elongation = forms.BooleanField(
        label="frameshift elongation", required=False, initial=True
    )
    effect_frameshift_truncation = forms.BooleanField(
        label="frameshift truncation", required=False, initial=True
    )
    effect_frameshift_variant = forms.BooleanField(
        label="frameshift variant", required=False, initial=True
    )
    effect_inframe_deletion = forms.BooleanField(
        label="inframe deletion", required=False, initial=True
    )
    effect_inframe_insertion = forms.BooleanField(
        label="inframe insertion", required=False, initial=True
    )
    effect_intergenic_variant = forms.BooleanField(label="intergenic variant", required=False)
    effect_internal_feature_elongation = forms.BooleanField(
        label="internal feature elongation", required=False, initial=True
    )
    effect_missense_variant = forms.BooleanField(
        label="missense variant", required=False, initial=True
    )
    effect_mnv = forms.BooleanField(label="mnv", required=False, initial=True)
    effect_non_coding_transcript_exon_variant = forms.BooleanField(
        label="non-coding exon variant", required=False
    )
    effect_non_coding_transcript_intron_variant = forms.BooleanField(
        label="non-coding intron variant", required=False
    )
    effect_splice_acceptor_variant = forms.BooleanField(
        label="splice acceptor variant", required=False, initial=True
    )
    effect_splice_donor_variant = forms.BooleanField(
        label="splice donor variant", required=False, initial=True
    )
    effect_splice_region_variant = forms.BooleanField(
        label="splice region variant", required=False, initial=True
    )
    effect_start_lost = forms.BooleanField(label="start lost", required=False, initial=True)
    effect_stop_gained = forms.BooleanField(label="stop gained", required=False, initial=True)
    effect_stop_lost = forms.BooleanField(label="stop lost", required=False, initial=True)
    effect_stop_retained_variant = forms.BooleanField(
        label="stop retained variant", required=False, initial=True
    )
    effect_structural_variant = forms.BooleanField(
        label="structural variant", required=False, initial=True
    )
    effect_synonymous_variant = forms.BooleanField(label="synonymous variant", required=False)
    effect_three_prime_UTR_exon_variant = forms.BooleanField(
        label="3' UTR exon variant", required=False
    )
    effect_three_prime_UTR_intron_variant = forms.BooleanField(
        label="3' UTR intron variant", required=False
    )
    effect_transcript_ablation = forms.BooleanField(
        label="transcript ablation", required=False, initial=True
    )
    effect_upstream_gene_variant = forms.BooleanField(label="upstream gene variant", required=False)

    compound_recessive_enabled = forms.BooleanField(
        label="enable compound het. mode", required=False
    )

    gene_blacklist = forms.CharField(
        label="Gene Blacklist",
        help_text="Enter a list of genes to blacklist in the results, separated by spaces or line breaks.",
        widget=forms.Textarea(attrs={"placeholder": "Your Gene Symbols Here"}),
        required=False,
        max_length=1000,
    )

    var_type_mnv = forms.BooleanField(label="MNV", required=False, initial=True)
    var_type_snv = forms.BooleanField(label="SNV", required=False, initial=True)
    var_type_indel = forms.BooleanField(label="InDel", required=False, initial=True)

    DATABASE_SELECT_CHOICES = [("refseq", "RefSeq"), ("ensembl", "EnsEMBL")]
    database_select = forms.ChoiceField(
        choices=DATABASE_SELECT_CHOICES,
        widget=forms.RadioSelect(),
        initial=DATABASE_SELECT_CHOICES[0],
    )

    def __init__(self, *args, **kwargs):
        self.pedigree = kwargs.pop("pedigree")
        super().__init__(*args, **kwargs)

        for member in self.pedigree:
            self.fields[member["fields"]["gt"]] = forms.CharField(
                label="", required=True, widget=forms.Select(choices=INHERITANCE)
            )
            self.fields[member["fields"]["dp"]] = forms.IntegerField(
                label="", required=True, initial=10, min_value=0
            )  # relaxed: 8
            self.fields[member["fields"]["ab"]] = forms.FloatField(
                label="", required=True, initial=0.3, min_value=0, max_value=1
            )  # relaxed: 0.2
            self.fields[member["fields"]["gq"]] = forms.IntegerField(
                label="", required=True, initial=30, min_value=0
            )  # relaxed: 20
            self.fields[member["fields"]["ad"]] = forms.IntegerField(
                label="", required=True, initial=10, min_value=0
            )  # ???
            self.fields[member["fields"]["fail"]] = forms.CharField(
                label="", widget=forms.Select(choices=FAIL), required=True, initial="drop-variant"
            )
            if member["role"] == "index" and (member["father"] == "0" or member["mother"] == "0"):
                self.fields["compound_recessive_enabled"].disabled = True

    translate_effects = {
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

    translate_inheritance = {
        "any": None,
        "ref": ("0/0",),
        "het": ("0/1", "1/0"),
        "hom": ("1/1",),
        "variant": ("1/0", "0/1", "1/1"),
        "non-variant": ("0/0", "./."),
        "non-reference": ("1/0", "0/1", "1/1", "./."),
    }

from django import forms
from .models import Pedigree


INHERITANCE = [
    ("any", "any"),
    ("ref", "0/0"),
    ("het", "0/1"),
    ("hom", "1/1"),
    ("variant", "variant"),
    ("non-variant", "non-variant"),
    ("non-reference", "non-reference"),
]

FAIL = [
    ("ignore", "ignore"),
    ("drop-variant", "drop variant"),
    ("no-call", "no-call"),
]


class FilterForm(forms.Form):
    frequency_filter = forms.FloatField(
        initial=0.01, max_value=0.01, min_value=0
    )
    remove_homozygous = forms.BooleanField(
        label="Remove variants that have at least one homozygous entry in ExAC",
        required=False,
    )

    effect_coding_transcript_intron_variant = forms.BooleanField(
        label="coding transcript intron variant", required=False
    )
    effect_complex_substitution = forms.BooleanField(
        label="complex substitution", required=True, initial=True, disabled=True
    )
    effect_direct_tandem_duplication = forms.BooleanField(
        label="direct tandem duplication",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_disruptive_inframe_deletion = forms.BooleanField(
        label="disruptive inframe deletion",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_disruptive_inframe_insertion = forms.BooleanField(
        label="disruptive inframe insertion",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_downstream_gene_variant = forms.BooleanField(
        label="downstream gene variant", required=False
    )
    effect_feature_truncation = forms.BooleanField(
        label="feature truncation", required=True, initial=True, disabled=True
    )
    effect_five_prime_UTR_exon_variant = forms.BooleanField(
        label="5' UTR exon variant", required=False
    )
    effect_five_prime_UTR_intron_variant = forms.BooleanField(
        label="5' UTR intron variant", required=False
    )
    effect_frameshift_elongation = forms.BooleanField(
        label="frameshift elongation",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_frameshift_truncation = forms.BooleanField(
        label="frameshift truncation",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_frameshift_variant = forms.BooleanField(
        label="frameshift variant", required=True, initial=True, disabled=True
    )
    effect_inframe_deletion = forms.BooleanField(
        label="inframe deletion", required=True, initial=True, disabled=True
    )
    effect_inframe_insertion = forms.BooleanField(
        label="inframe insertion", required=True, initial=True, disabled=True
    )
    effect_intergenic_variant = forms.BooleanField(
        label="intergenic variant", required=False
    )
    effect_internal_feature_elongation = forms.BooleanField(
        label="internal feature elongation", required=False
    )
    effect_missense_variant = forms.BooleanField(
        label="missense variant", required=True, initial=True, disabled=True
    )
    effect_mnv = forms.BooleanField(
        label="mnv", required=True, initial=True, disabled=True
    )
    effect_non_coding_transcript_exon_variant = forms.BooleanField(
        label="non-coding transcript exon variant", required=False
    )
    effect_non_coding_transcript_intron_variant = forms.BooleanField(
        label="non-coding transcript intron variant", required=False
    )
    effect_splice_acceptor_variant = forms.BooleanField(
        label="splice acceptor variant",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_splice_donor_variant = forms.BooleanField(
        label="splice donor variant", required=True, initial=True, disabled=True
    )
    effect_splice_region_variant = forms.BooleanField(
        label="splice region variant",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_start_lost = forms.BooleanField(
        label="start lost", required=True, initial=True, disabled=True
    )
    effect_stop_gained = forms.BooleanField(
        label="stop gained", required=True, initial=True, disabled=True
    )
    effect_stop_lost = forms.BooleanField(
        label="stop lost", required=True, initial=True, disabled=True
    )
    effect_stop_retained_variant = forms.BooleanField(
        label="stop retained variant",
        required=True,
        initial=True,
        disabled=True,
    )
    effect_structural_variant = forms.BooleanField(
        label="structural variant", required=True, initial=True, disabled=True
    )
    effect_synonymous_variant = forms.BooleanField(
        label="synonymous variant", required=False
    )
    effect_three_prime_UTR_exon_variant = forms.BooleanField(
        label="3' UTR exon variant", required=False
    )
    effect_three_prime_UTR_intron_variant = forms.BooleanField(
        label="3' UTR intron variant", required=False
    )
    effect_transcript_ablation = forms.BooleanField(
        label="transcript ablation", required=True, initial=True, disabled=True
    )
    effect_upstream_gene_variant = forms.BooleanField(
        label="upstream gene variant", required=False
    )

    def __init__(self, *args, **kwargs):
        self.pedigree = kwargs.pop("pedigree")
        super().__init__(*args, **kwargs)

        for member in self.pedigree:
            self.fields[member["fields"]["gt"]] = forms.CharField(
                label="", widget=forms.Select(choices=INHERITANCE)
            )
            self.fields[member["fields"]["dp"]] = forms.IntegerField(
                label="", required=False, initial=20, min_value=0
            )
            self.fields[member["fields"]["ab"]] = forms.FloatField(
                label="", required=False, initial=0.2, min_value=0, max_value=1
            )
            self.fields[member["fields"]["gq"]] = forms.IntegerField(
                label="", required=False, initial=40, min_value=0
            )
            self.fields[member["fields"]["ad"]] = forms.IntegerField(
                label="", required=False, initial=10, min_value=0
            )
            self.fields[member["fields"]["fail"]] = forms.CharField(
                label="",
                widget=forms.Select(choices=FAIL),
                required=False,
                initial="ignore",
            )

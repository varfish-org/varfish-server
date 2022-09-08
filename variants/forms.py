from functools import lru_cache
import io
from itertools import chain
import os
import re
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.utils.text import get_valid_filename
from projectroles.app_settings import AppSettingAPI
import vcfpy

from geneinfo.models import Hgnc, Hpo, HpoName

from .models import AcmgCriteriaRating, Case, CaseComments, SmallVariantComment, SmallVariantFlags
from .templatetags.variants_tags import get_term_description, only_source_name

app_settings = AppSettingAPI()


def save_file(file, file_name, tmpdir):
    """Save file to temp directory and return path to file."""
    fs = FileSystemStorage()
    filepath = os.path.join(tmpdir, file_name)
    if not hasattr(file, "read"):
        file = io.StringIO("\n".join(file))
    fs.save(filepath, file)
    return filepath


class CaseForm(forms.ModelForm):
    """Form for updating a ``Case``, including its pedigree.

    We need to build the fields dynamically as they depend on the value of the JSON ``pedigree`` field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        member_choices = tuple(
            ((i, line["patient"]) for i, line in enumerate(self.instance.pedigree))
        )
        parent_choices = tuple(chain(((-1, "0"),), member_choices))
        name_index = {
            "0": -1,
            **{line["patient"]: i for i, line in enumerate(self.instance.pedigree)},
        }

        # The choices for the index depends, of course, on the pedigree.
        self.fields["index"] = forms.ChoiceField(
            initial=self.instance.index, choices=member_choices
        )

        # Field names for template loop.
        self.col_names = ("patient", "father", "mother", "sex", "affected")
        self.ped_field_names = [
            {key: "member_%d_%s" % (i, key) for key in self.col_names}
            for i, _ in enumerate(self.instance.pedigree)
        ]

        # Build the fields for updating the pedigree.
        for i, line in enumerate(self.instance.pedigree):
            self.fields[self.ped_field_names[i]["patient"]] = forms.CharField(
                initial=line["patient"], min_length=1
            )
            self.fields[self.ped_field_names[i]["father"]] = forms.ChoiceField(
                initial=name_index.get(line["father"], -1), choices=parent_choices
            )
            self.fields[self.ped_field_names[i]["mother"]] = forms.ChoiceField(
                initial=name_index.get(line["mother"], -1), choices=parent_choices
            )
            self.fields[self.ped_field_names[i]["sex"]] = forms.ChoiceField(
                initial=self.instance.pedigree[i]["sex"],
                choices=((0, "unknown"), (1, "male"), (2, "female")),
            )
            self.fields[self.ped_field_names[i]["affected"]] = forms.ChoiceField(
                initial=self.instance.pedigree[i]["affected"],
                choices=((0, "unknown"), (1, "unaffected"), (2, "affected")),
            )

        self.genomebuild = self.instance.release

    def save(self, commit=True):
        case = super().save(commit=False)

        # Create a two-level deep copy of the pedigree information.
        self.instance.pedigree = [dict(line) for line in self.instance.pedigree]
        # Update non-parent fields first.
        for i, line in enumerate(self.instance.pedigree):
            self.instance.pedigree[i]["patient"] = self.cleaned_data[
                self.ped_field_names[i]["patient"]
            ]
            for key in ("sex", "affected"):
                self.instance.pedigree[i][key] = int(
                    self.cleaned_data[self.ped_field_names[i][key]]
                )
        # Now update parent fields.
        for i, line in enumerate(self.instance.pedigree):
            for key in ("father", "mother"):
                idx = int(self.cleaned_data[self.ped_field_names[i][key]])
                if idx == -1:
                    self.instance.pedigree[i][key] = "0"
                else:
                    parent_name = self.instance.pedigree[idx]["patient"]
                    self.instance.pedigree[i][key] = parent_name

        case.index = self.instance.pedigree[int(self.cleaned_data["index"])]["patient"]

        if commit:
            case.save()
        return case

    class Meta:
        model = Case
        # Only the name field can be used as-is.
        fields = ("name",)


#: Inheritance value - display pairs for select options.
INHERITANCE = [
    ("any", "any"),
    ("ref", "0/0"),
    ("het", "0/1"),
    ("hom", "1/1"),
    ("non-hom", "0/0 or 0/1"),
    ("variant", "variant"),
    ("non-variant", "non-variant"),
    ("non-reference", "non-reference"),
    ("index", "c/h index"),
    ("recessive-index", "recess. index"),
]

FAIL = [("ignore", "ignore"), ("drop-variant", "drop variant"), ("no-call", "no-call")]


FILTER_FORM_TRANSLATE_EFFECTS = {
    "effect_coding_transcript_intron_variant": "coding_transcript_intron_variant",
    "effect_complex_substitution": "complex_substitution",
    "effect_direct_tandem_duplication": "direct_tandem_duplication",
    "effect_disruptive_inframe_deletion": "disruptive_inframe_deletion",
    "effect_disruptive_inframe_insertion": "disruptive_inframe_insertion",
    "effect_downstream_gene_variant": "downstream_gene_variant",
    "effect_exon_loss_variant": "exon_loss_variant",
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
    "ref": ("0/0", "0|0", "0"),
    "het": ("0/1", "0|1", "1/0", "1|0", "1"),
    "hom": ("1/1", "1|1", "1"),
    "non-hom": ("0/0", "0|0", "0", "0/1", "0|1", "1/0", "1|0", "1"),
    "reference": ("0/0", "0|0", "0"),
    "variant": ("1/0", "1|0", "0/1", "0|1", "1/1", "1|1", "1"),
    "non-variant": ("0/0", "./.", "0"),
    "non-reference": ("1/0", "1|0", "0/1", "0|1", "1/1", "1|1", "./.", ".|.", "1"),
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


#: Phenix prioritization value.
PRIO_PHENIX = "phenix"
#: Phenix prioritization label.
PRIO_PHENIX_LABEL = "Phenix"
#: Phive prioritization value.
PRIO_PHIVE = "phive"
#: Phive prioritization label.
PRIO_PHIVE_LABEL = "Phive"
#: HiPhive prioritization value.
PRIO_HIPHIVE = "hiphive"
#: HiPhive prioritization value (all sources of evidence).
PRIO_HIPHIVE = "hiphive"
#: HiPhive prioritization value (human only).
PRIO_HIPHIVE_HUMAN = "hiphive-human"
#: HiPhive prioritization value (human and mouse).
PRIO_HIPHIVE_MOUSE = "hiphive-mouse"
#: HiPhive prioritization label (all sources of evidence).
PRIO_HIPHIVE_LABEL = "HiPhive (human, mouse, fish, PPI)"
#: HiPhive prioritization label (human only).
PRIO_HIPHIVE_HUMAN_LABEL = "HiPhive (human only)"
#: HiPhive prioritization label (human and mouse).
PRIO_HIPHIVE_MOUSE_LABEL = "HiPhive (human+mouse)"

#: Choices for prioritization algorithms.
PRIO_ALGORITHM_CHOICES = (
    (PRIO_PHENIX, PRIO_PHENIX_LABEL),
    (PRIO_PHIVE, PRIO_PHIVE_LABEL),
    (PRIO_HIPHIVE_HUMAN, PRIO_HIPHIVE_HUMAN_LABEL),
    (PRIO_HIPHIVE_MOUSE, PRIO_HIPHIVE_MOUSE_LABEL),
    (PRIO_HIPHIVE, PRIO_HIPHIVE_LABEL),
)


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
        self.fields["flag_no_disease_association"] = forms.BooleanField(
            label="no known disease association", required=False, initial=True
        )
        self.fields["flag_segregates"] = forms.BooleanField(
            label="segregates", required=False, initial=True
        )
        self.fields["flag_doesnt_segregate"] = forms.BooleanField(
            label="doesn't segregate", required=False, initial=True
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

        # Molecular
        self.fields["flag_molecular_positive"] = forms.BooleanField(
            label="positive", required=False, initial=True
        )
        self.fields["flag_molecular_uncertain"] = forms.BooleanField(
            label="uncertain", required=False, initial=True
        )
        self.fields["flag_molecular_negative"] = forms.BooleanField(
            label="negative", required=False, initial=True
        )
        self.fields["flag_molecular_empty"] = forms.BooleanField(
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
        # Dynamically add the fields based on the pedigree
        default_families = self.get_default_families()
        default_indices = [x["index"] for x in default_families]
        default_mothers = [x["mother"] for x in default_families]
        default_fathers = [x["father"] for x in default_families]
        for family, members in self.get_family_with_pedigree_with_samples().items():
            for member in members:
                name = member["patient"]
                affection = "affected" if 2 == member["affected"] else "unaffected"
                self.fields[self.get_genotype_field_names()[name]["gt"]] = forms.CharField(
                    label="",
                    required=True,
                    widget=forms.Select(
                        choices=INHERITANCE,
                        attrs={
                            "class": "genotype-field-gt %s" % affection,
                            "data-default-index": "1" if name in default_indices else "0",
                            "data-default-mother": "1" if name in default_mothers else "0",
                            "data-default-father": "1" if name in default_fathers else "0",
                            "data-mother": member["mother"],
                            "data-father": member["father"],
                            "data-family": family,
                        },
                    ),
                )

    def clean(self):
        result = super().clean()
        result["compound_recessive_indices"] = {}
        result["recessive_indices"] = {}
        for family, members in self.get_family_with_pedigree_with_samples().items():
            for member in members:
                name = member["patient"]
                if result[self.get_genotype_field_names()[name]["gt"]] == "index":
                    result["compound_recessive_indices"][family] = name
                elif result[self.get_genotype_field_names()[name]["gt"]] == "recessive-index":
                    result["recessive_indices"][family] = name
                elif result[self.get_genotype_field_names()[name]["gt"]] == "hom-recessive-index":
                    self.add_error(
                        self.get_genotype_field_names()[name]["gt"],
                        "This option value shouldn't be passed. Selecting it should trigger JS code which changes the value.",
                    )
        return result


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
            for key in ("dp_het", "dp_hom", "ab", "gq", "ad", "ad_max", "fail", "export"):
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
            affection = "affected" if 2 == member["affected"] else "unaffected"
            self.fields[self.get_quality_field_names()[name]["dp_het"]] = forms.IntegerField(
                label="",
                required=True,
                initial=10,
                min_value=0,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-dp-het numberInteger %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["dp_hom"]] = forms.IntegerField(
                label="",
                required=True,
                initial=5,
                min_value=0,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-dp-hom numberInteger %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["ab"]] = forms.FloatField(
                label="",
                required=True,
                initial=0.3,
                min_value=0,
                max_value=1,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-ab numberDecimal %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["gq"]] = forms.IntegerField(
                label="",
                required=True,
                initial=30,
                min_value=0,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-gq numberInteger %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["ad"]] = forms.IntegerField(
                label="",
                required=True,
                initial=3,
                min_value=0,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-ad numberInteger %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["ad_max"]] = forms.IntegerField(
                label="",
                required=False,
                min_value=0,
                widget=forms.TextInput(
                    attrs={"class": "quality-field-ad-max numberInteger %s" % affection}
                ),
            )
            self.fields[self.get_quality_field_names()[name]["fail"]] = forms.CharField(
                label="",
                widget=forms.Select(
                    choices=FAIL, attrs={"class": "quality-field-fail %s" % affection}
                ),
                required=True,
                initial="drop-variant",
            )
            self.fields[self.get_quality_field_names()[name]["export"]] = forms.BooleanField(
                label=only_source_name(name), required=False, initial=True
            )


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
        self.fields["exac_hemizygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal hemi. count in ExAC", "class": "numberInteger"}
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
        self.fields["gnomad_exomes_hemizygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hemi. count in gnomAD exomes",
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
        self.fields["gnomad_genomes_hemizygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hemi. count in gnomAD genomes",
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
        self.fields["thousand_genomes_hemizygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hemi. count in 1000 genomes",
                    "class": "numberInteger",
                }
            ),
        )

        self.fields["inhouse_enabled"] = forms.BooleanField(label="", required=False, initial=False)
        self.fields["inhouse_homozygous"] = forms.IntegerField(
            label="",
            initial=20,
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal in-house hom. count", "class": "numberInteger"}
            ),
        )
        self.fields["inhouse_heterozygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal in-house het. count", "class": "numberInteger"}
            ),
        )
        self.fields["inhouse_hemizygous"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal in-house hemi. count", "class": "numberInteger"}
            ),
        )
        self.fields["inhouse_carriers"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={"placeholder": "Maximal in-house carriers", "class": "numberInteger"}
            ),
        )
        self.fields["mtdb_enabled"] = forms.BooleanField(label="", required=False, initial=True)
        self.fields["mtdb_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in mtDB",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["mtdb_count"] = forms.IntegerField(
            label="",
            initial=10,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal count in mtDB",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["helixmtdb_enabled"] = forms.BooleanField(
            label="", required=False, initial=True
        )
        self.fields["helixmtdb_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in HelixMTdb",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["helixmtdb_hom_count"] = forms.IntegerField(
            label="",
            initial=10,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal hom. count in HelixMTdb",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["helixmtdb_het_count"] = forms.IntegerField(
            label="",
            initial=10,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal het. count in HelixMTdb",
                    "class": "numberInteger",
                }
            ),
        )
        self.fields["mitomap_enabled"] = forms.BooleanField(label="", required=False, initial=True)
        self.fields["mitomap_frequency"] = forms.DecimalField(
            label="",
            initial=0.01,
            max_value=1,
            min_value=0,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal frequency in MITOMAP",
                    "class": "numberDecimal",
                }
            ),
        )
        self.fields["mitomap_count"] = forms.IntegerField(
            label="",
            initial=10,
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal count in MITOMAP",
                    "class": "numberInteger",
                }
            ),
        )


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
        self.fields["effect_exon_loss_variant"] = forms.BooleanField(
            label="exon loss", required=False, initial=True
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

        self.fields["max_exon_dist"] = forms.IntegerField(
            label="",
            required=False,
            widget=forms.TextInput(
                attrs={
                    "placeholder": "Maximal distance to exon in bp. Leave empty to ignore.",
                    "class": "numberInteger",
                }
            ),
        )

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
            initial=200,
            help_text=(
                "Maximal number of rows displayed <b>when rendering on the website</b>.  "
                "This setting is <b>not</b> used when creating a file for export."
            ),
            widget=forms.TextInput(attrs={"class": "numberInteger"}),
        )

        self.fields["training_mode"] = forms.BooleanField(
            label="Training mode",
            required=False,
            initial=False,
            help_text=(
                "Activating this option hides the bookmark icons and omits the row colouring of flagged variants "
                "in the results table. It is intended for trainees to check if they can validate previous findings."
            ),
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

        self.fields["remove_if_in_dbsnp"] = forms.BooleanField(
            label="Remove if has dbSNP ID",
            required=False,
            initial=False,
            help_text=(
                "Remove variant from results list if it has an associated dbSNP ID. "
                "This option is ignored when ClinVar membership is required!"
            ),
        )

        self.fields["clinvar_paranoid_mode"] = forms.BooleanField(
            label="enable 'paranoid' mode",
            required=False,
            initial=False,
            help_text=(
                "When set, then variant assessments with and without assertion "
                "are interpreted as equally important.  By default, they are not "
                "those with assessment override the others."
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
        return cleaned_data


class VariantGeneListFilterFormMixin:
    """Form mixin with gene blocklist/allowlist fields and region list."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["gene_blocklist"] = forms.CharField(
            label="Gene Blocklist",
            help_text=(
                "Enter a list of HGNC symbols, Entrez IDs, or ENSEMBL gene IDs separated by spaces or line break."
                "<strong>The input is case sensitive!</strong>"
            ),
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter genes to block-list here",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            required=False,
            max_length=1_000_000,
        )

        self.fields["gene_allowlist"] = forms.CharField(
            label="Gene Allowlist",
            help_text=(
                "Enter a list of HGNC symbols, Entrez IDs, or ENSEMBL gene IDs separated by spaces or line break."
                "<strong>The input is case sensitive!</strong>"
            ),
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter genes to allow-list here",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            required=False,
            max_length=1_000_000,
        )

    def clean(self):
        """Translate effect field names into ``effects`` key list"""
        cleaned_data = super().clean()
        cleaned_data["gene_blocklist"] = [
            s.strip() for s in cleaned_data["gene_blocklist"].strip().split() if s.strip()
        ]
        cleaned_data["gene_allowlist"] = [
            s.strip() for s in cleaned_data["gene_allowlist"].strip().split() if s.strip()
        ]

        def _check_list(list_name):
            mismatches = [
                gene
                for gene in cleaned_data[list_name]
                if not Hgnc.objects.filter(
                    Q(hgnc_id=gene) | Q(entrez_id=gene) | Q(ensembl_gene_id=gene) | Q(symbol=gene)
                )
            ]
            if mismatches:
                self.add_error(
                    list_name,
                    "Can't find HGNC ID/symbol, Entrez ID or ENSEMBL gene ID: {}".format(
                        "; ".join(mismatches)
                    ),
                )

        _check_list("gene_blocklist")
        _check_list("gene_allowlist")

        return cleaned_data


class GenomicRegionFilterFormMixin:
    """Form mixin with genomic regions field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["genomic_region"] = forms.CharField(
            label="Genomic Region",
            help_text="Enter a list of genomic regions, separated by spaces or line break.",
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter regions to filter here, e.g., chr1:1,000,000-2,000,000 or chrX",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            required=False,
            max_length=10000,
        )

    def clean(self):
        """Turn entries into lines."""
        cleaned_data = super().clean()
        results = []
        malformed = []
        for entry in cleaned_data["genomic_region"].strip().split():
            entry_ = entry.strip()
            if entry_:
                m = re.match("^(?:chr)?([0-9MTXY]+)(?::([0-9,]+)-([0-9,]+))?$", entry_)
                if m:
                    results.append(
                        (
                            m[1],
                            int(m[2].replace(",", "")) if m[2] else None,
                            int(m[3].replace(",", "")) if m[3] else None,
                        )
                    )
                else:
                    malformed.append(entry_)
        if malformed:
            self.add_error(
                "genomic_region",
                "Invalid chromosomal region formatting: {}".format("; ".join(malformed)),
            )

        cleaned_data["genomic_region"] = results
        return cleaned_data


class SmallVariantPrioritizerFormMixin:
    """Form mixin with prioritizer fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial["prio_algorithm"] = PRIO_HIPHIVE_HUMAN

        self.fields["prio_enabled"] = forms.BooleanField(
            label="Enable phenotype-based prioritization",
            help_text=(
                "Note well that only variants in the first %d genes returned by your query will be prioritized!"
            )
            % settings.VARFISH_EXOMISER_PRIORITISER_MAX_GENES,
            required=False,
            widget=forms.CheckboxInput(),
        )

        self.fields["prio_algorithm"] = forms.ChoiceField(
            label="Algorithm",
            help_text=(
                "Prioritizer algorithm to use. Phenix uses known human disease gene, Phive also uses information "
                "from mouse models, and HiPhive also uses zebrafish and protein-protein interaction."
            ),
            choices=PRIO_ALGORITHM_CHOICES,
            required=False,
        )

        self.fields["prio_hpo_terms"] = forms.CharField(
            label="",
            help_text=(
                "Click a suggestion to add it to the text field, or type into text field. This field is sodar "
                "compatible. HPO and OMIM terms are <kbd>;</kbd> separated. Enter an HPO or OMIM id, optionally with the name, "
                "separated by <kbd> - </kbd>. Only HPO or OMIM ids are considered, i.e. the text can be arbitrary and does not "
                "have to match the actual name. It serves just your orientation."
            ),
            widget=forms.Textarea(
                attrs={
                    "placeholder": "Enter HPO or OMIM terms here (e.g. HP:1234567; OMIM:123456) or click a suggestion above ...",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            max_length=5000,
            required=False,
        )

        self.fields["patho_enabled"] = forms.BooleanField(
            label="Enable variant pathogenicity-based prioritization",
            help_text=(
                "First try to filter your variants without pathogenicity-based prioritization before enabling it. "
                "Note well that only the first %d variants returned by your query will be prioritized!"
            )
            % settings.VARFISH_CADD_MAX_VARS,
            required=False,
            widget=forms.CheckboxInput(),
        )

        #: Choices for variant scoring methods.
        PATHO_SCORE_CHOICES = [(PATHO_MUTATIONTASTER, PATHO_MUTATIONTASTER_LABEL)]
        PATHO_SCORE_INITIAL = (PATHO_MUTATIONTASTER, PATHO_MUTATIONTASTER_LABEL)
        if settings.VARFISH_ENABLE_CADD:
            PATHO_SCORE_CHOICES.append((PATHO_CADD, PATHO_CADD_LABEL))
            PATHO_SCORE_INITIAL = (PATHO_CADD, PATHO_CADD_LABEL)
        if app_settings.get_app_setting("variants", "umd_predictor_api_token", user=self.superuser):
            PATHO_SCORE_CHOICES.append((PATHO_UMD, PATHO_UMD_LABEL))

        self.fields["patho_score"] = forms.ChoiceField(
            label="Score",
            help_text="Pathogenicity scoring method to use.",
            choices=PATHO_SCORE_CHOICES,
            initial=PATHO_SCORE_INITIAL,
            required=False,
        )

    def clean(self):
        """Tokenize the HPO terms"""
        cleaned_data = super().clean()
        results = []
        results_curated = []
        for raw_term in cleaned_data["prio_hpo_terms"].split(";"):
            raw_term = raw_term.strip()
            if raw_term:
                m = re.match(r"^(HP:\d{7}|OMIM:\d{6}|DECIPHER:\d+|ORPHA:\d+)(?: - .*)?$", raw_term)
                if m:
                    term = m.group(1)
                    if term.startswith("HP"):
                        if not HpoName.objects.filter(hpo_id=term).exists():
                            self.add_error(
                                "prio_hpo_terms", "%s doesn't exist in HPO database" % term
                            )
                        else:
                            results_curated.append(term)
                            results.append(term)
                    else:
                        records = Hpo.objects.filter(database_id=term)
                        if not records.exists():
                            self.add_error(
                                "prio_hpo_terms", "%s doesn't exist in HPO database" % term
                            )
                        else:
                            results.append(term)
                            for record in records.values("hpo_id"):
                                results_curated.append(record["hpo_id"])
                else:
                    self.add_error(
                        "prio_hpo_terms",
                        "%s is not a valid HPO, OMIM, DECIPHER or ORPHA id (expecting HP:1234567 or OMIM:123456)"
                        % raw_term,
                    )
        cleaned_data["prio_hpo_terms"] = sorted(set(results))
        cleaned_data["prio_hpo_terms_curated"] = sorted(set(results_curated))
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
    SmallVariantPrioritizerFormMixin,
    VariantGeneListFilterFormMixin,
    GenomicRegionFilterFormMixin,
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
            ("submit-cadd", "Submit to CADD"),
            ("submit-spanr", "Submit to SPANR"),
        )
    )

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        self.superuser = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def get_pedigree(self):
        """Return ``list`` of ``dict`` with pedigree information."""
        return self.case.pedigree

    def get_pedigree_with_samples(self):
        """Return ``list`` of ``dict`` with pedigree information of samples that have variants."""
        return self.case.get_filtered_pedigree_with_samples()

    def get_family_with_pedigree_with_samples(self):
        """Return ``dict`` of ``dict`` with family and pedigree information of samples that have variants and a variant set."""
        return self.case.get_family_with_filtered_pedigree_with_samples()

    def get_default_families(self):
        """Return the registered index patient of the family."""
        trio = self.get_trio_roles()
        return [
            {"index": self.case.index, "mother": trio.get("mother"), "father": trio.get("father")}
        ]

    @lru_cache()
    def get_trio_roles(self):
        """Get trio role to member mapping"""
        return self.case.get_trio_roles()

    @lru_cache()
    def get_active_cases(self):
        """Return case as a list."""
        return [self.case]

    def clean(self):
        """Perform data cleaning and cross-field validation.

        Currently, ensures only that only one sample is selected for export in case of MutationDistiller submission.
        """
        cleaned_data = super().clean()
        # If submit is "submit-mutationdistiller" then only one sample can be checked for export.
        if cleaned_data["submit"] == "submit-mutationdistiller":
            number_selected = sum(
                [
                    cleaned_data[self.get_quality_field_names()[member["patient"]]["export"]]
                    for member in self.get_pedigree_with_samples()
                ]
            )
            if not number_selected == 1:
                raise forms.ValidationError(
                    "MutationDistiller only supports export of a single individual. "
                    'Please select exactly one donor in "More ..."/"Configure Downloads" tab.'
                )
        return cleaned_data


class ProjectCasesFilterForm(
    SmallVariantFlagsFilterFormMixin,
    SmallVariantExportFilterFormMixin,
    SmallVariantFrequencyFilterFormMixin,
    SmallVariantVariantEffectFilterFormMixin,
    SmallVariantMiscFilterFormMixin,
    SmallVariantClinvarHgmdFilterFormMixin,
    SmallVariantPrioritizerFormMixin,
    VariantGeneListFilterFormMixin,
    GenomicRegionFilterFormMixin,
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
        cohort = kwargs.pop("cohort")
        project = kwargs.pop("project")
        self.project_or_cohort = cohort or project
        self.superuser = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if cohort:
            self.fields["cohort"] = forms.CharField(
                widget=forms.HiddenInput(), initial=str(cohort.sodar_uuid)
            )

    def get_pedigree(self):
        """Return ``list`` of ``dict`` with pedigree information."""
        return self.project_or_cohort.pedigree(self.superuser)

    def get_pedigree_with_samples(self):
        """Return ``dict`` of ``dict`` with family and pedigree information of samples that have variants and a variant set."""
        return self.project_or_cohort.get_filtered_pedigree_with_samples(self.superuser)

    def get_family_with_pedigree_with_samples(self):
        """Return ``dict`` of ``dict`` with family and pedigree information of samples that have variants and a variant set."""
        return self.project_or_cohort.get_family_with_filtered_pedigree_with_samples(self.superuser)

    def get_default_families(self):
        """Return the registered index patient of the family."""
        pedigree = self.get_pedigree()
        indices = self.project_or_cohort.indices(self.superuser)
        ret = []
        for member in pedigree:
            for index in indices:
                if member["patient"] == index:
                    ret.append(
                        {"index": index, "mother": member["mother"], "father": member["father"]}
                    )
                    # Break the inner loop
                    break
        return ret

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
        if not self.get_pedigree():
            raise forms.ValidationError("No samples to process.")
        return cleaned_data


class SmallVariantFlagsForm(forms.ModelForm):
    """Form for validating small variant flags."""

    class Meta:
        model = SmallVariantFlags
        exclude = ("case", "sodar_uuid", "date_created", "date_modified", "chromosome_no")


class SmallVariantCommentForm(forms.ModelForm):
    """Form for validating small variant comments."""

    class Meta:
        model = SmallVariantComment
        exclude = ("case", "sodar_uuid", "user", "date_created", "date_modified", "chromosome_no")


class ProjectStatsJobForm(forms.Form):
    """Form class used for confirmation of recomputing project-wide statistics."""


class SyncProjectJobForm(forms.Form):
    """Form class used for confirmation of performing sync with remote."""


class AcmgCriteriaRatingForm(forms.ModelForm):
    """Form for giving the ACMG criteria."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["empty"] = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = AcmgCriteriaRating
        exclude = ("user", "bin", "sodar_uuid", "case", "date_created", "date_modified")

    def clean(self):
        self.cleaned_data["empty"] = True
        keys = (
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
            "class_override",
        )
        for i in keys:
            if self.cleaned_data.get(i):
                self.cleaned_data["empty"] = False
                break
        return self.cleaned_data


class CaseNotesStatusForm(forms.ModelForm):
    """Form for taking case notes."""

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project")
        super().__init__(*args, **kwargs)
        tags_string = app_settings.get_app_setting("variants", "user_defined_tags", project=project)
        if tags_string:
            self.fields["tags"].widget.choices = [
                (x.strip(), x.strip()) for x in tags_string.split(";")
            ]
        else:
            self.fields["tags"].disabled = True

    class Meta:
        model = Case
        fields = ("status", "tags", "notes")
        labels = {"notes": "", "status": "", "tags": ""}
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-control form-control-sm selectpicker mb-2"}
            ),
            "tags": forms.SelectMultiple(
                attrs={"class": "form-control form-control-sm selectpicker mb-2"}
            ),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control form-control-sm"}),
        }


class CaseCommentsForm(forms.ModelForm):
    """Form for commenting a case."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comment"].required = False

    class Meta:
        model = CaseComments
        fields = ("comment",)
        labels = {"comment": ""}
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 1,
                    "class": "form-control from-control-sm",
                    "placeholder": "Enter comment here",
                }
            )
        }


#: Regular expression to find terms.
RE_FIND_TERMS = r"(HP:\d{7}|OMIM:\d{6}|DECIPHER:\d+|ORPHA:\d+)"


class CaseTermsForm(forms.Form):
    """Form for updating the case phenotype and disease annotation."""

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop("case")
        super().__init__(*args, **kwargs)
        self._create_fields()

    def _create_fields(self):
        name_terms = {pt.individual: pt for pt in self.case.phenotype_terms.all()}
        for name in [p["patient"] for p in self.case.pedigree]:
            name_terms.setdefault(name, None)
        for name, terms in sorted(name_terms.items()):
            self.fields["terms-%s" % name] = forms.CharField(
                label="Terms for %s" % only_source_name(name),
                widget=forms.Textarea(
                    attrs={"placeholder": "e.g., HP:0001680, OMIM:616145, ORPHA:1388, ..."}
                ),
                initial=self._build_initial(terms),
                required=False,
            )

    def clean(self):
        """Validate the fields."""
        cleaned_data = super().clean()
        errors = {}
        updates = {}
        for field, value in cleaned_data.items():
            if field.startswith("terms-"):
                lines = []
                for m in re.findall(RE_FIND_TERMS, value):
                    description = get_term_description(m)
                    if not description:
                        errors.setdefault(field, []).append("Unknown term: %s" % m)
                    lines.append("%s - %s" % (m, description or "UNKNOWN TERM"))
                updates[field] = "\n".join(lines)
        cleaned_data.update(updates)
        for key, msgs in errors.items():
            for msg in msgs:
                self.add_error(key, msg)
        return cleaned_data

    def _build_initial(self, pheno_terms=None):
        if not pheno_terms:
            return None
        else:
            return (
                "\n".join(
                    [
                        "%s - %s" % (term, get_term_description(term) or "UNKNOWN TERM")
                        for term in pheno_terms.terms
                    ]
                )
                + "\n"
            )


class KioskUploadForm(forms.Form):
    """Form for uploading the user's data."""

    vcf_file = forms.FileField(
        label="VCF File",
        required=True,
        help_text="Select the VCF file to upload (compressed or uncompressed).",
    )

    ped_file = forms.FileField(
        label="PED File",
        required=False,
        help_text="Optional PED file with pedigree information, you can also type the text below.",
    )

    ped_text = forms.CharField(
        label="PED Text",
        required=False,
        help_text="Alternatively, type the PED file here. If both are given, the file has precedence.",
        widget=forms.Textarea(
            attrs={
                "rows": "3",
                "class": "form-input",
                "placeholder": (
                    "FAM index father mother 1 2\n" "FAM father 0 0 1 1\n" "FAM mother 0 0 2 1"
                ),
            }
        ),
    )

    def clean(self):
        raw_uploads_dir = os.path.join(settings.MEDIA_ROOT, "raw_uploads")
        try:
            os.mkdir(raw_uploads_dir)
        except FileExistsError:
            pass
        with tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT) as tmp_file:
            shutil.copyfileobj(self.cleaned_data.get("vcf_file"), tmp_file)
            save_file(
                tmp_file, get_valid_filename(self.cleaned_data.get("vcf_file")), raw_uploads_dir
            )
            tmp_file.flush()
            self.cleaned_data.get("vcf_file").seek(0)
        ped_samples = []
        ped_source = None
        if self.cleaned_data.get("ped_file"):
            with tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT) as tmp_file:
                shutil.copyfileobj(self.cleaned_data.get("ped_file"), tmp_file)
                save_file(tmp_file, self.cleaned_data.get("ped_file").name, raw_uploads_dir)
                tmp_file.flush()
                self.cleaned_data.get("ped_file").seek(0)
            self.cleaned_data["ped"] = list(
                map(lambda x: x.decode("utf-8").rstrip("\n"), self.cleaned_data.get("ped_file"))
            )
            ped_source = "ped_file"
        elif self.cleaned_data.get("ped_text"):
            self.cleaned_data["ped"] = [
                "\t".join(line.split()) for line in self.cleaned_data["ped_text"].splitlines()
            ]
            ped_source = "ped_text"

        if self.cleaned_data.get("ped") and ped_source:
            for line in self.cleaned_data["ped"]:
                arr = line.split("\t")
                if len(arr) != 6:
                    self.add_error(
                        ped_source, "Line must have 6 fields but has %d: %s" % (len(arr), line)
                    )
                    break
                ped_samples.append(arr[1])

        # Make file name valid (replace spaces, etc ...)
        self.cleaned_data["vcf_file"].name = get_valid_filename(self.cleaned_data["vcf_file"])

        # Simple file-extension check for vcf format (gzipped or not)
        if not self.cleaned_data["vcf_file"].name.lower().endswith((".vcf", ".vcf.gz")):
            self.add_error("vcf_file", "Please only upload VCF files!")
            return

        # Check that samples can be read from the file.
        suffix = (
            ".vcf.gz"
            if self.cleaned_data.get("vcf_file").name.lower().endswith(".vcf.gz")
            else ".vcf"
        )
        with tempfile.NamedTemporaryFile(suffix=suffix, dir=settings.MEDIA_ROOT) as tmp_file:
            shutil.copyfileobj(self.cleaned_data.get("vcf_file"), tmp_file)
            tmp_file.flush()
            self.cleaned_data.get("vcf_file").seek(0)
            try:
                vcf_header = vcfpy.Reader.from_path(tmp_file.name).header
                vcf_samples = vcf_header.samples.names
                # Check if samples are available at all
                if not vcf_samples:
                    self.add_error("vcf_file", "No samples present in VCF file!")
                    return
                self.cleaned_data["vcf_index"] = vcf_samples[0]
                # Check if samples in vcf file match those in ped file (only performed if ped is available)
                if ped_samples and set(vcf_samples) != set(ped_samples):
                    self.add_error(
                        "vcf_file",
                        "Samples from VCF file (%s) do not match those from pedigree (%s)"
                        % (", ".join(sorted(vcf_samples)), ", ".join(sorted(ped_samples))),
                    )
                    return
                if not ped_samples:
                    self.cleaned_data["ped"] = [
                        "\t".join(["FAM", sample, "0", "0", "1", "2"]) for sample in vcf_samples
                    ]
                # Check for correct genome build
                for entry in list(vcf_header.get_lines("contig")):
                    # GRCh38/hg38?
                    if entry.id in ("chr1", "1") and int(entry.length) == 248956422:
                        self.add_error("vcf_file", "Only GRCh37 build is supported!")
                        return
            except Exception as e:
                self.add_error("vcf_file", "Problem with VCF file: %s" % e)
                return

        return self.cleaned_data

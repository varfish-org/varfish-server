"""Common fixture code for testing the ``svs`` app."""

import binning

from projectroles.models import Project

from svdbs.models import G1K_CALLSET_DEL_UNION
from ..models import StructuralVariant, StructuralVariantGeneAnnotation
from .. import models

# ---------------------------------------------------------------------------
# Dictionaries for setting up database
# ---------------------------------------------------------------------------

#: Shared data for ``Project`` to use for all ``svs`` test cases.
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

#: Share data for setting up a ``Case``.
CASE_DICT = {
    "sodar_uuid": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    "name": "sample1",
    "index": "sample1-N1-DNA1-WGS1",
    "pedigree": [
        {
            "sex": 1,
            "father": "sample2-N1-DNA1-WGS1",
            "mother": "sample3-N1-DNA1-WGS1",
            "patient": "sample1-N1-DNA1-WGS1",
            "affected": 2,
            "has_gt_entries": True,
        },
        {
            "sex": 2,
            "father": "0",
            "mother": "0",
            "patient": "sample2-N1-DNA1-WGS1",
            "affected": 1,
            "has_gt_entries": True,
        },
        {
            "sex": 2,
            "father": "0",
            "mother": "0",
            "patient": "sample2-N1-DNA1-WGS1",
            "affected": 1,
            "has_gt_entries": True,
        },
    ],
}

#: Structural variant that deletes SHH.
#:
#: SHH lies at ``chr7:155,595,558-155,604,967``.
STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION = {
    "release": "GRCh37",
    "chromosome": "7",
    "start": 155_579_762,
    "end": 155_628_829,
    "bin": binning.assign_bin(155_579_761, 155_628_829),
    "containing_bins": binning.containing_bins(155_579_761, 155_628_829),
    "start_ci_left": 0,
    "start_ci_right": 0,
    "end_ci_left": 0,
    "end_ci_right": 0,
    "sv_uuid": "20ae7eff-8741-4d2c-9d35-8f3bd9211b78",
    "caller": "EMBL.DELLYv0.7.8",
    "sv_type": "DEL",
    "sv_sub_type": "DEL",
    "info": {"backgroundCarriers": 1, "affectedCarriers": 1, "unaffectedCarriers": 1},
    "genotype": {
        "sample1-N1-DNA1-WGS1": {
            "gt": "0/1",  # genotype
            "gq": 10,
            "src": 10,  # split read coverage
            "srv": 5,  # variant split reads
            "pec": 10,  # paired-end coverage
            "pev": 5,  # variant paired-ends
        },
        "sample2-N1-DNA1-WGS1": {"gt": "0/0", "gq": 10, "src": 10, "srv": 5, "pec": 10, "pev": 5},
        "sample3-N1-DNA1-WGS1": {"gt": "0/0", "gq": 10, "src": 10, "srv": 5, "pec": 10, "pev": 5},
    },
}

#: The gene annotation for ``STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION``.
STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION_ANNOTATION = {
    "sv_uuid": "20ae7eff-8741-4d2c-9d35-8f3bd9211b78",
    "refseq_gene_id": "6469",
    "refseq_transcript_id": "NM_000193.2",
    "refseq_transcript_coding": True,
    "refseq_effect": ["transcript_ablation", "coding_transcript_variant"],
    "ensembl_gene_id": None,
    "ensembl_transcript_id": None,
    "ensembl_transcript_coding": False,
    "ensembl_effect": [],
}


#: Structural variant that does not affect a transcript.
#:
#: This is left of SHH.
STRUCTURAL_VARIANT_DICT_2_NON_CODING = {
    "release": "GRCh37",
    "chromosome": "7",
    "start": 155_580_774,
    "end": 155_585_255,
    "bin": binning.assign_bin(155_580_773, 155_585_255),
    "containing_bins": binning.containing_bins(155_580_773, 155_585_255),
    "start_ci_left": 0,
    "start_ci_right": 0,
    "end_ci_left": 0,
    "end_ci_right": 0,
    "sv_uuid": "646d9642-8908-4120-a54f-5492e3cd14dd",
    "caller": "EMBL.DELLYv0.7.8",
    "sv_type": "DEL",
    "sv_sub_type": "DEL",
    "info": {"backgroundCarriers": 1, "affectedCarriers": 1, "unaffectedCarriers": 1},
    "genotype": {
        "sample1-N1-DNA1-WGS1": {"gt": "0/1"},
        "sample2-N1-DNA1-WGS1": {"gt": "0/0"},
        "sample3-N1-DNA1-WGS1": {"gt": "0/0"},
    },
}

# ---------------------------------------------------------------------------
# Fixture DB Information
# ---------------------------------------------------------------------------

DGV_SV_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1000,
    "end": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "accession": "sv1",
    "sv_type": "DEL",
    "sv_sub_type": "DEL",
    "study": "study1",
    "platform": ["platform1"],
    "num_samples": 1,
    "observed_gains": 0,
    "observed_losses": 1,
}

DGV_SV_GS_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start_inner": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 2000,
    "start_outer": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"],
    "end_inner": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 2000,
    "end_outer": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"],
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "accession": "sv1",
    "sv_type": "DEL",
    "sv_sub_type": "DEL",
    "num_studies": 1,
    "studies": ["study1"],
    "num_platforms": 1,
    "platforms": ["platform1"],
    "num_algorithms": 1,
    "algorithms": ["algorithms"],
    "num_variants": 1,
    "num_carriers": 1,
    "num_unique_samples": 1,
    "num_carriers_african": 0,
    "num_carriers_asian": 0,
    "num_carriers_european": 0,
    "num_carriers_mexican": 1,
    "num_carriers_middle_east": 0,
    "num_carriers_native_american": 0,
    "num_carriers_north_american": 0,
    "num_carriers_oceania": 0,
    "num_carriers_south_american": 0,
    "num_carriers_admixed": 0,
    "num_carriers_unknown": 0,
}

G1K_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1000,
    "end": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "start_ci_left": 10,
    "start_ci_right": 10,
    "end_ci_left": 10,
    "end_ci_right": 10,
    "sv_type": "DEL",
    "source_call_set": G1K_CALLSET_DEL_UNION,
    "mobile_element_info": [],
    "num_samples": 1,
    "num_alleles": 2,
    "num_var_alleles": 1,
    "num_alleles_afr": 0,
    "num_var_alleles_afr": 0,
    "num_alleles_amr": 0,
    "num_var_alleles_amr": 0,
    "num_alleles_eas": 0,
    "num_var_alleles_eas": 0,
    "num_alleles_eur": 2,
    "num_var_alleles_eur": 1,
    "num_alleles_sas": 0,
    "num_var_alleles_sas": 0,
}

EXAC_CNV_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1000,
    "end": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "sv_type": "DEL",
    "population": "SAS",
    "phred_score": 40,
}

DB_VAR_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1000,
    "end": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "num_carriers": 1,
    "sv_type": "DEL",
    "method": "method1",
    "analysis": "method1",
    "platform": "platform1",
    "study": "study1",
    "clinical_assertions": ["assertion1"],
    "clinvar_accessions": ["accessiono1"],
    "bin_size": 42,
    "min_ins_length": None,
    "max_ins_length": None,
}

GNOMAD_SV_DICT = {
    "release": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["release"],
    "chromosome": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "start": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1000,
    "end": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    "bin": binning.assign_bin(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "containing_bins": binning.containing_bins(
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"] - 1001,
        STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"] - 1000,
    ),
    "ref": "N",
    "alt": ["<DEL>"],
    "name": "del1",
    "svtype": "DEL",
    "svlen": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["end"]
    - STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["start"],
    "filter": ["PASS"],
    "evidence": ["PR", "SR"],
    "algorithms": ["delly"],
    "chr2": STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION["chromosome"],
    "cpx_type": None,
    "cpx_intervals": [],
    "source": None,
    "strands": None,
    "unresolved_type": None,
    "pcrplus_depleted": False,
    "pesr_gt_overdispersion": False,
    "protein_coding_lof": [],
    "protein_coding_dup_lof": [],
    "protein_coding_copy_gain": [],
    "protein_coding_dup_partial": [],
    "protein_coding_msv_exon_ovr": [],
    "protein_coding_intronic": [],
    "protein_coding_inv_span": [],
    "protein_coding_utr": [],
    "protein_coding_nearest_tss": [],
    "protein_coding_intergenic": False,
    "protein_coding_promoter": [],
    "an": 2,
    "ac": [1],
    "af": [0.5],
    "n_bi_genos": 1,
    "n_homref": 0,
    "n_het": 1,
    "n_homalt": 0,
    "freq_homref": 0.0,
    "freq_het": 1.0,
    "freq_homalt": 0.0,
    "popmax_af": 1.0,
    "afr_an": 2,
    "afr_ac": [1],
    "afr_af": [0.5],
    "afr_n_bi_genos": 1,
    "afr_n_homref": 0,
    "afr_n_het": 1,
    "afr_n_homalt": 0,
    "afr_freq_homref": 0.0,
    "afr_freq_het": 1.0,
    "afr_freq_homalt": 0.0,
    "amr_an": 0,
    "amr_ac": [0],
    "amr_af": [0.5],
    "amr_n_bi_genos": 0,
    "amr_n_homref": 0,
    "amr_n_het": 0,
    "amr_n_homalt": 0,
    "amr_freq_homref": 0,
    "amr_freq_het": 0,
    "amr_freq_homalt": 0,
    "eas_an": 0,
    "eas_ac": [0],
    "eas_af": [0.5],
    "eas_n_bi_genos": 0,
    "eas_n_homref": 0,
    "eas_n_het": 0,
    "eas_n_homalt": 0,
    "eas_freq_homref": 0,
    "eas_freq_het": 0,
    "eas_freq_homalt": 0,
    "eur_an": 0,
    "eur_ac": [0],
    "eur_af": [0.5],
    "eur_n_bi_genos": 0,
    "eur_n_homref": 0,
    "eur_n_het": 0,
    "eur_n_homalt": 0,
    "eur_freq_homref": 0,
    "eur_freq_het": 0,
    "eur_freq_homalt": 0,
    "oth_an": 0,
    "oth_ac": [0],
    "oth_af": [0.5],
    "oth_n_bi_genos": 0,
    "oth_n_homref": 0,
    "oth_n_het": 0,
    "oth_n_homalt": 0,
    "oth_freq_homref": 0,
    "oth_freq_het": 0,
    "oth_freq_homalt": 0,
}

# ---------------------------------------------------------------------------
# Dictionaries with query data
# ---------------------------------------------------------------------------

#: Dict with cleaned data
BASE_CLEANED_DATA = {
    "database_select": "refseq",
    # NB: no genotype values, only per-case
    # DB Frequency values
    "enable_dgv_filter": True,
    "dgv_min_overlap": "0.75",
    "dgv_max_carriers": None,
    "enable_dgv_gs_filter": True,
    "dgv_gs_min_overlap": "0.75",
    "dgv_gs_max_carriers": None,
    "enable_dbvar_filter": True,
    "dbvar_min_overlap": "0.75",
    "dbvar_max_carriers": None,
    "enable_exac_filter": True,
    "exac_min_overlap": "0.75",
    "exac_max_carriers": None,
    "enable_g1k_filter": True,
    "g1k_min_overlap": "0.75",
    "g1k_max_carriers": None,
    # Cohort frequency values.
    "collective_enabled": False,
    "cohort_affected_carriers_min": None,
    "cohort_affected_carriers_max": None,
    "cohort_unaffected_carriers_min": None,
    "cohort_unaffected_carriers_max": None,
    "cohort_background_carriers_min": None,
    "cohort_background_carriers_max": None,
    # Variant Types
    "sv_type": [
        models.SV_TYPE_DEL,
        models.SV_TYPE_DUP,
        models.SV_TYPE_INS,
        models.SV_TYPE_INV,
        models.SV_TYPE_BND,
        models.SV_TYPE_CNV,
    ],
    "sv_sub_type": [
        models.SV_SUB_TYPE_DEL,
        models.SV_SUB_TYPE_DEL_ME_ALU,
        models.SV_SUB_TYPE_DEL_ME,
        models.SV_SUB_TYPE_DEL_ME_L1,
        models.SV_SUB_TYPE_DEL_ME_SVA,
        models.SV_SUB_TYPE_DUP,
        models.SV_SUB_TYPE_DUP_TANDEM,
        models.SV_SUB_TYPE_INS,
        models.SV_SUB_TYPE_INS_ME_ALU,
        models.SV_SUB_TYPE_INS_ME_L1,
        models.SV_SUB_TYPE_INS_ME_SVA,
        models.SV_SUB_TYPE_INV,
        models.SV_SUB_TYPE_BND,
        models.SV_SUB_TYPE_CNV,
    ],
    # Effects
    "require_transcript_overlap": True,
    "effects": ["transcript_ablation"],
    "transcripts_coding": True,
    "transcripts_noncoding": True,
    # Sizes
    "sv_size_min": None,
    "sv_size_max": None,
    # Quality
    # NB: comes per-case
    # Whitelist/Blacklist
    "gene_whitelist": [],
    "gene_blacklist": [],
    # Intervals
    "region_whitelist": [],
    # ENSEMBL regulatory features from
    "regulatory_ensembl": [],
    # VISTA regulatory features from
    "regulatory_vista": [],
}

#: Dict with base cleaned data for case 1.
BASE_CLEANED_DATA_CASE_1 = {
    **BASE_CLEANED_DATA,
    "sample1-N1-DNA1-WGS1_gt": "any",
    "sample1-N1-DNA1-WGS1_fail": "no-call",
    "sample1-N1-DNA1-WGS1_gq_min": 0,
    "sample1-N1-DNA1-WGS1_src_min": 0,
    "sample1-N1-DNA1-WGS1_srv_min": 0,
    "sample1-N1-DNA1-WGS1_srv_max": 1000,
    "sample1-N1-DNA1-WGS1_pec_min": 0,
    "sample1-N1-DNA1-WGS1_pev_min": 0,
    "sample1-N1-DNA1-WGS1_pev_max": 1000,
    "sample1-N1-DNA1-WGS1_cov_min": 0,
    "sample1-N1-DNA1-WGS1_var_min": 0,
    "sample1-N1-DNA1-WGS1_var_max": 1000,
    "sample2-N1-DNA1-WGS1_gt": "any",
    "sample2-N1-DNA1-WGS1_fail": "no-call",
    "sample2-N1-DNA1-WGS1_gq_min": 0,
    "sample2-N1-DNA1-WGS1_src_min": 0,
    "sample2-N1-DNA1-WGS1_srv_min": 0,
    "sample2-N1-DNA1-WGS1_srv_max": 1000,
    "sample2-N1-DNA1-WGS1_pec_min": 0,
    "sample2-N1-DNA1-WGS1_pev_min": 0,
    "sample2-N1-DNA1-WGS1_pev_max": 1000,
    "sample2-N1-DNA1-WGS1_cov_min": 0,
    "sample2-N1-DNA1-WGS1_var_min": 0,
    "sample2-N1-DNA1-WGS1_var_max": 1000,
    "sample3-N1-DNA1-WGS1_gt": "any",
    "sample3-N1-DNA1-WGS1_fail": "no-call",
    "sample3-N1-DNA1-WGS1_gq_min": 0,
    "sample3-N1-DNA1-WGS1_src_min": 0,
    "sample3-N1-DNA1-WGS1_srv_min": 0,
    "sample3-N1-DNA1-WGS1_srv_max": 1000,
    "sample3-N1-DNA1-WGS1_pec_min": 0,
    "sample3-N1-DNA1-WGS1_pev_min": 0,
    "sample3-N1-DNA1-WGS1_pev_max": 1000,
    "sample3-N1-DNA1-WGS1_cov_min": 0,
    "sample3-N1-DNA1-WGS1_var_min": 0,
    "sample3-N1-DNA1-WGS1_var_max": 1000,
}

# ---------------------------------------------------------------------------
# Test Case 1: de novo deletion of SHH
# ---------------------------------------------------------------------------

# A simple de novo deletion of the whole transcript of SHH.


def fixture_setup_case1_simple():
    """Setup test case 1 -- a de novo deletion in SHH"""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(**CASE_DICT)
    StructuralVariant.objects.create(case_id=case.pk, **STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION)
    StructuralVariantGeneAnnotation.objects.create(
        **STRUCTURAL_VARIANT_DICT_1_SHH_ABLATION_ANNOTATION
    )
    StructuralVariant.objects.create(case_id=case.pk, **STRUCTURAL_VARIANT_DICT_2_NON_CODING)

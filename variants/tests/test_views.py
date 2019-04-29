"""Tests for the filter view"""

import json

import aldjemy.core
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils import timezone
from test_plus.test import TestCase
from requests_mock import Mocker
from unittest.mock import patch
from django.conf import settings

from projectroles.models import Project
from annotation.models import Annotation
from variants.models import (
    Case,
    SmallVariant,
    ExportFileBgJob,
    ExportFileJobResult,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    ExportProjectCasesFileBgJob,
    ExportProjectCasesFileBgJobResult,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    SmallVariantFlags,
    SmallVariantComment,
    ClinvarBgJob,
    ClinvarQuery,
)
from variants.variant_stats import rebuild_case_variant_stats
from clinvar.models import Clinvar
from frequencies.models import Exac, GnomadGenomes, GnomadExomes, ThousandGenomes
from conservation.models import KnowngeneAA
from geneinfo.models import RefseqToHgnc, Hpo, HpoName, Mim2geneMedgen, Hgnc

from ._fixtures import CLINVAR_DEFAULTS, CLINVAR_FORM_DEFAULTS

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()

# Shared project settings
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

# Default form settings
DEFAULT_FILTER_FORM_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "A_export": True,
    "compound_recessive_enabled": False,
    "effect_coding_transcript_intron_variant": True,
    "effect_complex_substitution": True,
    "effect_direct_tandem_duplication": True,
    "effect_disruptive_inframe_deletion": True,
    "effect_disruptive_inframe_insertion": True,
    "effect_downstream_gene_variant": True,
    "effect_exon_loss_variant": True,
    "effect_feature_truncation": True,
    "effect_five_prime_UTR_exon_variant": True,
    "effect_five_prime_UTR_intron_variant": True,
    "effect_frameshift_elongation": True,
    "effect_frameshift_truncation": True,
    "effect_frameshift_variant": True,
    "effect_inframe_deletion": True,
    "effect_inframe_insertion": True,
    "effect_intergenic_variant": True,
    "effect_internal_feature_elongation": True,
    "effect_missense_variant": True,
    "effect_mnv": True,
    "effect_non_coding_transcript_exon_variant": True,
    "effect_non_coding_transcript_intron_variant": True,
    "effect_splice_acceptor_variant": True,
    "effect_splice_donor_variant": True,
    "effect_splice_region_variant": True,
    "effect_start_lost": True,
    "effect_stop_gained": True,
    "effect_stop_lost": True,
    "effect_stop_retained_variant": True,
    "effect_structural_variant": True,
    "effect_synonymous_variant": True,
    "effect_three_prime_UTR_exon_variant": True,
    "effect_three_prime_UTR_intron_variant": True,
    "effect_transcript_ablation": True,
    "effect_upstream_gene_variant": True,
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "export_flags": True,
    "export_comments": True,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "training_mode": False,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "inhouse_enabled": False,
    "inhouse_carriers": 0,
    "inhouse_heterozygous": 0,
    "inhouse_homozygous": 0,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
    "display_hgmd_public_membership": False,
    # Gene lists
    "gene_blacklist": "",
    "gene_whitelist": "",
    "genomic_region": "",
    # Flags
    "flag_bookmarked": True,
    "flag_candidate": True,
    "flag_final_causative": True,
    "flag_for_validation": True,
    "flag_phenotype_match_empty": True,
    "flag_phenotype_match_negative": True,
    "flag_phenotype_match_positive": True,
    "flag_phenotype_match_uncertain": True,
    "flag_simple_empty": True,
    "flag_summary_empty": True,
    "flag_summary_negative": True,
    "flag_summary_positive": True,
    "flag_summary_uncertain": True,
    "flag_validation_empty": True,
    "flag_validation_negative": True,
    "flag_validation_positive": True,
    "flag_validation_uncertain": True,
    "flag_visual_empty": True,
    "flag_visual_negative": True,
    "flag_visual_positive": True,
    "flag_visual_uncertain": True,
    # Submit buttons
    "submit": "display",
}

# Default joint filter form settings
DEFAULT_JOINT_FILTER_FORM_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "B_fail": "ignore",
    "B_gt": "any",
    "B_dp_het": 0,
    "B_dp_hom": 0,
    "B_gq": 0,
    "B_ad": 0,
    "B_ab": 0.0,
    "C_fail": "ignore",
    "C_gt": "any",
    "C_dp_het": 0,
    "C_dp_hom": 0,
    "C_gq": 0,
    "C_ad": 0,
    "C_ab": 0.0,
    "compound_recessive_enabled": False,
    "effect_coding_transcript_intron_variant": True,
    "effect_complex_substitution": True,
    "effect_direct_tandem_duplication": True,
    "effect_disruptive_inframe_deletion": True,
    "effect_disruptive_inframe_insertion": True,
    "effect_downstream_gene_variant": True,
    "effect_exon_loss_variant": True,
    "effect_feature_truncation": True,
    "effect_five_prime_UTR_exon_variant": True,
    "effect_five_prime_UTR_intron_variant": True,
    "effect_frameshift_elongation": True,
    "effect_frameshift_truncation": True,
    "effect_frameshift_variant": True,
    "effect_inframe_deletion": True,
    "effect_inframe_insertion": True,
    "effect_intergenic_variant": True,
    "effect_internal_feature_elongation": True,
    "effect_missense_variant": True,
    "effect_mnv": True,
    "effect_non_coding_transcript_exon_variant": True,
    "effect_non_coding_transcript_intron_variant": True,
    "effect_splice_acceptor_variant": True,
    "effect_splice_donor_variant": True,
    "effect_splice_region_variant": True,
    "effect_start_lost": True,
    "effect_stop_gained": True,
    "effect_stop_lost": True,
    "effect_stop_retained_variant": True,
    "effect_structural_variant": True,
    "effect_synonymous_variant": True,
    "effect_three_prime_UTR_exon_variant": True,
    "effect_three_prime_UTR_intron_variant": True,
    "effect_transcript_ablation": True,
    "effect_upstream_gene_variant": True,
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "export_flags": True,
    "export_comments": True,
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "training_mode": False,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
    "display_hgmd_public_membership": False,
    # Gene lists
    "gene_blacklist": "",
    "gene_whitelist": "",
    "genomic_region": "",
    # Flags
    "flag_bookmarked": True,
    "flag_candidate": True,
    "flag_final_causative": True,
    "flag_for_validation": True,
    "flag_phenotype_match_empty": True,
    "flag_phenotype_match_negative": True,
    "flag_phenotype_match_positive": True,
    "flag_phenotype_match_uncertain": True,
    "flag_simple_empty": True,
    "flag_summary_empty": True,
    "flag_summary_negative": True,
    "flag_summary_positive": True,
    "flag_summary_uncertain": True,
    "flag_validation_empty": True,
    "flag_validation_negative": True,
    "flag_validation_positive": True,
    "flag_validation_uncertain": True,
    "flag_visual_empty": True,
    "flag_visual_negative": True,
    "flag_visual_positive": True,
    "flag_visual_uncertain": True,
    # Submit buttons
    "submit": "display",
}

DEFAULT_RESUBMIT_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "A_export": True,
    "compound_recessive_enabled": False,
    "effects": [
        "coding_transcript_intron_variant",
        "complex_substitution",
        "direct_tandem_duplication",
        "disruptive_inframe_deletion",
        "disruptive_inframe_insertion",
        "downstream_gene_variant",
        "feature_truncation",
        "five_prime_UTR_exon_variant",
        "five_prime_UTR_intron_variant",
        "frameshift_elongation",
        "frameshift_truncation",
        "frameshift_variant",
        "inframe_deletion",
        "inframe_insertion",
        "intergenic_variant",
        "internal_feature_elongation",
        "missense_variant",
        "mnv",
        "non_coding_transcript_exon_variant",
        "non_coding_transcript_intron_variant",
        "splice_acceptor_variant",
        "splice_donor_variant",
        "splice_region_variant",
        "start_lost",
        "stop_gained",
        "stop_lost",
        "stop_retained_variant",
        "structural_variant",
        "synonymous_variant",
        "three_prime_UTR_exon_variant",
        "three_prime_UTR_intron_variant",
        "transcript_ablation",
        "upstream_gene_variant",
    ],
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "export_flags": True,
    "export_comments": True,
    "gene_blacklist": "",
    "gene_whitelist": "",
    "genomic_region": "",
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "training_mode": False,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "inhouse_enabled": False,
    "inhouse_carriers": 0,
    "inhouse_heterozygous": 0,
    "inhouse_homozygous": 0,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "submit": "display",
}


CLINVAR_RESUBMIT_SETTING = {
    "A_gt": "variant",
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_likely_pathogenic": False,
    "clinvar_include_pathogenic": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_origin_germline": True,
    "clinvar_origin_somatic": False,
    "clinvar_status_conflict": True,
    "clinvar_status_expert_panel": True,
    "clinvar_status_multiple_no_conflict": True,
    "clinvar_status_no_assertion": True,
    "clinvar_status_no_criteria": True,
    "clinvar_status_practice_guideline": True,
    "clinvar_status_single": True,
    "database_select": "refseq",
    "flag_bookmarked": True,
    "flag_candidate": True,
    "flag_final_causative": True,
    "flag_for_validation": True,
    "flag_phenotype_match_empty": True,
    "flag_phenotype_match_negative": True,
    "flag_phenotype_match_positive": True,
    "flag_phenotype_match_uncertain": True,
    "flag_simple_empty": True,
    "flag_summary_empty": True,
    "flag_summary_negative": True,
    "flag_summary_positive": True,
    "flag_summary_uncertain": True,
    "flag_validation_empty": True,
    "flag_validation_negative": True,
    "flag_validation_positive": True,
    "flag_validation_uncertain": True,
    "flag_visual_empty": True,
    "flag_visual_negative": True,
    "flag_visual_positive": True,
    "flag_visual_uncertain": True,
    "require_in_clinvar": True,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "display_hgmd_public_membership": True,
    "result_rows_limit": 500,
    "submit": "display",
}


DEFAULT_JOINT_RESUBMIT_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "A_export": True,
    "B_fail": "ignore",
    "B_gt": "any",
    "B_dp_het": 0,
    "B_dp_hom": 0,
    "B_gq": 0,
    "B_ad": 0,
    "B_ab": 0.0,
    "B_export": True,
    "C_fail": "ignore",
    "C_gt": "any",
    "C_dp_het": 0,
    "C_dp_hom": 0,
    "C_gq": 0,
    "C_ad": 0,
    "C_ab": 0.0,
    "C_export": True,
    "compound_recessive_enabled": False,
    "effects": [
        "coding_transcript_intron_variant",
        "complex_substitution",
        "direct_tandem_duplication",
        "disruptive_inframe_deletion",
        "disruptive_inframe_insertion",
        "downstream_gene_variant",
        "feature_truncation",
        "five_prime_UTR_exon_variant",
        "five_prime_UTR_intron_variant",
        "frameshift_elongation",
        "frameshift_truncation",
        "frameshift_variant",
        "inframe_deletion",
        "inframe_insertion",
        "intergenic_variant",
        "internal_feature_elongation",
        "missense_variant",
        "mnv",
        "non_coding_transcript_exon_variant",
        "non_coding_transcript_intron_variant",
        "splice_acceptor_variant",
        "splice_donor_variant",
        "splice_region_variant",
        "start_lost",
        "stop_gained",
        "stop_lost",
        "stop_retained_variant",
        "structural_variant",
        "synonymous_variant",
        "three_prime_UTR_exon_variant",
        "three_prime_UTR_intron_variant",
        "transcript_ablation",
        "upstream_gene_variant",
    ],
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "export_flags": True,
    "export_comments": True,
    "gene_blacklist": "",
    "gene_whitelist": "",
    "genomic_region": "",
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "training_mode": False,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "inhouse_enabled": False,
    "inhouse_carriers": 0,
    "inhouse_heterozygous": 0,
    "inhouse_homozygous": 0,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "submit": "display",
}


def fixture_setup_case(user):
    """Set up test case for filter tests. Contains a case with three variants."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )

    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        "in_clinvar": False,
        # frequencies
        "exac_frequency": 0.01,
        "exac_homozygous": 0,
        "exac_heterozygous": 0,
        "exac_hemizygous": 0,
        "thousand_genomes_frequency": 0.01,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 0,
        "thousand_genomes_hemizygous": 0,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 0,
        "gnomad_exomes_hemizygous": 0,
        "gnomad_genomes_frequency": 0.01,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 0,
        "gnomad_genomes_hemizygous": 0,
        # RefSeq
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    a = SmallVariant.objects.create(**{**basic_var, **{"position": 100}})
    b = SmallVariant.objects.create(
        **{**basic_var, **{"position": 200, "in_clinvar": True, "refseq_gene_id": "2234"}}
    )
    c = SmallVariant.objects.create(**{**basic_var, **{"position": 300, "refseq_gene_id": "2234"}})

    rebuild_case_variant_stats(SQLALCHEMY_ENGINE, case)

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "position": 200,
            "start": 200,
            "stop": 200,
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )

    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a962", user=user, job_type="type"
    )

    smallvariantquery = SmallVariantQuery.objects.create(
        case=case,
        user=user,
        form_id="1",
        form_version=1,
        query_settings=DEFAULT_RESUBMIT_SETTING,
        public=False,
    )

    smallvariantquery.query_results.add(a, c)

    clinvarjob = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a963", user=user, job_type="type"
    )

    clinvarquery = ClinvarQuery.objects.create(
        case=case,
        user=user,
        form_id="1",
        form_version=1,
        query_settings=CLINVAR_RESUBMIT_SETTING,
        public=False,
    )

    clinvarquery.query_results.add(b)

    project.clinvarbgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3202",
        bg_job=clinvarjob,
        case=case,
        clinvarquery=clinvarquery,
    )

    return project.filterbgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3201",
        bg_job=job,
        case=case,
        smallvariantquery=smallvariantquery,
    )


def fixture_setup_projectcases(user):
    """Set up test case for filter tests. Contains a case with three variants."""
    project = Project.objects.create(**PROJECT_DICT)
    case1 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e4",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    case2 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e5",
        name="B",
        index="B",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "B",
                "affected": 1,
                "has_gt_entries": True,
            },
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "C",
                "affected": 1,
                "has_gt_entries": True,
            },
        ],
    )

    basic_var = {
        "case_id": None,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": None,
        "in_clinvar": False,
        # frequencies
        "exac_frequency": 0.01,
        "exac_homozygous": 0,
        "exac_heterozygous": 0,
        "exac_hemizygous": 0,
        "thousand_genomes_frequency": 0.01,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 0,
        "thousand_genomes_hemizygous": 0,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 0,
        "gnomad_exomes_hemizygous": 0,
        "gnomad_genomes_frequency": 0.01,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 0,
        "gnomad_genomes_hemizygous": 0,
        # RefSeq
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    a = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "position": 100,
            "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        }
    )
    b = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "position": 200,
            "in_clinvar": True,
            "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        }
    )
    c = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "position": 300,
            "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        }
    )
    d = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "position": 100,
            "genotype": {
                "B": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            },
        }
    )
    e = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "position": 200,
            "in_clinvar": True,
            "genotype": {
                "B": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            },
        }
    )
    f = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "position": 300,
            "genotype": {
                "B": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
                "C": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"},
            },
        }
    )

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "position": 200,
            "start": 200,
            "stop": 200,
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )

    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a963", user=user, job_type="type"
    )

    projectcasessmallvariantquery = ProjectCasesSmallVariantQuery.objects.create(
        project=project,
        user=user,
        form_id="1",
        form_version=1,
        query_settings=DEFAULT_JOINT_RESUBMIT_SETTING,
        public=False,
    )

    projectcasessmallvariantquery.query_results.add(a, c, d, e, f)

    return project.projectcasesfilterbgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3202",
        bg_job=job,
        projectcasessmallvariantquery=projectcasessmallvariantquery,
    )


def fixture_setup_distiller(user):
    """Create setup for distiller job submission testing."""
    project = Project.objects.create(**PROJECT_DICT)

    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e6",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )

    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a967", user=user, job_type="type"
    )

    project.distillersubmissionbgjob_set.create(
        case=case, query_args=DEFAULT_RESUBMIT_SETTING, distiller_project_id="12345", bg_job=job
    )


class TestViewBase(TestCase):
    """Base class for view testing (and file export)"""

    setup_case_in_db = None

    def setUp(self):
        self.request_factory = RequestFactory()

        # setup super user
        self.user = self.make_user("superuser")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        # some fixtures need the created user
        self.__class__.setup_case_in_db(self.user)


class TestCaseListView(TestViewBase):
    """Test case list view"""

    setup_case_in_db = fixture_setup_case

    # TODO
    #   dp_medians = null
    #   dp_medians = null

    def test_render(self):
        """Test display of case list page."""
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.get(
                reverse("variants:case-list", kwargs={"project": project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 1)


class TestCaseDetailView(TestViewBase):
    """Test case detail view"""

    setup_case_in_db = fixture_setup_case

    def test_render(self):
        """Test display of case detail view page."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()

            response = self.client.get(
                reverse(
                    "variants:case-detail",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].name, "A")


class TestCaseFilterView(TestViewBase):
    """Test case filter view"""

    setup_case_in_db = fixture_setup_case

    def test_status_code_200(self):
        """Test display of the filter forms, no submit."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)

    def test_post_download(self):
        """Test form submit for download as file."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 0)
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "submit": "download"},
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            created_job = ExportFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:export-job-detail",
                    kwargs={"project": case.project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )

    @Mocker()
    def test_post_mutation_distiller(self, mock):
        with self.login(self.user):
            from ..submit_external import DISTILLER_POST_URL

            mock.post(
                DISTILLER_POST_URL,
                status_code=200,
                text=(
                    '\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<HTM'
                    'L>\n<HEAD>\n<TITLE>testsubmission - QueryEngine initialising</TITLE>\n<meta http-equiv="refresh" content="5; U'
                    'RL=/temp/QE/vcf_10585_21541/progress.html">\n<link href="/MutationTaster/css.css" rel="stylesheet" type="text/'
                    'css">\n</head><body>\n\n\t\t<table  border="0" width="100%" cellspacing="20">\n\t\t\t<tr>\n\t\t\t\t<td style="'
                    'text-align:center"><img src="/MutationTaster/MutationTaster_small.png" alt="Yum, tasty mutations..." align="le'
                    'ft"></td>\n\t\t\t\t<td ><h1>testsubmission - QueryEngine initialising</h1></td>\n\t\t\t\t<td><A HREF="/Mutatio'
                    'nTaster/info/MTQE_documentation.html" TARGET="_blank">MTQE documentation</A></td>\n\t\t\t</tr>\n\t\t</table> <'
                    "h1>testsubmission - QueryEngine initialising</h1>\n<h2>We are uploading your file. NEVER press reload or F5 - "
                    "unless you want to start from the very beginning. </h2>MutationTaster QueryEngine: vcf number 10585<br>"
                ),
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 0)
            case = Case.objects.select_related("project").first()

            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "submit": "submit-mutationdistiller"},
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 1)
            created_job = DistillerSubmissionBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": case.project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )


class TestCasePrefetchFilterView(TestViewBase):
    """Tests for CasePrefetchFilterView.
    """

    setup_case_in_db = fixture_setup_case

    def test_get_job_id(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                DEFAULT_FILTER_FORM_SETTING,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(FilterBgJob.objects.last().sodar_uuid),
            )

    def test_invalid_form(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "exac_frequency": "I am supposed to be a float."},
            )

            self.assertEqual(response.status_code, 400)
            self.assertTrue("exac_frequency" in json.loads(response.content.decode("utf-8")))


class TestCaseFilterJobView(TestViewBase):
    """Tests for CaseFilterJobView.
    """

    setup_case_in_db = fixture_setup_case

    def test_status_code_200(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            bgjob = FilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:case-filter-job",
                    kwargs={
                        "project": case.project.sodar_uuid,
                        "case": case.sodar_uuid,
                        "job": bgjob.sodar_uuid,
                    },
                ),
                DEFAULT_FILTER_FORM_SETTING,
            )
            self.assertEqual(response.status_code, 200)


class TestCaseLoadPrefetchedFilterView(TestViewBase):
    """Tests for CaseLoadPrefetchedFilterView.
    """

    setup_case_in_db = fixture_setup_case

    def test_count_results(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    **DEFAULT_FILTER_FORM_SETTING,
                    "filter_job_uuid": FilterBgJob.objects.first().sodar_uuid,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 2)
            self.assertEqual(response.context["training_mode"], False)

    def test_training_mode(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            query = SmallVariantQuery.objects.first()
            query.query_settings["training_mode"] = True
            query.save()
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    **DEFAULT_FILTER_FORM_SETTING,
                    "filter_job_uuid": FilterBgJob.objects.first().sodar_uuid,
                },
            )
            self.assertEqual(response.context["training_mode"], True)

    @patch("django.conf.settings.VARFISH_ENABLE_EXOMISER_PRIORITISER", True)
    @patch("django.conf.settings.VARFISH_ENABLE_CADD", True)
    @patch("django.conf.settings.VARFISH_EXOMISER_PRIORITISER_API_URL", "https://exomiser.com")
    @patch("django.conf.settings.VARFISH_CADD_REST_API_URL", "https://cadd.com")
    @Mocker()
    def test_ranking_results(self, mock):
        mock.get(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "results": [
                        {
                            "geneId": 1234,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                        {
                            "geneId": 2234,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                    ]
                }
            ),
        )
        mock.post(
            settings.VARFISH_CADD_REST_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "scores": {
                        "1-100-A-G": [0.345146, 7.773],
                        "1-200-A-G": [0.345179, 7.773],
                        "1-300-A-G": [0.345212, 7.774],
                    }
                }
            ),
        )
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    **DEFAULT_FILTER_FORM_SETTING,
                    "prio_enabled": True,
                    "prio_algorithm": "phenix",
                    "prio_hpo_terms": ["HP:0000001"],
                    "patho_enabled": True,
                    "patho_score": "phenix",  # ?
                },
            )
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    **DEFAULT_FILTER_FORM_SETTING,
                    "filter_job_uuid": FilterBgJob.objects.last().sodar_uuid,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 3)
            self.assertEqual(response.context["training_mode"], False)
            self.assertEqual(response.context["has_phenotype_scores"], True)
            self.assertEqual(response.context["has_pathogenicity_scores"], True)
            self.assertEqual(response.context["result_rows"][0].pathogenicity_score, 7.774)
            self.assertEqual(response.context["result_rows"][0].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][0].joint_score, 0.1 * 7.774)
            self.assertEqual(response.context["result_rows"][0].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][0].pathogenicity_rank, 1)
            self.assertEqual(response.context["result_rows"][0].joint_rank, 1)
            self.assertEqual(response.context["result_rows"][1].pathogenicity_score, 7.773)
            self.assertEqual(response.context["result_rows"][1].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][1].joint_score, 0.1 * 7.773)
            self.assertEqual(response.context["result_rows"][1].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][1].pathogenicity_rank, 1)
            self.assertEqual(response.context["result_rows"][1].joint_rank, 1)
            self.assertEqual(response.context["result_rows"][2].pathogenicity_score, 7.773)
            self.assertEqual(response.context["result_rows"][2].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][2].joint_score, 0.1 * 7.773)
            self.assertEqual(response.context["result_rows"][2].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][2].pathogenicity_rank, 2)
            self.assertEqual(response.context["result_rows"][2].joint_rank, 2)


class TestFilterJobDetailView(TestViewBase):
    """Tests for FilterJobDetailView.
    """

    setup_case_in_db = fixture_setup_case

    def test_status_code_200(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, "A")


class TestFilterJobResubmitView(TestViewBase):
    """Tests for FilterJobResubmitView.
    """

    setup_case_in_db = fixture_setup_case

    def test_redirect(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:filter-job-resubmit",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            created_job = FilterBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:filter-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestFilterJobGetStatus(TestViewBase):
    """Tests for FilterJobGetStatusView.
    """

    setup_case_in_db = fixture_setup_case

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.post(
                reverse("variants:filter-job-status", kwargs={"project": bgjob.project.sodar_uuid}),
                {"filter_job_uuid": bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.post(
                reverse("variants:filter-job-status", kwargs={"project": bgjob.project.sodar_uuid}),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.post(
                reverse("variants:filter-job-status", kwargs={"project": bgjob.project.sodar_uuid}),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestFilterJobGetPrevious(TestViewBase):
    """Tests for FilterJobGetPreviousView.
    """

    setup_case_in_db = fixture_setup_case

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:filter-job-previous",
                    kwargs={"project": bgjob.project.sodar_uuid, "case": bgjob.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            bgjob = FilterBgJob.objects.first()
            project = bgjob.project.sodar_uuid
            case = bgjob.case.sodar_uuid
            bgjob.delete()
            response = self.client.get(
                reverse("variants:filter-job-previous", kwargs={"project": project, "case": case})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestProjectCasesFilterJobGetStatus(TestViewBase):
    """Tests for ProjectCasesFilterJobGetStatusView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestProjectCasesFilterJobGetPrevious(TestViewBase):
    """Tests for ProjectCasesFilterJobGetPreviousView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-previous",
                    kwargs={"project": bgjob.project.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            project = bgjob.project.sodar_uuid
            bgjob.delete()
            response = self.client.get(
                reverse("variants:project-cases-filter-job-previous", kwargs={"project": project})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestProjectCasesFilterView(TestViewBase):
    """Tests for FilterProjectCasesFilterView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_status_code_200(self):
        """Test display of the filter forms, no submit."""
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.get(
                reverse("variants:project-cases-filter", kwargs={"project": project.sodar_uuid})
            )

            self.assertEqual(response.status_code, 200)

    def test_post_download(self):
        """Test form submit for download as file."""
        with self.login(self.user):
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
            project = Project.objects.first()
            response = self.client.post(
                reverse("variants:project-cases-filter", kwargs={"project": project.sodar_uuid}),
                {**DEFAULT_JOINT_FILTER_FORM_SETTING, "submit": "download"},
            )
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
            created_job = ExportProjectCasesFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={"project": project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )


class TestProjectCasesPrefetchFilterView(TestViewBase):
    """Tests for FilterProjectCasesPrefetchFilterView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_count_results(self):
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-results", kwargs={"project": project.sodar_uuid}
                ),
                DEFAULT_JOINT_FILTER_FORM_SETTING,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(ProjectCasesFilterBgJob.objects.last().sodar_uuid),
            )

    def test_invalid_form(self):
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-results", kwargs={"project": project.sodar_uuid}
                ),
                {
                    **DEFAULT_JOINT_FILTER_FORM_SETTING,
                    "exac_frequency": "I am supposed to be a float.",
                },
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("exac_frequency" in json.loads(response.content.decode("utf-8")))


class TestProjectCasesFilterJobDetailView(TestViewBase):
    """Tests for ProjectCasesFilterJobDetailView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_status_code_200(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_project_name(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].project.title, "project")


class TestProjectCasesLoadPrefetchedFilterView(TestViewBase):
    """Tests for ProjectCasesLoadPrefetchedFilterView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_count_results(self):
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-load-filter-results",
                    kwargs={"project": project.sodar_uuid},
                ),
                {
                    **DEFAULT_JOINT_FILTER_FORM_SETTING,
                    "filter_job_uuid": ProjectCasesFilterBgJob.objects.first().sodar_uuid,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 8)
            self.assertEqual(len(response.context["result_rows"]), 8)


class TestProjectCasesFilterJobResubmitView(TestViewBase):
    """Tests for ProjectCasesFilterJobResubmitView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_redirect(self):
        with self.login(self.user):
            bgjob = ProjectCasesFilterBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-resubmit",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            created_job = ProjectCasesFilterBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestCaseClinvarReportView(TestViewBase):
    """Test case Clinvar report view"""

    setup_case_in_db = fixture_setup_case

    # TODO
    #   _yield_grouped_rows: when candidates = null
    #     status_level(status): when status not found
    #     sig_level(significance): when significance not found

    def test_get_renders_form(self):
        """Test that GET returns the form"""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:case-clinvar",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context[-1].get("form"))

    def test_get_renders_form_with_given_job(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:case-clinvar-job",
                    kwargs={
                        "project": case.project.sodar_uuid,
                        "case": case.sodar_uuid,
                        "job": bgjob.sodar_uuid,
                    },
                ),
                CLINVAR_FORM_DEFAULTS,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context[-1].get("form"))


class TestCasePrefetchClinvarReportView(TestViewBase):
    """Test CasePrefetchClinvarReportView"""

    setup_case_in_db = fixture_setup_case

    def test_get_job_id(self):
        """Test that an appropriate POST returns a report"""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:clinvar-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**CLINVAR_FORM_DEFAULTS, "submit": "display"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(ClinvarBgJob.objects.last().sodar_uuid),
            )


class TestClinvarReportJobDetailView(TestViewBase):
    """Test ClinvarReportJobDetailView"""

    setup_case_in_db = fixture_setup_case

    def test_status_code_200(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:clinvar-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)


class TestClinvarReportJobResubmitView(TestViewBase):
    """Test ClinvarReportJobResubmitView"""

    setup_case_in_db = fixture_setup_case

    def test_redirect(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-resubmit",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            created_job = ClinvarBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:clinvar-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestCaseLoadPrefetchedClinvarReportView(TestViewBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    setup_case_in_db = fixture_setup_case

    def test_count_results(self):
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:load-clinvar-results",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    **CLINVAR_FORM_DEFAULTS,
                    "filter_job_uuid": ClinvarBgJob.objects.first().sodar_uuid,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 1)


class TestCaseClinvarReportJobGetStatus(TestViewBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    setup_case_in_db = fixture_setup_case

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestCaseClinvarReportJobGetPrevious(TestViewBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    setup_case_in_db = fixture_setup_case

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:clinvar-job-previous",
                    kwargs={"project": bgjob.project.sodar_uuid, "case": bgjob.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            bgjob = ClinvarBgJob.objects.first()
            project = bgjob.project.sodar_uuid
            case = bgjob.case.sodar_uuid
            bgjob.delete()
            response = self.client.get(
                reverse("variants:clinvar-job-previous", kwargs={"project": project, "case": case})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestDistillerSubmissionJobDetailView(TestViewBase):
    """Tests for DistillerSubmissionJobDetailView.
    """

    setup_case_in_db = fixture_setup_distiller

    def test_status_code_200(self):
        with self.login(self.user):
            bgjob = DistillerSubmissionBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.user):
            bgjob = DistillerSubmissionBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": bgjob.project.sodar_uuid, "job": bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, "A")


class TestDistillerSubmissionJobResubmitView(TestViewBase):
    """Tests for DistillerSubmissionJobResubmitView.
    """

    setup_case_in_db = fixture_setup_case

    @Mocker()
    def test_resubmission(self, mock):
        with self.login(self.user):
            # Mock post
            from ..submit_external import DISTILLER_POST_URL

            mock.post(
                DISTILLER_POST_URL,
                status_code=200,
                text=(
                    '\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<HTM'
                    'L>\n<HEAD>\n<TITLE>testsubmission - QueryEngine initialising</TITLE>\n<meta http-equiv="refresh" content="5; U'
                    'RL=/temp/QE/vcf_10585_21541/progress.html">\n<link href="/MutationTaster/css.css" rel="stylesheet" type="text/'
                    'css">\n</head><body>\n\n\t\t<table  border="0" width="100%" cellspacing="20">\n\t\t\t<tr>\n\t\t\t\t<td style="'
                    'text-align:center"><img src="/MutationTaster/MutationTaster_small.png" alt="Yum, tasty mutations..." align="le'
                    'ft"></td>\n\t\t\t\t<td ><h1>testsubmission - QueryEngine initialising</h1></td>\n\t\t\t\t<td><A HREF="/Mutatio'
                    'nTaster/info/MTQE_documentation.html" TARGET="_blank">MTQE documentation</A></td>\n\t\t\t</tr>\n\t\t</table> <'
                    "h1>testsubmission - QueryEngine initialising</h1>\n<h2>We are uploading your file. NEVER press reload or F5 - "
                    "unless you want to start from the very beginning. </h2>MutationTaster QueryEngine: vcf number 10585<br>"
                ),
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 0)
            case = Case.objects.select_related("project").first()
            # Create background job
            self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "submit": "submit-mutationdistiller"},
            )
            first_bgjob = DistillerSubmissionBgJob.objects.last()
            # Re-submit background job
            response = self.client.post(
                reverse(
                    "variants:distiller-job-resubmit",
                    kwargs={"project": case.project.sodar_uuid, "job": first_bgjob.sodar_uuid},
                )
            )
            # Check existence of resubmitted job
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 2)
            second_bgjob = DistillerSubmissionBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": case.project.sodar_uuid, "job": second_bgjob.sodar_uuid},
                ),
            )


def fixture_setup_small_variant_details(user):
    """Setup test case for expand view. Contains project and frequency objects"""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )

    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        "in_clinvar": False,
        # frequencies
        "exac_frequency": 0.01,
        "exac_homozygous": 0,
        "exac_heterozygous": 0,
        "exac_hemizygous": 0,
        "thousand_genomes_frequency": 0.01,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 0,
        "thousand_genomes_hemizygous": 0,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 0,
        "gnomad_exomes_hemizygous": 0,
        "gnomad_genomes_frequency": 0.01,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 0,
        "gnomad_genomes_hemizygous": 0,
        # RefSeq
        "refseq_gene_id": "12345",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }
    SmallVariant.objects.create(**{**basic_var, **{"position": 100}})

    basic_pop = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
        "ac": None,
        "ac_afr": 10,
        "ac_amr": 0,
        "ac_eas": 0,
        "ac_fin": 0,
        "ac_nfe": 0,
        "ac_oth": 0,
        "an": None,
        "an_afr": 8726,
        "an_amr": 838,
        "an_eas": 1620,
        "an_fin": 3464,
        "an_nfe": 14996,
        "an_oth": 982,
        "hemi": None,
        "hemi_afr": None,
        "hemi_amr": None,
        "hemi_eas": None,
        "hemi_fin": None,
        "hemi_nfe": None,
        "hemi_oth": None,
        "hom": 0,
        "hom_afr": 2,
        "hom_amr": 0,
        "hom_eas": 0,
        "hom_fin": 0,
        "hom_nfe": 0,
        "hom_oth": 0,
        "popmax": "AFR",
        "ac_popmax": 1,
        "an_popmax": 8726,
        "af_popmax": 0.0001146,
        "hemi_popmax": None,
        "hom_popmax": 0,
        "af": None,
        "af_afr": 0.0001146,
        "af_amr": 0.0,
        "af_eas": 0.0,
        "af_fin": 0.0,
        "af_nfe": 0.0,
        "af_oth": 0.0,
    }

    Exac.objects.create(
        **{
            **basic_pop,
            **{"ac_sas": 3, "an_sas": 323, "hemi_sas": None, "hom_sas": 0, "af_sas": 0.0},
        }
    )
    ThousandGenomes.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        ac=3,
        an=5008,
        het=3,
        hom=0,
        af=0.000058,
        af_afr=0.0,
        af_amr=0.0054,
        af_eas=0.0,
        af_eur=0.0,
        af_sas=0.0,
    )
    GnomadExomes.objects.create(
        **{
            **basic_pop,
            **{
                "ac_asj": 4,
                "ac_sas": 3,
                "an_asj": 323,
                "an_sas": 932,
                "hemi_asj": None,
                "hemi_sas": None,
                "hom_asj": 0,
                "hom_sas": 0,
                "af_asj": 0.0,
                "af_sas": 0.0,
            },
        }
    )
    GnomadGenomes.objects.create(
        **{
            **basic_pop,
            **{"ac_asj": 4, "an_asj": 323, "hemi_asj": None, "hom_asj": 0, "af_asj": 0.0},
        }
    )
    KnowngeneAA.objects.create(
        chromosome="1", start=99, end=101, transcript_id="ENSG0001", alignment="XXX"
    )
    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "position": 100,
            "start": 100,
            "stop": 100,
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )
    RefseqToHgnc.objects.create(entrez_id="12345", hgnc_id="HGNC:1")
    Hpo.objects.create(
        database_id="OMIM:55555",
        hpo_id="HP:0000001",
        name="Disease1;;Alternative Description Disease1",
    )
    Hpo.objects.create(database_id="OMIM:55555", hpo_id="HP:0000007", name="Disease1; ABBR")
    HpoName.objects.create(hpo_id="HP:0000001", name="All")
    HpoName.objects.create(hpo_id="HP:0000007", name="Autosomal recessive")
    Mim2geneMedgen.objects.create(omim_id=55555, entrez_id="12345", omim_type="phenotype")
    Hgnc.objects.create(hgnc_id="HGNC:1", ensembl_gene_id="ENSG0001", symbol="AAA")
    Annotation.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        database="refseq",
        effect=[],
        gene_id="12345",
        transcript_id="NR_00001.1",
        transcript_coding=False,
        hgvs_c=None,
        hgvs_p=None,
    )
    Annotation.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        database="refseq",
        effect=[],
        gene_id="12345",
        transcript_id="NR_00002.1",
        transcript_coding=False,
        hgvs_c=None,
        hgvs_p=None,
    )
    Annotation.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        database="ensembl",
        effect=[],
        gene_id="12345",
        transcript_id="ENST0001",
        transcript_coding=False,
        hgvs_c=None,
        hgvs_p=None,
    )
    Annotation.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        database="ensembl",
        effect=[],
        gene_id="12345",
        transcript_id="ENST0002",
        transcript_coding=False,
        hgvs_c=None,
        hgvs_p=None,
    )


class TestSmallVariantDetailsView(TestViewBase):
    """Test variant details view"""

    setup_case_in_db = fixture_setup_small_variant_details

    # TODO
    #   _get_gene_infos database refseq
    #   _get_gene_infos with data from gene
    #   if self.request.GET.get("render_full", "no").lower() in ("yes", "true"): ... true

    def test_render(self):
        """Test rendering of the variant detail view"""
        with self.login(self.user):
            case = Case.objects.first()
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": case.project.sodar_uuid,
                        "case": case.sodar_uuid,
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                        "database": "refseq",
                        "gene_id": "12345",
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_content_refseq(self):
        with self.login(self.user):
            case = Case.objects.first()
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": case.project.sodar_uuid,
                        "case": case.sodar_uuid,
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                        "database": "refseq",
                        "gene_id": "12345",
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["af"], 0.0001146)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["hom"], 2)
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["af"], 0.0001146
            )
            self.assertEqual(response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["hom"], 2)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["af"], 0.0001146)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["hom"], 2)
            self.assertEqual(response.context["pop_freqs"]["1000GP"]["AMR"]["af"], 0.0054)
            self.assertEqual(response.context["clinvar"][0]["clinical_significance"], "pathogenic")
            self.assertEqual(response.context["knowngeneaa"][0]["alignment"], "XXX")
            self.assertEqual(response.context["gene"]["hpo_terms"][0][0], "HP:0000001")
            self.assertEqual(response.context["gene"]["hpo_terms"][0][1], "All")
            self.assertEqual(response.context["gene"]["hpo_inheritance"][0][0], "HP:0000007")
            self.assertEqual(response.context["gene"]["hpo_inheritance"][0][1], "AR")
            self.assertEqual(response.context["gene"]["omim"][55555][0], "Disease1")
            self.assertEqual(
                response.context["gene"]["omim"][55555][1][0], "Alternative Description Disease1"
            )
            self.assertEqual(response.context["gene"]["symbol"], "AAA")
            self.assertEqual(response.context["effect_details"][0]["transcript_id"], "NR_00001.1")
            self.assertEqual(response.context["effect_details"][1]["transcript_id"], "NR_00002.1")

    def test_content_ensembl(self):
        with self.login(self.user):
            case = Case.objects.first()
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": case.project.sodar_uuid,
                        "case": case.sodar_uuid,
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                        "database": "ensembl",
                        "gene_id": "ENSG0001",
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["af"], 0.0001146)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["hom"], 2)
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["af"], 0.0001146
            )
            self.assertEqual(response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["hom"], 2)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["af"], 0.0001146)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["het"], 6)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["hom"], 2)
            self.assertEqual(response.context["pop_freqs"]["1000GP"]["AMR"]["af"], 0.0054)
            self.assertEqual(response.context["clinvar"][0]["clinical_significance"], "pathogenic")
            self.assertEqual(response.context["knowngeneaa"][0]["alignment"], "XXX")
            self.assertEqual(response.context["gene"]["hpo_terms"][0][0], "HP:0000001")
            self.assertEqual(response.context["gene"]["hpo_terms"][0][1], "All")
            self.assertEqual(response.context["gene"]["hpo_inheritance"][0][0], "HP:0000007")
            self.assertEqual(response.context["gene"]["hpo_inheritance"][0][1], "AR")
            self.assertEqual(response.context["gene"]["omim"][55555][0], "Disease1")
            self.assertEqual(
                response.context["gene"]["omim"][55555][1][0], "Alternative Description Disease1"
            )
            self.assertEqual(response.context["gene"]["symbol"], "AAA")
            self.assertEqual(response.context["effect_details"][0]["transcript_id"], "ENST0001")
            self.assertEqual(response.context["effect_details"][1]["transcript_id"], "ENST0002")


def fixture_setup_bgjob(user):
    """Setup for background job database (no associated file is generated!)"""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a961", user=user, job_type="type"
    )
    return project.exportfilebgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3200",
        bg_job=job,
        case=case,
        query_args=DEFAULT_RESUBMIT_SETTING,
        file_type="xlsx",
    )


class TestExportFileJobDetailView(TestViewBase):
    """Test export file job detail view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_render(self):
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)


class TestExportFileJobResubmitView(TestViewBase):
    """Test export file job resubmit view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            existing_job = ExportFileBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:export-job-resubmit",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                ),
                {"file_type": "xlsx"},
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 2)
            created_job = ExportFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )

    def test_render_detail_view(self):
        """Test if rendering works."""
        with self.login(self.user):
            existing_job = ExportFileBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportFileJobDownloadView(TestViewBase):
    """Test export file job download view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 404)


def fixture_setup_bgjob_result(user):
    job = fixture_setup_bgjob(user)

    ExportFileJobResult.objects.create(job=job, expiry_time=timezone.now(), payload=b"Testcontent")


class TestExportFileJobDownloadViewResult(TestViewBase):
    """Test export file download view"""

    setup_case_in_db = fixture_setup_bgjob_result

    def test_download(self):
        """Test file download"""
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"Testcontent")


def fixture_setup_projectcases_bgjob(user):
    """Setup for background job database (no associated file is generated!)"""
    project = Project.objects.create(**PROJECT_DICT)
    project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e4",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e5",
        name="B",
        index="B",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "B",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a961", user=user, job_type="type"
    )
    return project.exportprojectcasesfilebgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3200",
        bg_job=job,
        query_args=DEFAULT_JOINT_RESUBMIT_SETTING,
        file_type="xlsx",
    )


def fixture_setup_projectcases_bgjob_result(user):
    job = fixture_setup_projectcases_bgjob(user)

    ExportProjectCasesFileBgJobResult.objects.create(
        job=job, expiry_time=timezone.now(), payload=b"Testcontent"
    )


class TestExportProjectCasesFileJobResubmitView(TestViewBase):
    """Test ExportProjectCasesFileJobResubmitView.
    """

    setup_case_in_db = fixture_setup_projectcases_bgjob

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.user):
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
            existing_job = ExportProjectCasesFileBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-export-job-resubmit",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                ),
                {"file_type": "xlsx"},
            )
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 2)
            created_job = ExportProjectCasesFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )

    def test_render_detail_view(self):
        """Test if rendering works."""
        with self.login(self.user):
            existing_job = ExportProjectCasesFileBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportProjectCasesFileJobDownloadView(TestViewBase):
    """Test ExportProjectCasesFileJobDownloadView.
    """

    setup_case_in_db = fixture_setup_projectcases_bgjob

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.user):
            created_job = ExportProjectCasesFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-download",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 404)


class TestProjectStatsJobCreateView(TestViewBase):
    """Test ProjectStatsJobCreateView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_project_stat_job_creation(self):
        with self.login(self.user):
            project = Project.objects.last()
            response = self.client.post(
                reverse("variants:project-stats-job-create", kwargs={"project": project.sodar_uuid})
            )
            created_job = ComputeProjectVariantsStatsBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-stats-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestProjectStatsJobDetailView(TestViewBase):
    """Test ProjectStatsJobDetailView.
    """

    setup_case_in_db = fixture_setup_projectcases

    def test_render(self):
        with self.login(self.user):
            project = Project.objects.last()
            self.client.post(
                reverse("variants:project-stats-job-create", kwargs={"project": project.sodar_uuid})
            )
            created_job = ComputeProjectVariantsStatsBgJob.objects.last()
            response = self.client.get(
                reverse(
                    "variants:project-stats-job-detail",
                    kwargs={"project": project.sodar_uuid, "job": created_job.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context["object"].bg_job.name,
                "Recreate variant statistic for whole project",
            )


SMALLVARIANT_FLAGS_FORM_DATA = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 100,
    "reference": "A",
    "alternative": "G",
    "flag_bookmarked": True,
    "flag_candidate": False,
    "flag_final_causative": False,
    "flag_for_validation": False,
    "flag_visual": "empty",
    "flag_validation": "empty",
    "flag_phenotype_match": "empty",
    "flag_summary": "empty",
}


class TestSmallVariantFlagsApiView(TestViewBase):
    """Test SmallVariantFlagsApiView.
    """

    setup_case_in_db = fixture_setup_case

    def test_get_json_response_non_existing(self):
        with self.login(self.user):
            case = Case.objects.last()
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            response = self.client.get(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    "release": "GRCh37",
                    "chromosome": "1",
                    "position": 100,
                    "reference": "A",
                    "alternative": "G",
                },
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            self.assertEqual(response.status_code, 404)

    def test_post_json_response_non_existing(self):
        with self.login(self.user):
            case = Case.objects.last()
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_FLAGS_FORM_DATA,
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 1)
            self.assertEqual(response.status_code, 200)

    def test_get_json_response_existing(self):
        with self.login(self.user):
            case = Case.objects.last()
            # Create variant
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_FLAGS_FORM_DATA,
            )
            # Query variant
            response = self.client.get(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {
                    "release": "GRCh37",
                    "chromosome": "1",
                    "position": 100,
                    "reference": "A",
                    "alternative": "G",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(json.loads(response.content.decode("utf-8"))["flag_bookmarked"])

    def test_post_json_response_existing(self):
        with self.login(self.user):
            case = Case.objects.last()
            # Create variant
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_FLAGS_FORM_DATA,
            )
            # Query variant
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_FLAGS_FORM_DATA,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(json.loads(response.content.decode("utf-8"))["flag_bookmarked"])

    def test_post_remove_flags(self):
        with self.login(self.user):
            case = Case.objects.last()
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            # Create flags
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_FLAGS_FORM_DATA,
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 1)
            # Delete flags
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**SMALLVARIANT_FLAGS_FORM_DATA, "flag_bookmarked": False},
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["message"], "erased")


SMALLVARIANT_COMMENT_FORM_DATA = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 100,
    "reference": "A",
    "alternative": "G",
    "text": "Comment X",
}


class TestSmallVariantCommentApiView(TestViewBase):
    """Test SmallVariantCommentApiView.
    """

    setup_case_in_db = fixture_setup_case

    def test_json_response(self):
        with self.login(self.user):
            case = Case.objects.last()
            self.assertEqual(SmallVariantComment.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:small-variant-comment-api",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                SMALLVARIANT_COMMENT_FORM_DATA,
            )
            self.assertEqual(SmallVariantComment.objects.count(), 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["result"], "OK")


class TestBackgroundJobListView(TestViewBase):
    """Tets BackgroundJobListView.
    """

    setup_case_in_db = fixture_setup_bgjob

    def test_render(self):
        with self.login(self.user):
            case = Case.objects.first()
            response = self.client.get(
                reverse(
                    "variants:job-list",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_resulting_list_length(self):
        with self.login(self.user):
            case = Case.objects.first()
            response = self.client.get(
                reverse(
                    "variants:job-list",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(len(response.context["object_list"]), 1)

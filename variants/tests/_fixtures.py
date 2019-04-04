"""Common fixture code.
"""

import aldjemy.core

from projectroles.models import Project
from variants.models import SmallVariant, SmallVariantSummary
from variants.variant_stats import rebuild_case_variant_stats
from geneinfo.models import Hgnc, RefseqToHgnc

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()

#: Shared data for ``Project`` to use for all test cases.
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


#: Default arguments to the ClinvarForm
CLINVAR_FORM_DEFAULTS = form_data = {
    # Pathogenicity
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": False,
    "clinvar_include_pathogenic": False,
    # Origin
    "clinvar_origin_germline": True,
    "clinvar_origin_somatic": False,
    # Reliability
    "clinvar_status_practice_guideline": True,
    "clinvar_status_expert_panel": True,
    "clinvar_status_multiple_no_conflict": True,
    "clinvar_status_conflict": True,
    "clinvar_status_single": True,
    "clinvar_status_no_criteria": True,
    "clinvar_status_no_assertion": True,
    # Database
    "database_select": "refseq",
    # Genotypes
    "A_gt": "variant",
    "compound_recessive_enabled": False,
    # Limit on number of rows
    "result_rows_limit": 500,
    # Filter selection for form.
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
    # Clinvar/HGMD
    "require_in_clinvar": False,
    "remove_if_in_dbsnp": False,
    "require_in_hgmd_public": False,
    "display_hgmd_public_membership": True,
}


#: Defaults for creating a variant for Case 1.  Only ``case_id`` must be filled in.
SMALL_VARIANT_CASE1_DEFAULTS = {
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

#: Default for creating a small variant summary (in-house DB) summary for Case 1.
SMALL_VARIANT_SUMMARY_CASE1_DEFAULTS = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": 100,
    "reference": "A",
    "alternative": "G",
    "count_hom_ref": 0,
    "count_het": 0,
    "count_hom_alt": 0,
    "count_hemi_ref": 0,
    "count_hemi_alt": 0,
}

#: Default values for Clinvar entries.
CLINVAR_DEFAULTS = {
    "release": "GRCh37",
    "chromosome": "1",
    "position": None,
    "reference": "A",
    "alternative": "G",
    "start": None,
    "stop": None,
    "strand": "+",
    "variation_type": "Variant",
    "variation_id": 12345,
    "rcv": "RCV12345",
    "scv": ["RCV12345"],
    "allele_id": 12345,
    "symbol": "ENSG2",
    "hgvs_c": "some-hgvs-c",
    "hgvs_p": "home-hgvs-p",
    "molecular_consequence": "some-molecular-consequence",
    "clinical_significance": None,
    "clinical_significance_ordered": None,
    "pathogenic": 0,
    "likely_pathogenic": 0,
    "uncertain_significance": 0,
    "likely_benign": 0,
    "benign": 0,
    "review_status": None,
    "review_status_ordered": None,
    "last_evaluated": "2016-06-14",
    "all_submitters": ["Some Submitter"],
    "submitters_ordered": ["Some Submitter"],
    "all_traits": ["Some trait"],
    "all_pmids": [12345],
    "inheritance_modes": "",
    "age_of_onset": "",
    "prevalence": "",
    "disease_mechanism": "",
    "origin": ["germline"],
    "xrefs": ["Some xref"],
    "dates_ordered": ["2016-06-14"],
    "multi": 1,
}


# ---------------------------------------------------------------------------
# Tests for Case 1
# ---------------------------------------------------------------------------

# Case 1 is a singleton with a single variant.  Here, we perform tests for
# the basic queries.


def fixture_setup_case1_simple():
    """Setup test case 1 -- a singleton with one variant only."""
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
    SmallVariant.objects.create(
        case_id=case.pk,
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        var_type="snv",
        genotype={"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        in_clinvar=True,
        # frequencies
        exac_frequency=0.01,
        exac_homozygous=0,
        exac_heterozygous=0,
        exac_hemizygous=0,
        thousand_genomes_frequency=0.01,
        thousand_genomes_homozygous=0,
        thousand_genomes_heterozygous=0,
        thousand_genomes_hemizygous=0,
        gnomad_exomes_frequency=0.01,
        gnomad_exomes_homozygous=0,
        gnomad_exomes_heterozygous=0,
        gnomad_exomes_hemizygous=0,
        gnomad_genomes_frequency=0.01,
        gnomad_genomes_homozygous=0,
        gnomad_genomes_heterozygous=0,
        gnomad_genomes_hemizygous=0,
        # RefSeq
        refseq_gene_id="1234",
        refseq_transcript_id="NR_00001.1",
        refseq_transcript_coding=False,
        refseq_hgvs_c="n.111+2T>C",
        refseq_hgvs_p="p.=",
        refseq_effect=["synonymous_variant"],
        # ENSEMBL
        ensembl_gene_id="ENGS00001",
        ensembl_transcript_id="ENST00001",
        ensembl_transcript_coding=False,
        ensembl_hgvs_c="n.111+2T>C",
        ensembl_hgvs_p="p.=",
        ensembl_effect=["synonymous_variant"],
    )
    SmallVariantSummary.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        count_hom_ref=0,
        count_het=1,
        count_hom_alt=1,
        count_hemi_ref=0,
        count_hemi_alt=0,
    )
    Hgnc.objects.create(hgnc_id="HGNC:1", symbol="AAA")
    RefseqToHgnc.objects.create(entrez_id="1234", hgnc_id="HGNC:1")

    rebuild_case_variant_stats(SQLALCHEMY_ENGINE.connect(), case)

"""Common fixture code."""

import aldjemy.core
import binning
from projectroles.models import Project

from geneinfo.models import Hgnc, RefseqToHgnc
from variants.models import SmallVariant, SmallVariantSummary
from variants.variant_stats import rebuild_case_variant_stats

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
        start=100,
        end=100,
        bin=binning.assign_bin(99, 100),
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
        start=100,
        end=100,
        bin=binning.assign_bin(99, 100),
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

    rebuild_case_variant_stats(aldjemy.core.get_engine(), case)

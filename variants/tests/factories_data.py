"""Data for the Factory Boy factories.

The data is externalized into this module such that more than one ``factories`` module can
access the data.  This is useful as we want to generate, e.g., ExAC data that fits to the
variants of the small variants without duplicating these variants.
"""

import factory

#: Data table with small variant data (currently only for one gene)
SMALL_VARS = {
    # Actual variants with predictions from LAMA1, but fake-rare.
    "LAMA1": {
        "release": "GRCh37",
        "chromosome": "18",
        "position": [6977844, 6985631, 7034508, 7038884],
        "reference": ["A", "C", "T", "G"],
        "alternative": ["G", "T", "G", "GT"],
        "var_type": ["snv", "snv", "snv", "indel"],
        "in_clinvar": [False] * 4,
        "exac_frequency": [0.0001, 0.01, 0.0001, 0.01],
        "exac_homozygous": [0, 1, 0, 2],
        "exac_heterozygous": [0, 100, 1, 100],
        "exac_hemizygous": [0, 0, 0, 0],
        "thousand_genomes_frequency": [0.0001, 0.01, 0.0001, 0.01],
        "thousand_genomes_homozygous": [0, 1, 0, 2],
        "thousand_genomes_heterozygous": [0, 100, 1, 100],
        "thousand_genomes_hemizygous": [0, 0, 0, 0],
        "gnomad_exomes_frequency": [0.0001, 0.01, 0.0001, 0.01],
        "gnomad_exomes_homozygous": [0, 1, 0, 2],
        "gnomad_exomes_heterozygous": [0, 100, 1, 100],
        "gnomad_exomes_hemizygous": [0, 0, 0, 0],
        "gnomad_genomes_frequency": [0.0001, 0.01, 0.0001, 0.01],
        "gnomad_genomes_homozygous": [0, 1, 0, 2],
        "gnomad_genomes_heterozygous": [0, 100, 1, 100],
        "gnomad_genomes_hemizygous": [0, 0, 0, 0],
        "refseq_gene_id": ["284217"] * 4,
        "refseq_transcript_id": ["NM_005559.3"] * 4,
        "refseq_transcript_coding": [True] * 4,
        "refseq_hgvs_c": ["c.6227C>T", "c.5391C>A", "c.2021A>G", "c.1487_1488insA"],
        "refseq_hgvs_p": ["p.I2076T", "p.=", "p.N674T", "p.N496Kfs*15"],
        "refseq_effect": [
            ["missense_variant"],
            ["synonymous_variant"],
            ["missense_variant"],
            ["frameshift_variant"],
        ],
        "ensembl_gene_id": ["ENSG00000101680"] * 4,
        "ensembl_transcript_id": ["ENST00000389658"] * 4,
        "ensembl_transcript_coding": [True] * 4,
        "ensembl_hgvs_c": ["c.6227C>T", "c.5391C>A", "c.2021A>G", "c.1487_1488insA"],
        "ensembl_hgvs_p": ["p.I2076T", "p.=", "p.N674T", "p.N496Kfs*15"],
        "ensembl_effect": [
            ["missense_variant"],
            ["synonymous_variant"],
            ["missense_variant"],
            ["frameshift_variant"],
        ],
    }
}


#: Number of variants to generate records for.
NUM_VARIANTS = len(SMALL_VARS["LAMA1"]["position"])


def small_var_attribute(gene, attribute):
    """Return attribute value for the given gene and attribute"""
    return SMALL_VARS[gene][attribute]


def small_var_iterator(gene, attribute):
    """Return ``factory.Iterator`` for the given gene and attribute."""
    return factory.Iterator(SMALL_VARS[gene][attribute])

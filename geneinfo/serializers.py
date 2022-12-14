import typing

import attrs
from rest_framework import serializers

from clinvar.models import ClinvarPathogenicGenes
from geneinfo.models import ExacConstraints, GnomadConstraints, NcbiGeneInfo, NcbiGeneRif


class GeneInfoSerializer(serializers.Serializer):
    """Serializer that serializes ``Hgnc`` to gene information"""

    hgnc_id = serializers.CharField(max_length=16)
    symbol = serializers.CharField(max_length=16)
    ensembl_gene_id = serializers.CharField(max_length=32)
    entrez_id = serializers.CharField(max_length=16)


@attrs.define
class Gene:
    omim: typing.Dict[str, typing.Any] = None
    omim_genes: typing.List[str] = None
    hpo_inheritance: typing.List[str] = None
    hpo_terms: typing.List[str] = None
    clinvar_pathogenicity: typing.Dict[str, typing.Any] = None
    gnomad_constraints: typing.Dict[str, typing.Any] = None
    exac_constraints: typing.Dict[str, typing.Any] = None
    # HGNC model fields (that have been serialized through model_to_dict)
    hgnc_id: typing.Optional[str] = None
    symbol: typing.Optional[str] = None
    name: typing.Optional[str] = None
    locus_group: typing.Optional[str] = None
    locus_type: typing.Optional[str] = None
    status: typing.Optional[str] = None
    location: typing.Optional[str] = None
    location_sortable: typing.Optional[str] = None
    alias_symbol: typing.Optional[str] = None
    alias_name: typing.Optional[str] = None
    prev_symbol: typing.Optional[str] = None
    prev_name: typing.Optional[str] = None
    gene_family: typing.Optional[str] = None
    gene_family_id: typing.Optional[str] = None
    date_approved_reserved: typing.Optional[str] = None
    date_symbol_changed: typing.Optional[str] = None
    date_name_changed: typing.Optional[str] = None
    date_modified: typing.Optional[str] = None
    entrez_id: typing.Optional[str] = None
    ensembl_gene_id: typing.Optional[str] = None
    vega_id: typing.Optional[str] = None
    ucsc_id: typing.Optional[str] = None
    ucsc_id_novers: typing.Optional[str] = None
    ena: typing.Optional[str] = None
    refseq_accession: typing.Optional[str] = None
    ccds_id: typing.Optional[str] = None
    uniprot_ids: typing.Optional[str] = None
    pubmed_id: typing.Optional[str] = None
    mgd_id: typing.Optional[str] = None
    rgd_id: typing.Optional[str] = None
    lsdb: typing.Optional[str] = None
    cosmic: typing.Optional[str] = None
    omim_id: typing.Optional[str] = None
    mirbase: typing.Optional[str] = None
    homeodb: typing.Optional[str] = None
    snornabase: typing.Optional[str] = None
    bioparadigms_slc: typing.Optional[str] = None
    orphanet: typing.Optional[str] = None
    pseudogene_org: typing.Optional[str] = None
    horde_id: typing.Optional[str] = None
    merops: typing.Optional[str] = None
    imgt: typing.Optional[str] = None
    iuphar: typing.Optional[str] = None
    kznf_gene_catalog: typing.Optional[str] = None
    mamit_trnadb: typing.Optional[str] = None
    cd: typing.Optional[str] = None
    lncrnadb: typing.Optional[str] = None
    enzyme_id: typing.Optional[str] = None
    intermediate_filament_db: typing.Optional[str] = None
    rna_central_ids: typing.Optional[str] = None
    gtrnadb: typing.Optional[str] = None
    lncipedia: typing.Optional[str] = None
    agr: typing.Optional[str] = None
    mane_select: typing.Optional[str] = None
    ncbi_summary: typing.Dict[str, typing.Any] = None
    ncbi_gene_rifs: typing.List[typing.Dict[str, typing.Any]] = None


class ClinvarPathogenicGenesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinvarPathogenicGenes
        fields = (
            "symbol",
            "entrez_id",
            "ensembl_gene_id",
            "pathogenic_count",
            "likely_pathogenic_count",
        )


class GnomadConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GnomadConstraints
        fields = (
            "symbol",
            "ensembl_transcript_id",
            "obs_mis",
            "exp_mis",
            "oe_mis",
            "mu_mis",
            "possible_mis",
            "obs_mis_pphen",
            "exp_mis_pphen",
            "oe_mis_pphen",
            "possible_mis_pphen",
            "obs_syn",
            "exp_syn",
            "oe_syn",
            "mu_syn",
            "possible_syn",
            "obs_lof",
            "mu_lof",
            "possible_lof",
            "exp_lof",
            "pLI",
            "pNull",
            "pRec",
            "oe_lof",
            "oe_syn_lower",
            "oe_syn_upper",
            "oe_mis_lower",
            "oe_mis_upper",
            "oe_lof_lower",
            "oe_lof_upper",
            "constraint_flag",
            "syn_z",
            "mis_z",
            "lof_z",
            "oe_lof_upper_rank",
            "oe_lof_upper_bin",
            "oe_lof_upper_bin_6",
            "n_sites",
            "classic_caf",
            "max_af",
            "no_lofs",
            "obs_het_lof",
            "obs_hom_lof",
            "defined",
            "p",
            "exp_hom_lof",
            "classic_caf_afr",
            "classic_caf_amr",
            "classic_caf_asj",
            "classic_caf_eas",
            "classic_caf_fin",
            "classic_caf_nfe",
            "classic_caf_oth",
            "classic_caf_sas",
            "p_afr",
            "p_amr",
            "p_asj",
            "p_eas",
            "p_fin",
            "p_nfe",
            "p_oth",
            "p_sas",
            "transcript_type",
            "ensembl_gene_id",
            "transcript_level",
            "cds_length",
            "num_coding_exons",
            "gene_type",
            "gene_length",
            "exac_pLI",
            "exac_obs_lof",
            "exac_exp_lof",
            "exac_oe_lof",
            "brain_expression",
            "chromosome",
            "start_position",
            "end_position",
        )


class ExacConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExacConstraints
        fields = (
            "ensembl_transcript_id",
            "symbol",
            "chromosome",
            "n_exons",
            "cds_start",
            "cds_end",
            "bp",
            "mu_syn",
            "mu_mis",
            "mu_lof",
            "n_syn",
            "n_mis",
            "n_lof",
            "exp_syn",
            "exp_mis",
            "exp_lof",
            "syn_z",
            "mis_z",
            "lof_z",
            "pLI",
            "pRec",
            "pNull",
        )


class NcbiGeneInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NcbiGeneInfo
        fields = (
            "entrez_id",
            "summary",
        )


class NcbiGeneRifSerializer(serializers.ModelSerializer):
    class Meta:
        model = NcbiGeneRif
        fields = (
            "entrez_id",
            "rif_text",
            "pubmed_ids",
        )


class GeneSerializer(serializers.Serializer):
    omim = serializers.JSONField()
    omim_genes = serializers.JSONField()
    hpo_inheritance = serializers.JSONField()
    hpo_terms = serializers.JSONField()
    clinvar_pathogenicity = ClinvarPathogenicGenesSerializer()
    gnomad_constraints = GnomadConstraintsSerializer()
    exac_constraints = ExacConstraintsSerializer()
    # HGNC model fields
    hgnc_id = serializers.CharField(max_length=16)
    symbol = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=128)
    locus_group = serializers.CharField(max_length=32, allow_null=True)
    locus_type = serializers.CharField(max_length=32, allow_null=True)
    status = serializers.CharField(max_length=32, allow_null=True)
    location = serializers.CharField(max_length=64, allow_null=True)
    location_sortable = serializers.CharField(max_length=64, allow_null=True)
    alias_symbol = serializers.CharField(max_length=128, allow_null=True)
    alias_name = serializers.CharField(max_length=512, allow_null=True)
    prev_symbol = serializers.CharField(max_length=128, allow_null=True)
    prev_name = serializers.CharField(max_length=1024, allow_null=True)
    gene_family = serializers.CharField(max_length=256, allow_null=True)
    gene_family_id = serializers.CharField(max_length=32, allow_null=True)
    date_approved_reserved = serializers.CharField(max_length=32, allow_null=True)
    date_symbol_changed = serializers.CharField(max_length=32, allow_null=True)
    date_name_changed = serializers.CharField(max_length=32, allow_null=True)
    date_modified = serializers.CharField(max_length=16, allow_null=True)
    entrez_id = serializers.CharField(max_length=16, allow_null=True)
    ensembl_gene_id = serializers.CharField(max_length=32, allow_null=True)
    vega_id = serializers.CharField(max_length=32, allow_null=True)
    ucsc_id = serializers.CharField(max_length=16, allow_null=True)
    ucsc_id_novers = serializers.CharField(max_length=16, allow_null=True)
    ena = serializers.CharField(max_length=64, allow_null=True)
    refseq_accession = serializers.CharField(max_length=128, allow_null=True)
    ccds_id = serializers.CharField(max_length=256, allow_null=True)
    uniprot_ids = serializers.CharField(max_length=256, allow_null=True)
    pubmed_id = serializers.CharField(max_length=64, allow_null=True)
    mgd_id = serializers.CharField(max_length=256, allow_null=True)
    rgd_id = serializers.CharField(max_length=32, allow_null=True)
    lsdb = serializers.CharField(max_length=1024, allow_null=True)
    cosmic = serializers.CharField(max_length=32, allow_null=True)
    omim_id = serializers.CharField(max_length=32, allow_null=True)
    mirbase = serializers.CharField(max_length=16, allow_null=True)
    homeodb = serializers.CharField(max_length=16, allow_null=True)
    snornabase = serializers.CharField(max_length=16, allow_null=True)
    bioparadigms_slc = serializers.CharField(max_length=32, allow_null=True)
    orphanet = serializers.CharField(max_length=16, allow_null=True)
    pseudogene_org = serializers.CharField(max_length=32, allow_null=True)
    horde_id = serializers.CharField(max_length=16, allow_null=True)
    merops = serializers.CharField(max_length=16, allow_null=True)
    imgt = serializers.CharField(max_length=32, allow_null=True)
    iuphar = serializers.CharField(max_length=32, allow_null=True)
    kznf_gene_catalog = serializers.CharField(max_length=32, allow_null=True)
    mamit_trnadb = serializers.CharField(max_length=16, allow_null=True)
    cd = serializers.CharField(max_length=16, allow_null=True)
    lncrnadb = serializers.CharField(max_length=32, allow_null=True)
    enzyme_id = serializers.CharField(max_length=64, allow_null=True)
    intermediate_filament_db = serializers.CharField(max_length=32, allow_null=True)
    rna_central_ids = serializers.CharField(max_length=32, allow_null=True)
    gtrnadb = serializers.CharField(max_length=32, allow_null=True)
    lncipedia = serializers.CharField(max_length=32, allow_null=True)
    agr = serializers.CharField(max_length=32, allow_null=True)
    mane_select = serializers.CharField(max_length=64, allow_null=True)
    ncbi_summary = NcbiGeneInfoSerializer()
    ncbi_gene_rifs = NcbiGeneRifSerializer(many=True)

"""Query schema handling for ``svs`` module."""

from enum import Enum, unique
import typing

import attrs

from variants.query_presets import Database, GenotypeChoice
from variants.query_schemas import GenomicRegionV1, RecessiveModeV1


@unique
class Pathogenicity(Enum):
    """ClinVar pathogenicity"""

    PATHOGENIC = "pathogenic"
    LIKELY_PATHOGENIC = "likely-pathogenic"
    UNCERTAIN = "uncertain"
    LIKELY_BENIGN = "likely-benign"
    BENIGN = "benign"


@unique
class SvType(Enum):
    """SV types."""

    #: Deletion.
    DEL = "DEL"
    #: Duplication.
    DUP = "DUP"
    #: Inversion.
    INV = "INV"
    #: Insertion.
    INS = "INS"
    #: Breakend.
    BND = "BND"
    #: Copy number variation.
    CNV = "CNV"


@unique
class SvSubType(Enum):
    #: Deletion
    DEL = "DEL"
    #: Mobile element deletion.
    DEL_ME = "DEL:ME"
    #: Mobile element deletion (SVA).
    DEL_ME_SVA = "DEL:ME:SVA"
    #: Mobile element deletion (L1).
    DEL_ME_L1 = "DEL:ME:L1"
    #: Mobile element deletion (ALU).
    DEL_ME_ALU = "DEL:ME:ALU"
    #: Duplication.
    DUP = "DUP"
    #: Tandem duplication.
    DUP_TANDEM = "DUP:TANDEM"
    #: Inversion.
    INV = "INV"
    #: Insertion.
    INS = "INS"
    #: Mobile element insertion.
    INS_ME = "INS:ME"
    #: Mobile element insertion (SVA).
    INS_ME_SVA = "INS:ME:SVA"
    #: Mobile element insertion (L1).
    INS_ME_L1 = "INS:ME:L1"
    #: Mobile element insertion (ALU).
    INS_ME_ALU = "INS:ME:ALU"
    #: Breakend
    BND = "BND"
    #: CNV
    CNV = "CNV"


@unique
class TranscriptEffect(Enum):
    #: Affects the full transcript.
    TRANSCRIPT_VARIANT = "transcript_variant"
    #: An exon is affected by the SV.
    EXON_VARIANT = "exon_variant"
    #: The splice region is affected by the SV.
    SPLICE_REGION_VARIANT = "splice_region_variant"
    #: The intron is affected by the SV.
    INTRON_VARIANT = "intron_variant"
    #: The upstream region of the transcript is affected.
    UPSTREAM_VARIANT = "upstream_variant"
    #: The downstream region of the transcript is affected.
    DOWNSTREAM_VARIANT = "downstream_variant"
    #: Only intergenic regions is affected,
    INTERGENIC_VARIANT = "intergenic_variant"


@unique
class VariantEffect(Enum):
    CODING_SEQUENCE_VARIANT = "coding_sequence_variant"
    CODING_TRANSCRIPT_INTRON_VARIANT = "coding_transcript_intron_variant"
    CODING_TRANSCRIPT_VARIANT = "coding_transcript_variant"
    COPY_NUMBER_CHANGE = "copy_number_change"
    DIRECT_TANDEM_DUPLICATION = "direct_tandem_duplication"
    DOWNSTREAM_GENE_VARIANT = "downstream_gene_variant"
    EXON_LOSS_VARIANT = "exon_loss_variant"
    FEATURE_TRUNCATION = "feature_truncation"
    FIVE_PRIME_UTR_EXON_VARIANT = "5_prime_UTR_exon_variant"
    FIVE_PRIME_UTR_INTRON_VARIANT = "5_prime_UTR_intron_variant"
    FIVE_PRIME_UTR_TRUNCATION = "5_prime_UTR_truncation"
    FRAMESHIFT_TRUNCATION = "frameshift_truncation"
    INSERTION = "insertion"
    INTRON_VARIANT = "intron_variant"
    INVERSION = "inversion"
    MOBILE_ELEMENT_DELETION = "mobile_element_deletion"
    MOBILE_ELEMENT_INSERTION = "mobile_element_insertion"
    NON_CODING_TRANSCRIPT_EXON_VARIANT = "non_coding_transcript_exon_variant"
    NON_CODING_TRANSCRIPT_INTRON_VARIANT = "non_coding_transcript_intron_variant"
    NON_CODING_TRANSCRIPT_VARIANT = "non_coding_transcript_variant"
    SEQUENCE_VARIANT = "sequence_variant"
    START_LOST = "start_lost"
    STOP_LOST = "stop_lost"
    STRUCTURAL_VARIANT = "structural_variant"
    THREE_PRIME_UTR_EXON_VARIANT = "3_prime_UTR_exon_variant"
    THREE_PRIME_UTR_INTRON_VARIANT = "3_prime_UTR_intron_variant"
    THREE_PRIME_UTR_TRUNCATION = "3_prime_UTR_truncation"
    TRANSCRIPT_ABLATION = "transcript_ablation"
    TRANSCRIPT_AMPLIFICATION = "transcript_amplification"
    TRANSLOCATION = "translocation"
    UPSTREAM_GENE_VARIANT = "upstream_variant"


@unique
class EnsemblRegulatorFeature(Enum):
    """Feature from ENSEMBL regulatory build."""

    #: Any fature.
    ANY_FEATURE = "any_feature"
    #: CTCF binding site.
    CTCF_BINDING_SITE = "CTCF_binding_site"
    #: Enhancer.
    ENHANCER = "enhancer"
    #: Open chromatin region.
    OPEN_CHROMATIN_REGION = "open_chromatin_region"
    #: Promoter region.
    PROMOTER = "promoter"
    #: Promoter flanking region.
    PROMOTER_FLANKING_REGION = "promoter_flanking_region"
    #: Transcription factor binding site.
    TF_BINDING_SITE = "TF_binding_site"


@unique
class VistaValidation(Enum):
    """Validation status from VISTA."""

    #: Any validation result.
    ANY = "any_validation"
    #: Positive validation result.
    POSITIVE = "positive"
    #: Negative validation result.
    NEGATIVE = "negative"


@attrs.define(frozen=True)
class RegulatoryCustomConfig:
    """Configuration of custom regulatory maps."""

    #: The selected cell types.
    cell_types: typing.List[str] = attrs.field(factory=list)
    #: The selected element type.
    element_types: typing.List[str] = attrs.field(factory=list)
    #: Alternatively, overlapping with interaction in cell type (includes all elements).
    overlaps_interaction: bool = False


@attrs.frozen
class GenotypeCriteria:
    """Define rule to apply to a given sub set of structural variants for showing a genotype.

    For example, select specify that deletions smaller than 1'000bp must fulfill the following criteria to show
    the given genotype.

    ::

        GenotypeCriteria(
            # To evaluate as heterozygous, ...
            genotype=GenotypeChoice.HET,
            # ... deletions between 0 and 1'000 bp must ...
            select_sv_sub_type=['DEL'],
            select_sv_min_size=None,
            select_sv_max_size=1_000,
            # ... irrespective of FORMAT/GT from the caller ...
            gt_one_of=None,
            # ... have at least one variant split read, one variant read pair, and the sum of both must be 4 or higher.
            min_sr_var=1,
            min_pr_var=1,
            min_srpr_var=4,  # at least 4 split reads or read pairs
        )
    """

    #: The genotype to evaluate to
    genotype: GenotypeChoice

    #: SV (sub) type that this applies to
    select_sv_sub_type: typing.List[str]
    #: Minimal size of SV (ignored for BND and INS)
    select_sv_min_size: typing.Optional[int] = None
    #: Maximal size of SV (ignored for BND and INS)
    select_sv_max_size: typing.Optional[int] = None

    #: The FORMAT/GT field should be one of, unless ``None``.
    gt_one_of: typing.Optional[typing.List[str]] = None

    #: Maximal number of ends/breakpoints within segmental duplications.
    max_brk_segdup: typing.Optional[int] = None
    #: Maximal number of ends/breakpoints within repeat-masked sequence.
    max_brk_repeat: typing.Optional[int] = None
    #: Maximal number of ends/breakpoints within segmental duplications or repeat-masked sequence.
    max_brk_segduprepeat: typing.Optional[int] = None

    #: Minimal genotype quality as returned by caller.
    min_gq: typing.Optional[float] = None
    #: Minimal number of total paired-end reads covering the SV.
    min_pr_cov: typing.Optional[int] = None
    #: Maximal number of total paired-end reads covering the SV.
    max_pr_cov: typing.Optional[int] = None
    #: Minimal number of reference paired-end reads covering the SV.
    min_pr_ref: typing.Optional[int] = None
    #: Maximal number of reference paired-end reads covering the SV.
    max_pr_ref: typing.Optional[int] = None
    #: Minimal number of variant paired-end reads covering the SV.
    min_pr_var: typing.Optional[int] = None
    #: Maximal number of variant paired-end reads covering the SV.
    max_pr_var: typing.Optional[int] = None
    #: Minimal number of total split reads covering the SV.
    min_sr_cov: typing.Optional[int] = None
    #: Maximal number of total split reads covering the SV.
    max_sr_cov: typing.Optional[int] = None
    #: Minimal number of reference split reads covering the SV.
    min_sr_ref: typing.Optional[int] = None
    #: Maximal number of reference split reads covering the SV.
    max_sr_ref: typing.Optional[int] = None
    #: Minimal number of variant split reads covering the SV.
    min_sr_var: typing.Optional[int] = None
    #: Maximal number of variant split reads covering the SV.
    max_sr_var: typing.Optional[int] = None
    #: Minimal sum of total paired-end/split read coverage.
    min_srpr_cov: typing.Optional[int] = None
    #: Maximal sum of total paired-end/split read coverage.
    max_srpr_cov: typing.Optional[int] = None
    #: Minimal sum of reference paired-end/split read coverage.
    min_srpr_ref: typing.Optional[int] = None
    #: Maximal sum of reference paired-end/split read coverage.
    max_srpr_ref: typing.Optional[int] = None
    #: Minimal sum of variant paired-end/split read coverage.
    min_srpr_var: typing.Optional[int] = None
    #: Maximal sum of variant paired-end/split read coverage.
    max_srpr_var: typing.Optional[int] = None
    #: Minimal split read allelic balance.
    min_sr_ab: typing.Optional[float] = None
    #: Maximal split read allelic balance.
    max_sr_ab: typing.Optional[float] = None
    #: Minimal paired read allelic balance.
    min_pr_ab: typing.Optional[float] = None
    #: Maximal paired read allelic balance.
    max_pr_ab: typing.Optional[float] = None
    #: Minimal split read or paired read allelic balance.
    min_srpr_ab: typing.Optional[float] = None
    #: Maximal split read or paired read allelic balance.
    max_srpr_ab: typing.Optional[float] = None
    #: Minimal coverage deviation.
    min_rd_dev: typing.Optional[float] = None
    #: Maximal coverage deviation.
    max_rd_dev: typing.Optional[float] = None
    #: Minimal average mapping quality.
    min_amq: typing.Optional[float] = None
    #: Maximal average mapping quality.
    max_amq: typing.Optional[float] = None

    #: Whether missing genotype call leads to filter out variant
    missing_gt_ok: typing.Optional[bool] = True
    #: Whether missing genotype quality information leads filter out variant
    missing_gq_ok: typing.Optional[bool] = True
    #: Whether missing paired-read information leads to filter out variant
    missing_pr_ok: typing.Optional[bool] = True
    #: Whether missing split read information leads to filter out variant
    missing_sr_ok: typing.Optional[bool] = True
    #: Whether missing split read or paired read information leads to filter out variant
    missing_srpr_ok: typing.Optional[bool] = True
    #: Whether missing read depth information leads to filter out variant
    missing_rd_dev_ok: typing.Optional[bool] = True
    #: Whether missing mapping quality information leads to filter out variant
    missing_amq_ok: typing.Optional[bool] = True

    #: An optional comment.
    comment: typing.Optional[str] = None


@attrs.define(frozen=True)
class CaseQuery:
    """Data structure to hold query settings for ``svs`` queries."""

    #: The transcript database to use.
    database: Database = Database.REFSEQ

    #: Whether to enable SVDB overlap queries with DGV.
    svdb_dgv_enabled: bool = False
    #: The minimal reciprocal overlap for querying DGV.
    svdb_dgv_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying DGV.
    svdb_dgv_max_count: typing.Optional[int] = None
    #: Whether to enable SVDB overlap queries with DGV gold standard.
    svdb_dgv_gs_enabled: bool = False
    #: The minimal reciprocal overlap for querying DGV gold standard.
    svdb_dgv_gs_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying DGV gold standard.
    svdb_dgv_gs_max_count: typing.Optional[int] = None
    #: Whether to enable SVDB overlap queries with gnomAD.
    svdb_gnomad_genomes_enabled: bool = True
    #: The minimal reciprocal overlap for querying gnomAD.
    svdb_gnomad_genomes_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying gnomAD.
    svdb_gnomad_genomes_max_count: typing.Optional[int] = 20
    #: Whether to enable SVDB overlap queries with ExAC.
    svdb_gnomad_exomes_enabled: bool = True
    #: The minimal reciprocal overlap for querying ExAC.
    svdb_gnomad_exomes_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying ExAC.
    svdb_gnomad_exomes_max_count: typing.Optional[int] = 20
    #: Whether to enable SVDB overlap queries with dbVar.
    svdb_dbvar_enabled: bool = True
    #: The minimal reciprocal overlap for querying dbVar.
    svdb_dbvar_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying dbVar.
    svdb_dbvar_max_count: typing.Optional[int] = 40
    #: Whether to enable SVDB overlap queries with Thousand Genomes Project.
    svdb_g1k_enabled: bool = True
    #: The minimal reciprocal overlap for querying Thousand Genomes Project.
    svdb_g1k_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of carriers for querying Thousand Genomes Project.
    svdb_g1k_max_count: typing.Optional[int] = 10
    #: Whether to enable SVDB overlap queries with in-house DB.
    svdb_inhouse_enabled: bool = True
    #: The minimal reciprocal overlap for querying in-house DB.
    svdb_inhouse_min_overlap: typing.Optional[float] = 0.75
    #: The maximal number of alleles for querying in-house DB.
    svdb_inhouse_max_count: typing.Optional[int] = 10

    #: Minimal reciprocal overlap when overlapping with ClinVar SVs
    clinvar_sv_min_overlap: typing.Optional[float] = 0.75
    #: Minimal pathogenicity when overlapping with ClinVar SVs.
    clinvar_sv_min_pathogenicity: typing.Optional[Pathogenicity] = Pathogenicity.LIKELY_PATHOGENIC

    #: The minimal SV size to consider.
    sv_size_min: typing.Optional[int] = 500
    #: The maximal SV size to consider.
    sv_size_max: typing.Optional[int] = None

    #: The SV types to consider.
    sv_types: typing.List[SvType] = attrs.field(factory=list)
    #: The SV subtypes to consider.
    sv_sub_types: typing.List[SvSubType] = attrs.field(factory=list)
    #: The effect on the transcript to consider.
    tx_effects: typing.List[TranscriptEffect] = attrs.field(factory=list)

    #: List of genes to require.
    gene_allowlist: typing.Optional[typing.List[str]] = None
    #: Genomic region to limit consideration to.
    genomic_region: typing.Optional[typing.List[GenomicRegionV1]] = None

    #: Regulatory region padding to use.
    regulatory_overlap: int = 100
    #: Regulatory features to select from ENSEMBL.
    regulatory_ensembl_features: typing.Optional[typing.List[EnsemblRegulatorFeature]] = None
    #: VISTA enhancer validation results.
    regulatory_vista_validation: typing.Optional[VistaValidation] = None

    #: Custom regulatory maps configuration.
    regulatory_custom_configs: typing.List[RegulatoryCustomConfig] = attrs.field(factory=list)

    #: Name of the TAD set to use for annotation, if any.
    tad_set: typing.Optional[str] = None

    #: Genotype choices
    genotype: typing.Dict[str, typing.Optional[GenotypeChoice]] = attrs.field(factory=dict)
    #: Criteria for filtering CNVs.
    genotype_criteria: typing.List[GenotypeCriteria] = attrs.field(factory=list)

    #: The mode for recessive inheritance.
    recessive_mode: typing.Optional[RecessiveModeV1] = None
    #: The index to use for recessive inheritance.
    recessive_index: typing.Optional[str] = None

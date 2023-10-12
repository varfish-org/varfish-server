from django_pydantic_field import SchemaField
import pydantic

from cases_qc.models import CaseQcBaseModel, CaseQcForSampleBaseModel


class BcftoolsStatsSnRecord(pydantic.BaseModel):
    """A Record from the ``SN`` lines in ``bcftools stats`` output."""

    #: Name of the summarized metric
    key: str
    #: Value of the summarized metric
    value: int | float | str | None

    class Config:
        smart_union = True  # prevent "int | float" from float to int conversion


class BcftoolsStatsTstvRecord(pydantic.BaseModel):
    """A Record from the ``TSTV`` lines in ``bcftools stats`` output."""

    #: ts
    ts: int
    #: tv
    tv: int
    #: ts/tv
    tstv: float
    #: ts (1st ALT)
    ts_1st_alt: int
    #: tv (1st ALT)
    tv_1st_alt: int
    #: ts/tv (1st ALT)
    tstv_1st_alt: float


class BcftoolsStatsSisRecord(pydantic.BaseModel):
    """A Record from the ``SiS`` (singleton stats) lines in ``bcftools stats`` output."""

    #: allele count
    total: int
    #: number of SNPs
    snps: int
    #: number of transitions (1st ALT)
    ts: int
    #: number of transversions (1st ALT)
    tv: int
    #: number of indels
    indels: int
    #: repeat-consistent
    repeat_consistent: int
    #: repeat-inconsistent
    repeat_inconsistent: int


class BcftoolsStatsAfRecord(pydantic.BaseModel):
    """A Record from the ``AF`` (non-reference allele frequency) lines in ``bcftools stats``
    output."""

    #: allele frequency
    af: float
    #: number of SNPs
    snps: int
    #: number of transitions (1st ALT)
    ts: int
    #: number of transversions (1st ALT)
    tv: int
    #: number of indels
    indels: int
    #: repeat-consistent
    repeat_consistent: int
    #: repeat-inconsistent
    repeat_inconsistent: int
    #: not applicable
    na: int


class BcftoolsStatsQualRecord(pydantic.BaseModel):
    """A Record from the ``QUAL`` (quality) lines in ``bcftools stats`` output."""

    #: quality
    qual: float | None
    #: number of SNPs
    snps: int
    #: number of transitions (1st ALT)
    ts: int
    #: number of transversions (1st ALT)
    tv: int
    #: number of indels
    indels: int


class BcftoolsStatsIddRecord(pydantic.BaseModel):
    """A Record from the ``IDD`` (indel distribution) lines in ``bcftools stats`` output."""

    #: length (deletions negative)
    length: int
    #: number of sites
    sites: int
    #: number of genotypes
    gts: int
    #: mean VAF
    mean_vaf: float | None


class BcftoolsStatsStRecord(pydantic.BaseModel):
    """A Record from the ``ST`` (substitution types) lines in ``bcftools stats`` output."""

    #: type of the substitution
    type: str
    #: count
    count: int


class BcftoolsStatsDpRecord(pydantic.BaseModel):
    """A Record from the ``DP`` (AF) lines in ``bcftools stats`` output."""

    #: bin number
    bin: int
    #: number of genotypes
    gts: int
    #: fraction of genotypes
    gts_frac: float
    #: number of sites
    sites: int
    #: fraction of sites
    sites_frac: float


class BcftoolsStatsMetrics(CaseQcBaseModel):
    """Statistics from ``bcftools stats`` output."""

    #: summary (``SN`` records)
    sn = SchemaField(schema=list[BcftoolsStatsSnRecord], blank=False, null=False)
    #: transition / transversion ratios (``TSTV`` records)
    tstv = SchemaField(schema=list[BcftoolsStatsTstvRecord], blank=False, null=False)
    #: singleton stats (``SiS`` records)
    sis = SchemaField(schema=list[BcftoolsStatsSisRecord], blank=False, null=False)
    #: non-reference allele frequency (``AF`` records)
    af = SchemaField(schema=list[BcftoolsStatsAfRecord], blank=False, null=False)
    #: quality (``QUAL`` records)
    qual = SchemaField(schema=list[BcftoolsStatsQualRecord], blank=False, null=False)
    #: indel distribution
    idd = SchemaField(schema=list[BcftoolsStatsIddRecord], blank=False, null=False)
    #: substitution types
    st = SchemaField(schema=list[BcftoolsStatsStRecord], blank=False, null=False)
    #: depth distribution
    dp = SchemaField(schema=list[BcftoolsStatsDpRecord], blank=False, null=False)


class SamtoolsStatsChkRecord(pydantic.BaseModel):
    """A Record from the ``CHK`` lines in ``samtools stats`` output."""

    #: read names CRC32
    read_names_crc32: str
    #: sequences CRC32
    sequences_crc32: str
    #: qualities CRC32
    qualities_crc32: str


class SamtoolsStatsSnRecord(pydantic.BaseModel):
    """A Record from the ``SN`` lines in ``samtools stats`` output."""

    #: name of the summarized metric
    key: str
    #: value of the summarized metric
    value: int


class SamtoolsStatsFqRecord(pydantic.BaseModel):
    """A Record from the ``FFQ`` and ``LFQ`` lines in ``samtools stats`` output."""

    #: cycle
    cycle: int
    #: counts
    counts: list[int]


class SamtoolsStatsGcRecord(pydantic.BaseModel):
    """A Record from the ``GCF`` and ``GCL`` lines in ``samtools stats`` output."""

    #: GC content
    gc_content: float
    #: count
    count: int


class SamtoolsIdxstatsRecord(pydantic.BaseModel):
    """A record for the lines in ``samtools idxstats`` output."""

    #: contig name
    contig_name: str
    #: contig length
    contig_len: int
    #: mapped fragments
    mapped: int
    #: unmapped fragments
    unmapped: int


class SamtoolsIdxstatsMetrics(CaseQcForSampleBaseModel):
    """Metrics for ``samtools idxstats`` output."""

    #: Metrics as JSON following the ``SamtoolsIdxstatsRecord`` schema
    records = SchemaField(schema=list[SamtoolsIdxstatsRecord], blank=False, null=False)


class SamtoolsFlagstatRecord(pydantic.BaseModel):
    """A record for the ``flagstat`` lines in ``samtools stats`` output."""

    #: total (QC-passed reads + QC-failed reads)
    total: int = 0
    #: primary
    primary: int = 0
    #: secondary
    secondary: int = 0
    #: supplementary
    supplementary: int = 0
    #: duplicates
    duplicates: int = 0
    #: primary duplicates
    duplicates_primary: int = 0
    #: mapped
    mapped: int = 0
    #: primary mapped
    mapped_primary: int = 0
    #: paired in sequencing
    paired: int = 0
    #: read1
    fragment_first: int = 0
    #: read2
    fragment_last: int = 0
    #: properly paired (98.51% : N/A)
    properly_paired: int = 0
    #: with itself and mate mapped
    with_itself_and_mate_mapped: int = 0
    #: singletons (0.10% : N/A)
    singletons: int = 0
    #: with mate mapped to a different chr
    with_mate_mapped_to_different_chr: int = 0
    #: with mate mapped to a different chr (mapQ>=5)
    with_mate_mapped_to_different_chr_mapq5: int = 0


class SamtoolsFlagstatMetrics(CaseQcForSampleBaseModel):
    """Metrics for ``samtools flagstat`` output."""

    #: statistics for QC pass records
    qc_pass = SchemaField(schema=SamtoolsFlagstatRecord, blank=False, null=False)
    #: statistics for QC fail records
    qc_fail = SchemaField(schema=SamtoolsFlagstatRecord, blank=False, null=False)


class SamtoolsStatsIcRecord(pydantic.BaseModel):
    """A record for the ``IC`` lines in ``samtools stats`` output."""

    #: cycle
    cycle: int
    #: number of insertions on forward
    ins_fwd: int
    #: number of insertions on reverse
    dels_fwd: int
    #: number of deletions on forward
    ins_rev: int
    #: number of deletions on reverse
    dels_rev: int


class SamtoolsStatsHistoRecord(pydantic.BaseModel):
    """A record for a value/count pair.

    Used for ``MAPQ``, ``ID``, ``COV``
    """

    #: value
    value: int
    #: count
    count: int


class SamtoolsStatsBasePercentagesRecord(pydantic.BaseModel):
    """A Record from the ``GCC``, ``GCT``, ``FBC``, and ``LBC`` lines in ``samtools stats``
    output.
    """

    #: cycle
    cycle: int
    #: fraction of A, C, G, T
    percentages: list[float]


class SamtoolsStatsSupplementaryMetrics(CaseQcForSampleBaseModel):
    """Metrics for some "supplementary" metrics from ``samtools stats`` records.

    This is split between two models so the supplementary data can loaded only when
    necessary.  This split was done with visualization in VarFish in mind.
    """

    #: first fragment GC content for each cycle
    gcf = SchemaField(schema=list[SamtoolsStatsGcRecord], blank=False, null=False)
    #: last fragment GC content for each cycle
    gcl = SchemaField(schema=list[SamtoolsStatsGcRecord], blank=False, null=False)
    #: ACGT content for each cycle
    gcc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord], blank=False, null=False)
    #: ACGT content for each cycle (read-oriented)
    gct = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord], blank=False, null=False)
    #: read lengths
    rl = SchemaField(schema=list[SamtoolsStatsHistoRecord], blank=False, null=False)
    #: mapping qualities
    mapq = SchemaField(schema=list[SamtoolsStatsHistoRecord], blank=False, null=False)
    #: indel distribution (per cycle)
    ic = SchemaField(schema=list[SamtoolsStatsIcRecord], blank=False, null=False)


class SamtoolsStatsGcdRecord(pydantic.BaseModel):
    """A record for the ``GCD`` lines in ``samtools stats`` output."""

    #: GC content
    gc_content: float
    #: unique sequence percentiles
    unique_seq_percentiles: float
    #: 10th depth percentile
    dp_percentile_10: float
    #: 25th depth percentile
    dp_percentile_25: float
    #: 50th depth percentile
    dp_percentile_50: float
    #: 75th depth percentile
    dp_percentile_75: float
    #: 90th depth percentile
    dp_percentile_90: float


class SamtoolsStatsIdRecord(pydantic.BaseModel):
    """A record for the ``ID`` lines in ``samtools stats`` output."""

    #: length
    length: int
    #: number of insertions
    ins: int
    #: number of deletions
    dels: int


class SamtoolsStatsIsRecord(pydantic.BaseModel):
    """Records for the ``IS`` records."""

    #: insert size
    insert_size: int
    #: pairs total
    pairs_total: int
    #: inward oriented pairs
    pairs_inward: int
    #: outward oriented pairs
    pairs_outward: int
    #: other pairs
    pairs_other: int


class SamtoolsStatsMainMetrics(CaseQcForSampleBaseModel):
    """Metrics for the most relevant metrics from ``samtools stats`` records.

    This is split between two models so the supplementary data can loaded only when
    necessary.  This split was done with visualization in VarFish in mind.
    """

    #: summary information
    sn = SchemaField(schema=list[SamtoolsStatsSnRecord], blank=False, null=False)
    #: checksum information
    chk = SchemaField(schema=list[SamtoolsStatsChkRecord], blank=False, null=False)
    #: insert size statistics
    isize = SchemaField(schema=list[SamtoolsStatsIsRecord], blank=False, null=False)
    #: coverage distribution
    cov = SchemaField(schema=list[SamtoolsStatsHistoRecord], blank=False, null=False)
    #: GC-depth
    gcd = SchemaField(schema=list[SamtoolsStatsGcdRecord], blank=False, null=False)
    #: first fragment read lengths
    frl = SchemaField(schema=list[SamtoolsStatsHistoRecord], blank=False, null=False)
    #: last fragment read lengths
    lrl = SchemaField(schema=list[SamtoolsStatsHistoRecord], blank=False, null=False)
    #: indel distribution
    idd = SchemaField(schema=list[SamtoolsStatsIdRecord], blank=False, null=False)
    #: first fragment qualities for each cycle
    ffq = SchemaField(schema=list[SamtoolsStatsFqRecord], blank=False, null=False)
    #: last fragment qualities for each cycle
    lfq = SchemaField(schema=list[SamtoolsStatsFqRecord], blank=False, null=False)
    #: first fragment ACGT content for each cycle
    fbc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord], blank=False, null=False)
    #: last fragment ACGT content for each cycle
    lbc = SchemaField(schema=list[SamtoolsStatsBasePercentagesRecord], blank=False, null=False)

"""Common denominator data structures for QC statistics in VarFish.

While we expose all raw statistics via a REST API, this data type is used for generating
the quality control display in the frontend.

We only use Pydantic models here; we construct them on the fly from the raw statistics in
the REST API endpoints.
"""

import pydantic


class SampleReadStats(pydantic.BaseModel):
    """Per-sample QC stats for reads."""

    #: sample name
    sample: str

    #: N50 of reads
    read_length_n50: int
    #: read length histogram as ``[bin_start, value]`` pairs, equidistant bins, can be
    #: estimated from first two bins
    read_length_histogram: list[list[int, int]]

    #: total number of reads
    total_reads: int
    #: total number of base pairs
    total_yield: int
    #: number of first fragments / read1
    fragment_first: int
    #: number of second fragments / read2
    fragment_last: int


class RegionCoverageStats(pydantic.BaseModel):
    """Per-region QC stats for alignment."""

    #: region name
    region_name: str
    #: overall mean read depth
    mean_rd: float
    #: read depth for coverage as ``[>={cov}x, count]`` pairs
    min_rd_fraction: list[list[int, float]]


class InsertSizeStats(pydantic.BaseModel):
    """Per-sample QC stats for insert sizes."""

    #: read orientation of inwards-facing reads
    read_orientation: str
    #: mean insert size
    insert_size_mean: float
    #: stddev of insert size
    insert_size_stddev: float
    #: insert size histogram as ``[bin_start, value]`` pairs, equidistant bins, can be
    #: estimated from first two bins
    insert_size_histogram: list[list[int, int]]


class DetailedAlignmentCounts(pydantic.BaseModel):
    """Detailed alignment counts"""

    #: number of primary alignments
    primary: int
    #: number of secondary alignments
    secondary: int
    #: number of secondary alignments (chimeric/split reads)
    supplementary: int
    #: number of reads marked as duplicate
    duplicates: int
    #: number of mapped reads
    mapped: int
    #: number of properly paired reads
    properly_paired: int
    #: number of properly paired reads with itself and mate mapped
    with_itself_and_mate_mapped: int
    #: number of singleton reads
    singletons: int
    #: number of reads with mate mapped to different chr
    with_mate_mapped_to_different_chr: int
    #: number of reads with mate mapped to different chr and "higher" mapq >= 5 / 10
    #: (samtools flagstat/Dragen)
    with_mate_mapped_to_different_chr_mapq: int

    #: mismatch rate
    mismatch_rate: float

    #: statistics of reads with mapq in bins of 10, -1 => unmapped
    mapq: list[list[int, int]]


class SampleAlignmentStats(pydantic.BaseModel):
    """Per-sample QC stats for alignment."""

    #: sample name
    sample: str

    #: aligned reads/pairs count
    detailed_counts: DetailedAlignmentCounts
    #: per-chromosome counts
    per_chromosome_counts: list[(str, int)]
    #: statistics on insert size
    insert_size_stats: InsertSizeStats
    #: per-region coverage stats
    region_coverage_stats: list[RegionCoverageStats]


class RegionVariantStats(pydantic.BaseModel):
    """Per-region sequence variant statistics."""

    #: name of the region
    region_name: str
    #: number of SNVs
    snv_count: int
    #: number of indels
    indel_count: int
    #: multi-allelic sites
    multiallelic_count: int

    #: number of transitions
    transition_count: int
    #: number of transversions
    transversion_count: int
    #: Ts/Tv ratio
    tstv_ratio: float


class SampleSeqvarStats(pydantic.BaseModel):
    """Per-sample QC stats for sequence variants."""

    #: sample name
    sample: str
    #: genome-wide statistics
    genome_wide: RegionVariantStats
    #: per-region statistics
    per_region: list[RegionVariantStats]


class SampleStrucvarStats(pydantic.BaseModel):
    """Per-sample QC stats for structural variants."""

    #: sample name
    sample: str
    #: number of deletions
    deletion_count: int
    #: number of duplications
    duplication_count: int
    #: number of insertions
    insertion_count: int
    #: number of inversions
    inversion_count: int
    #: number of breakend pairs
    breakend_count: int

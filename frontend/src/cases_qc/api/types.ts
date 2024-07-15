export interface SampleReadStats {
  sample: string
  read_length_n50: number
  read_length_histogram: [number, number][]
  total_reads: number
  total_yield: number
  fragment_first: number | null
  fragment_last: number | null
}

export interface RegionCoverageStats {
  region_name: string
  mean_rd: number
  min_rd_fraction: [number, number][]
}

export interface InsertSizeStats {
  insert_size_mean: number
  insert_size_median: number | null
  insert_size_stddev: number
  insert_size_histogram: [number, number][]
}

export interface DetailedAlignmentCounts {
  primary: number
  secondary: number
  supplementary: number
  duplicates: number
  mapped: number
  properly_paired: number
  with_itself_and_mate_mapped: number
  singletons: number
  with_mate_mapped_to_different_chr: number
  with_mate_mapped_to_different_chr_mapq: number
  mismatch_rate: number
  mapq: [number, number][]
}

export interface SampleAlignmentStats {
  sample: string
  detailed_counts: DetailedAlignmentCounts
  per_chromosome_counts: [string, number][]
  insert_size_stats: InsertSizeStats
  region_coverage_stats: RegionCoverageStats[]
}

export interface RegionVariantStats {
  region_name: string
  snv_count: number
  indel_count: number
  multiallelic_count: number
  transition_count: number
  transversion_count: number
  tstv_ratio: number
}

export interface SampleSeqvarStats {
  sample: string
  genome_wide: RegionVariantStats
  per_region: RegionVariantStats[]
}

export interface SampleStrucvarStats {
  sample: string
  deletion_count: number
  duplication_count: number
  insertion_count: number
  inversion_count: number
  breakend_count: number
}

export interface VarfishStats {
  samples: string[]
  readstats: SampleReadStats[]
  alignmentstats: SampleAlignmentStats[]
  seqvarstats: SampleSeqvarStats[]
  strucvarstats: SampleStrucvarStats[]
}

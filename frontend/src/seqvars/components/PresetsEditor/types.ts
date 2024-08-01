/**
 * Frequency thresholds for gnomAD nuclear as returned from API.
 */
export interface GnomadFreqs {
  enabled?: boolean
  homozygous?: number | null
  heterozygous?: number | null
  hemizygous?: number | null
  frequency?: number | null
}

/**
 * Frequency thresholds for mitochondrial variants as returned from API.
 */
export interface MitochondrialFreqs {
  enabled?: boolean
  heteroplasmic?: number | null
  homoplasmic?: number | null
  frequency?: number | null
}

/**
 * Frequency thresholds for in-house data as returned from API.
 */
export interface InhouseFreqs {
  enabled?: boolean
  homozygous?: number | null
  heterozygous?: number | null
  hemizygous?: number | null
  carriers?: number | null
}

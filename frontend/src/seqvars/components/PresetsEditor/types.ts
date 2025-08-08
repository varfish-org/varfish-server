/**
 * Frequency thresholds for nuclear variant frequencies as returned from API.
 */
export interface NuclearFreqs {
  enabled?: boolean
  max_hom?: number | null
  max_het?: number | null
  max_hemi?: number | null
  max_af?: number | null
}

/**
 * Frequency thresholds for mitochondrial frequencies as returned from API.
 */
export interface MitochondrialFreqs {
  enabled?: boolean
  max_het?: number | null
  max_hom?: number | null
  max_af?: number | null
}

/**
 * Frequency thresholds for inhouse frequencies as returned from API.
 */
export interface InhouseFreqs {
  enabled?: boolean
  max_het?: number | null
  max_hom?: number | null
  max_hemi?: number | null
  max_carriers?: number | null
}

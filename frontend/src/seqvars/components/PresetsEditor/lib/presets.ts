import { SeqvarsGenotypePresetChoice } from '@varfish-org/varfish-api/lib'

/** Labels for genotype presets. */
export const GENOTYPE_PRESET_LABELS: {
  [key in SeqvarsGenotypePresetChoice]: string
} = {
  any: 'Any',
  de_novo: 'De novo',
  dominant: 'Dominant',
  homozygous_recessive: 'Homozygous recessive',
  compound_heterozygous_recessive: 'Compound heterozygous recessive',
  recessive: 'Recessive',
  x_recessive: 'X-linked recessive',
  affected_carriers: 'Affected carriers',
}

/** Debounce wait value for category presets updates. */
export const CATEGORY_PRESETS_DEBOUNCE_WAIT = 500

/** Enumeration for the presets categories. */
export enum PresetsCategory {
  QUALITY = 'quality',
  FREQUENCY = 'frequency',
  CONSEQUENCE = 'consequence',
  LOCUS = 'locus',
  PHENOTYPE_PRIO = 'phenotype_prioritization',
  VARIANT_PRIO = 'variant_prioritization',
  CLINVAR = 'clinvar',
  COLUMNS = 'columns',
  PREDEFINED_QUERIES = 'predefined_queries',
}

/** Type for the category items. */
export interface PresetsListItem {
  sodar_uuid: string
  label: string
  rank?: number
}

/** Information about one category. */
export interface PresetsCategoryInfo {
  label: string
  category: PresetsCategory
  items: PresetsListItem[]
}

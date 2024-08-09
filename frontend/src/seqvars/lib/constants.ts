import { SeqvarsGenotypePresetChoice } from '@varfish-org/varfish-api/lib'

/** Labels for `SeqvarsGenotypePresetChoice`. */
export const SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS: {
  [key in SeqvarsGenotypePresetChoice]: string
} = {
  any: 'any',
  de_novo: 'de novo',
  dominant: 'dominant',
  homozygous_recessive: 'hom. recessive',
  compound_heterozygous_recessive: 'comp. het. recessive',
  recessive: 'recessive',
  x_recessive: 'X-linked recessive',
  affected_carriers: 'affected carriers',
}

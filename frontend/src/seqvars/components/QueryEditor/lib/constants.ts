/**
 * Constants used in the `QueryEditor` component.
 */
import {
  RecessiveModeEnum,
  SeqvarsGenotypePresetChoice,
} from '@varfish-org/varfish-api/lib'

/** Mapping from genotype preset to associated recessive mode. */
export const GENOTYPE_PRESET_TO_RECESSIVE_MODE: Record<
  SeqvarsGenotypePresetChoice,
  RecessiveModeEnum
> = {
  de_novo: 'disabled',
  dominant: 'disabled',
  homozygous_recessive: 'homozygous_recessive',
  affected_carriers: 'disabled',
  any: 'disabled',
  compound_heterozygous_recessive: 'comphet_recessive',
  recessive: 'recessive',
  x_recessive: 'recessive',
}

/** Debounce wait value for query updates. */
export const QUERY_DEBOUNCE_WAIT = 500

import {
  RecessiveModeEnum,
  SeqvarsGenotypeChoice,
  SeqvarsGenotypePresetChoice,
} from '@varfish-org/varfish-api/lib'

export enum SexAssignedAtBirth {
  UNDEFINED = 'undefined',
  MALE = 'male',
  FEMALE = 'female',
}

export enum Affected {
  UNDEFINED = 'undefined',
  UNAFFECTED = 'unaffected',
  AFFECTED = 'affected',
}

export type Pedigree = 'index' | 'father' | 'mother'

export type PedigreeInheritanceMode = Record<Pedigree, SeqvarsGenotypeChoice>

/** Mapping from genotype preset to associated recessive mode. */
export const GENOTYPE_PRESET_TO_RECESSIVE_MODE = {
  de_novo: 'disabled',
  dominant: 'disabled',
  homozygous_recessive: 'disabled',
  affected_carriers: 'disabled',
  any: 'disabled',
  compound_heterozygous_recessive: 'comphet_recessive',
  recessive: 'recessive',
  x_recessive: 'recessive',
} satisfies Record<SeqvarsGenotypePresetChoice, RecessiveModeEnum>

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

export const GENOTYPE_PRESETS = {
  de_novo: {
    recessiveMode: 'disabled',
    samples: { index: 'variant', father: 'ref', mother: 'ref' },
  },
  dominant: {
    recessiveMode: 'disabled',
    samples: { index: 'ref', father: 'ref', mother: 'ref' },
  },
  homozygous_recessive: {
    recessiveMode: 'disabled',
    samples: { index: 'hom', father: 'ref', mother: 'ref' },
  },
  affected_carriers: {
    recessiveMode: 'disabled',
    samples: { index: 'variant', father: 'any', mother: 'any' },
  },
  any: {
    recessiveMode: 'disabled',
    samples: { index: 'any', father: 'any', mother: 'any' },
  },
  compound_heterozygous_recessive: {
    recessiveMode: 'comphet_recessive',
    samples: {
      index: 'recessive_index',
      father: 'recessive_father',
      mother: 'recessive_mother',
    },
  },
  recessive: {
    recessiveMode: 'recessive',
    samples: {
      index: 'recessive_index',
      father: 'recessive_father',
      mother: 'recessive_mother',
    },
  },
  x_recessive: {
    recessiveMode: 'recessive',
    samples: {
      index: 'recessive_index',
      father: 'recessive_father',
      mother: 'recessive_mother',
    },
  },
} satisfies Record<
  SeqvarsGenotypePresetChoice,
  { recessiveMode: RecessiveModeEnum; samples: PedigreeInheritanceMode }
>

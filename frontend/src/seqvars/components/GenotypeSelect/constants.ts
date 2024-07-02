import { GenotypePresets, InheritanceMode } from './types'

const { WILD_TYPE, HET_ALT, HOM_ALT } = InheritanceMode
export const GENOTYPE_PRESETS = {
  DE_NOVO: {
    index: new Set([HET_ALT, HOM_ALT]),
    father: new Set([WILD_TYPE]),
    mother: new Set([WILD_TYPE]),
  },
  DOMINANT: {
    index: new Set([HET_ALT]),
    father: new Set([WILD_TYPE]),
    mother: new Set([WILD_TYPE]),
  },
  HOMOZYGOUS_RECESSIVE: {
    index: new Set([HOM_ALT]),
    father: new Set([HET_ALT]),
    mother: new Set([HET_ALT]),
  },
  COMPOUND_RECESSIVE: {
    index: new Set([HET_ALT]), // TODO c/h index?
    father: new Set([HOM_ALT]), // TODO recess parent?
    mother: new Set([HET_ALT]), // TODO recess parent?
  },
  RECESSIVE: {
    index: new Set([HET_ALT]), // TODO recess index?
    father: new Set([HET_ALT]), // TODO recess parent?
    mother: new Set([HET_ALT]), // TODO recess parent?
  },
  X_RECESSIVE: {
    index: new Set([HOM_ALT]),
    father: new Set([WILD_TYPE]),
    mother: new Set([HET_ALT]),
  },
  AFFECTED_CARRIERS: {
    index: new Set([HET_ALT, HOM_ALT]),
    father: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    mother: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
  },
  ANY: {
    index: new Set([HET_ALT, HOM_ALT]),
    father: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    mother: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
  },
} satisfies GenotypePresets

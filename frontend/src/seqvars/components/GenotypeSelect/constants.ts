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

export interface PedigreeMember {
  name: Pedigree
  sexAssignedAtBirth: SexAssignedAtBirth
  affected: Affected
}

export enum InheritanceMode {
  WILD_TYPE = 'wild-type',
  HET_ALT = 'het. alt.',
  HOM_ALT = 'hom. alt.',
  NO_CALL = 'no call',
}

export type InheritanceModeSet = Set<InheritanceMode>

export type PedigreeInheritanceMode = Record<Pedigree, InheritanceModeSet>

export type GenotypePresets = Record<string, PedigreeInheritanceMode>

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
    index: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    father: new Set([WILD_TYPE]),
    mother: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
  },
  AFFECTED_CARRIERS: {
    index: new Set([HET_ALT, HOM_ALT]),
    father: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    mother: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
  },
  ANY: {
    index: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    father: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
    mother: new Set([HET_ALT, HOM_ALT, WILD_TYPE]),
  },
} satisfies GenotypePresets
export type GenotypePresetKey = keyof typeof GENOTYPE_PRESETS

export type PedigreeModel = Record<
  Pedigree,
  { checked: boolean; mode: Set<InheritanceMode> }
>

export type GenotypeModel = {
  preset: GenotypePresetKey
  value: PedigreeModel
}

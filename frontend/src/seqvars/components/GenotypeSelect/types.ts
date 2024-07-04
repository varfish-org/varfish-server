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

export type GenotypeModel = Record<
  Pedigree,
  { checked: boolean; mode: Set<InheritanceMode> }
>

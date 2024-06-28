export enum GenotypeChoice {
  DE_NOVO = 'de novo',
  DOMINANT = 'dominant',
  HOMOZYGOUS_RECESSIVE = 'homozygous recessive',
  COMPOUND_RECESSIVE = 'compound recessive',
  RECESSIVE = 'recessive',
  X_RECESSIVE = 'x recessive',
  AFFECTED_CARRIERS = 'affected carriers',
  ANY = 'any',
}

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

export interface PedigreeMember {
  name: string
  sexAssignedAtBirth: SexAssignedAtBirth
  affected: Affected
}

export enum InheritanceMode {
  WILD_TYPE = 'wild-type',
  HET_ALT = 'het. alt.',
  HOM_ALT = 'hom. alt.',
}

export type InheritanceModeSet = Set<InheritanceMode>

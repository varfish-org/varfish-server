/**
 * ACMG category criteria.
 */
export enum Category {
  PATHOGENIC_VERY_STRONG = 'pathogenic_very_strong',
  PATHOGENIC_STRONG = 'pathogenic_strong',
  PATHOGENIC_MODERATE = 'pathogenic_moderate',
  PATHOGENIC_SUPPORTING = 'pathogenic_supporting',
  BENIGN_STANDALONE = 'benign_standalone',
  BENIGN_VERY_STRONG = 'benign_very_strong',
  BENIGN_STRONG = 'benign_strong',
  BENIGN_MODERATE = 'benign_moderate',
  BENIGN_SUPPORTING = 'benign_supporting',
}

/**
 * ACMG criterion.
 */
export interface Criterion {
  /** criteria category */
  category: Category
  /** computer-aimed name; e.g. "pvs1" */
  name:
    | 'pvs1'
    | 'ps1'
    | 'ps2'
    | 'ps3'
    | 'ps4'
    | 'pm1'
    | 'pm2'
    | 'pm3'
    | 'pm4'
    | 'pm5'
    | 'pm6'
    | 'pp1'
    | 'pp2'
    | 'pp3'
    | 'pp4'
    | 'pp5'
    | 'ba1'
    | 'bs1'
    | 'bs2'
    | 'bs3'
    | 'bs4'
    | 'bp1'
    | 'bp2'
    | 'bp3'
    | 'bp4'
    | 'bp5'
    | 'bp6'
    | 'bp7'
  /** title; e.g. "PVS1" */
  title: string
  /** synopsis; e.g., "null variant" */
  synopsis: string
  /** description; e.g., "Null variant (nonsense, ..." */
  description: string
}

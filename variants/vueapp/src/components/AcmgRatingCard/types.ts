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
  name: string
  /** title; e.g. "PVS1" */
  title: string
  /** synopsis; e.g., "null variant" */
  synopsis: string
  /** description; e.g., "Null variant (nonsense, ..." */
  description: string
}

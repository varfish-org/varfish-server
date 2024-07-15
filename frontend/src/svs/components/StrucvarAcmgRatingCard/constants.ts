import { AcmgRating } from '@/svs/api/strucvarClient'

/** Empty ACMG rating data. */
/** Template for an empty ACMG rating. */
export const EMPTY_ACMG_RATING_TEMPLATE: AcmgRating = {
  genomeBuild: 'grch37',
  chrom: '',
  start: 0,
  stop: 0,
  userRepr: '',
  svType: 'DEL',
}

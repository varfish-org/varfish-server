import { displayName } from '@/varfish/helpers'
import { PedigreeMember } from './types'

/** Get comma-separated string with individual names. */
export const getIndividuals = (pedigree: PedigreeMember[]) => {
  return pedigree
    .map((row) => {
      return displayName(row.name)
    })
    .join(', ')
}

import { describe, expect, test } from 'vitest'

import { previousQueryDetailsToQuerySettings } from './variantQuery.funcs'

const caseObj = {
  name: 'NA12878',
  pedigree: [
    { name: 'NA12878-N1-DNA1-WES1' },
    { name: 'NA12891-N1-DNA1-WES1' },
    { name: 'NA12892-N1-DNA1-WES1' },
  ],
}

/** Query details as stored by the backend for the given genotypes. */
const makeQueryDetails = (
  genotypes: Record<string, string>,
  recessiveIndices: Record<string, string>,
  compoundRecessiveIndices: Record<string, string>,
) => ({
  query_settings: {
    database_select: 'refseq',
    genomic_region: [],
    recessive_indices: recessiveIndices,
    compound_recessive_indices: compoundRecessiveIndices,
    ...Object.fromEntries(
      Object.entries(genotypes).map(([name, gt]) => [`${name}_gt`, gt]),
    ),
  },
})

describe('previousQueryDetailsToQuerySettings', () => {
  test('restores the comp het index', () => {
    const result = previousQueryDetailsToQuerySettings(
      caseObj,
      makeQueryDetails(
        {
          'NA12878-N1-DNA1-WES1': 'index',
          'NA12891-N1-DNA1-WES1': 'recessive-parent',
          'NA12892-N1-DNA1-WES1': 'recessive-parent',
        },
        {},
        { NA12878: 'NA12878-N1-DNA1-WES1' },
      ),
    )

    expect(result.genotype).toEqual({
      'NA12878-N1-DNA1-WES1': 'comphet-index',
      'NA12891-N1-DNA1-WES1': 'recessive-parent',
      'NA12892-N1-DNA1-WES1': 'recessive-parent',
    })
    expect(result.recessive_index).toBe('NA12878-N1-DNA1-WES1')
    expect(result.recessive_mode).toBe('compound-recessive')
  })

  test('restores the recessive index', () => {
    const result = previousQueryDetailsToQuerySettings(
      caseObj,
      makeQueryDetails(
        {
          'NA12878-N1-DNA1-WES1': 'recessive-index',
          'NA12891-N1-DNA1-WES1': 'recessive-parent',
          'NA12892-N1-DNA1-WES1': 'recessive-parent',
        },
        { NA12878: 'NA12878-N1-DNA1-WES1' },
        {},
      ),
    )

    expect(result.genotype).toEqual({
      'NA12878-N1-DNA1-WES1': 'recessive-index',
      'NA12891-N1-DNA1-WES1': 'recessive-parent',
      'NA12892-N1-DNA1-WES1': 'recessive-parent',
    })
    expect(result.recessive_index).toBe('NA12878-N1-DNA1-WES1')
    expect(result.recessive_mode).toBe('recessive')
  })
})

import { igvLocus } from '@bihealth/reev-frontend-lib/lib/utils'
import { describe, expect, test } from 'vitest'

import { StrucvarResultRow, strucvarFromResultRow } from './strucvar'

/** Build a result row, overriding the given fields. */
const row = (
  overrides: Partial<StrucvarResultRow> = {},
): StrucvarResultRow => ({
  release: 'GRCh37',
  chromosome: '17',
  chromosome2: '17',
  start: 100,
  end: 200,
  sv_type: 'DEL',
  ...overrides,
})

describe('strucvarFromResultRow', () => {
  test('maps a linear SV', () => {
    const strucvar = strucvarFromResultRow(row({ sv_type: 'DUP' }))

    expect(strucvar).toMatchObject({
      svType: 'DUP',
      genomeBuild: 'grch37',
      chrom: '17',
      start: 100,
      stop: 200,
    })
  })

  test('maps an insertion to its insertion point', () => {
    const strucvar = strucvarFromResultRow(row({ sv_type: 'INS' }))

    expect(strucvar).toMatchObject({ svType: 'INS', chrom: '17', start: 100 })
  })

  test('maps a breakend, keeping the partner end', () => {
    const strucvar = strucvarFromResultRow(
      row({ sv_type: 'BND', chromosome2: '22' }),
    )

    expect(strucvar).toMatchObject({
      svType: 'BND',
      chrom: '17',
      chrom2: '22',
      start: 100,
      stop: 200,
    })
  })

  test('strips the chr prefix from both ends', () => {
    const strucvar = strucvarFromResultRow(
      row({
        release: 'GRCh38',
        sv_type: 'BND',
        chromosome: 'chr17',
        chromosome2: 'chr22',
      }),
    )

    expect(strucvar).toMatchObject({
      genomeBuild: 'grch38',
      chrom: '17',
      chrom2: '22',
    })
  })

  // The rows feed straight into `igvLocus`, so pin the loci they produce.
  test.each([
    [{ sv_type: 'DEL' }, '17:100-200'],
    [{ sv_type: 'INS' }, '17:100-101'],
    [{ sv_type: 'BND', chromosome2: '22' }, '17:100-101 22:200-201'],
    [{ sv_type: 'BND', chromosome2: 'MT' }, '17:100-101 chrM:200-201'],
  ])('yields the IGV locus %o -> %s', (overrides, expected) => {
    expect(igvLocus(strucvarFromResultRow(row(overrides)))).toBe(expected)
  })
})

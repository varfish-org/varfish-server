import { describe, expect, test } from 'vitest'
import { parseGenomeRegion } from './lib'

describe('parseGenomeRegion - valid', () => {
  test.each([
    // full chromosomes
    ['chr1', { chromosome: '1' }],
    ['1', { chromosome: '1' }],
    ['chrX', { chromosome: 'X' }],
    ['X', { chromosome: 'X' }],
    ['chrY', { chromosome: 'Y' }],
    ['Y', { chromosome: 'Y' }],
    ['chrM', { chromosome: 'M' }],
    ['M', { chromosome: 'M' }],
    ['chrMT', { chromosome: 'M' }],
    ['MT', { chromosome: 'M' }],
    // region
    [
      'chr1:1,000,000-2,000,000',
      { chromosome: '1', range: { start: 1000000, end: 2000000 } },
    ],
    [
      '1:1,000,000-2,000,000',
      { chromosome: '1', range: { start: 1000000, end: 2000000 } },
    ],
    // 1bp length range
    ['1:100-100', { chromosome: '1', range: { start: 100, end: 100 } }],
    // "weird" formatting
    [
      '1:1,0,0,0,0,0,0-2,0,0,0,0,0,0',
      { chromosome: '1', range: { start: 1000000, end: 2000000 } },
    ],
  ])('parses %s -> %s', (input, expected) => {
    expect(parseGenomeRegion(input)).toEqual(expected)
  })
})

describe('parseGenomeRegion - invalid', () => {
  test.each([
    // invalid chromosome
    ['chr0', /Invalid chromosome:/],
    ['0', /Invalid chromosome:/],
    ['chr23', /Invalid chromosome:/],
    ['23', /Invalid chromosome:/],
    ['chrZ', /Invalid chromosome:/],
    ['Z', /Invalid chromosome:/],
    ['chrA', /Invalid chromosome:/],
    ['A', /Invalid chromosome:/],
    ['chrMM', /Invalid chromosome:/],
    ['MM', /Invalid chromosome:/],
    // invalid range
    ['chr1:1-2-3', /Invalid range:/],
    ['1:1-2-3', /Invalid range:/],
    // multiple colons
    ['chr1:1:2', /Too many colons in input/],
    ['1:1:2', /Too many colons in input/],
    // multiple hyphens
    ['chr1:1-2-3', /Invalid range:/],
    ['1:1-2-3', /Invalid range:/],
    // invalid range
    ['chr1:101-100', /Invalid range:/],
    ['1:101-100', /Invalid range:/],
  ])('throws on %s', (input, regex) => {
    expect(() => parseGenomeRegion(input)).toThrowError(regex)
  })
})

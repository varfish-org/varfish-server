import { describe, expect, test } from 'vitest'
import { parseGenomeRegion } from './lib'

describe('parseGenomeRegion - valid', () => {
  test.each([
    ['chr1', { chromosome: '1' }],
  ])('parses %s -> %s', (input, expected) => {
    expect(parseGenomeRegion(input)).toEqual(expected)
  })
})

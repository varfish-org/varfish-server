import { describe, expect, test } from 'vitest'

import { pairwise, zip } from './lib'

describe('zip', () => {
  test('zips two arrays together', () => {
    const lhs = [1, 2, 3]
    const rhs = ['a', 'b', 'c']
    const result = zip(lhs, rhs)
    expect(result).toEqual([
      [1, 'a'],
      [2, 'b'],
      [3, 'c'],
    ])
  })
})

describe('pairwise', () => {
  test('returns array for pairwise iteration', () => {
    const arr = [1, 2, 3]
    const result = pairwise(arr)
    expect(result).toEqual([
      [1, undefined],
      [2, 1],
      [3, 2],
    ])
  })

  test('returns empty array for empty input', () => {
    const result = pairwise([])
    expect(result).toEqual([])
  })
})

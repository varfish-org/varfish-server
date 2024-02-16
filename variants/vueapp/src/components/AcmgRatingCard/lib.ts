/**
 * Zip two arrays together.
 *
 * @param lhs first array
 * @param rhs second array
 * @returns zipped array
 */
export function zip<T1, T2>(lhs: T1[], rhs: T2[]): [T1, T2][] {
  return lhs.map((value, index) => [value, rhs[index]])
}

/**
 * Return array for pairwise iteration.
 *
 * @param arr array to iterate over
 * @returns pairwise array
 */
export function pairwise<T>(arr: T[]): [T | undefined, T | undefined][] {
  if (arr.length === 0) {
    return []
  } else {
    const tmp = arr as (T | undefined)[]
    return zip(tmp, ([undefined] as (T | undefined)[]).concat(tmp))
  }
}

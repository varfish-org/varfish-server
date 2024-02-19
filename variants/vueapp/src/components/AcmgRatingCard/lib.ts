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
export function pairwise<T>(arr: T[]): [T, T | undefined][] {
  if (arr.length === 0) {
    return []
  } else {
    const tmp = arr
    return zip(tmp, ([undefined] as (T | undefined)[]).concat(tmp))
  }
}

/**
 * Return color for ACMG rating.
 */
export function acmgColor(acmgClass: number): string {
  if (acmgClass === 5) {
    return 'red-darken-2'
  } else if (acmgClass === 4) {
    return 'red-lighten-2'
  } else if (acmgClass === 3) {
    return 'grey-darken-2'
  } else if (acmgClass === 2) {
    return 'green-lighten-2'
  } else if (acmgClass === 1) {
    return 'green-darken-2'
  } else {
    return 'yello-darken-2'
  }
}

/**
 * Return class name for ACMG rating.
 */
export function acmgLabel(acmgClass: number): string {
  if (acmgClass === 5) {
    return 'pathogenic'
  } else if (acmgClass === 4) {
    return 'likely pathogenic'
  } else if (acmgClass === 3) {
    return 'uncertain significance'
  } else if (acmgClass === 2) {
    return 'likely benign'
  } else if (acmgClass === 1) {
    return 'benign'
  } else {
    return 'UNKNOWN'
  }
}

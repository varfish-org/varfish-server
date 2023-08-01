/**
 * Various helpers used throughout the VarFish front-end.
 */

import TimeAgo from 'javascript-time-ago'
import en from 'javascript-time-ago/locale/en'

// Setup `javascript-time-ago` library by adding the English default locale
// creating a `TimeAgo` object with the `en-US` locale.
TimeAgo.addDefaultLocale(en)
const timeAgo = new TimeAgo('en-US')

/**
 * Types representing a genome range.
 */
export interface GenomeRange {
  /** Chromosome name. */
  chromosome: string
  /** 1-based start position */
  start: number
  /** 1-based end position */
  end: number
}

/**
 * Compute overlap length between two `GenomeRange` values.
 *
 * @param lhs First range.
 * @param rhs Second range.
 * @returns The overlap length.
 */
export function overlapLength(lhs: GenomeRange, rhs: GenomeRange): number {
  if (lhs.chromosome !== rhs.chromosome) {
    return 0.0
  }

  const begin = Math.max(lhs.start - 1, rhs.start - 1)
  const end = Math.min(lhs.end, rhs.end)

  if (begin >= end) {
    return 0.0
  } else {
    return end - begin
  }
}

/**
 * Return whether two ranges representing BND or INS start positions overlap within a given
 * radius.
 *
 * @param lhs First start position.
 * @param rhs Second start position.
 * @param radius The radius to use for comparison.
 * @returns Whether `lhs` and `rhs` are within a `radius`.
 */
export function bndInsOverlap(
  lhs: GenomeRange,
  rhs: GenomeRange,
  radius: number,
): boolean {
  return (
    overlapLength(
      {
        chromosome: lhs.chromosome,
        start: lhs.start - radius,
        end: lhs.start + radius,
      },
      { chromosome: rhs.chromosome, start: rhs.start, end: rhs.start + 1 },
    ) > 0
  )
}

/**
 * Compute reciprocal overlap between two `GenomeRange` values.
 *
 * @param lhs First range.
 * @param rhs Second range.
 * @returns Reciprocal overlap length.
 */
export function reciprocalOverlap(lhs: GenomeRange, rhs: GenomeRange): number {
  const overlap = overlapLength(lhs, rhs)
  return Math.min(
    overlap / (rhs.end - rhs.start + 1),
    overlap / (lhs.end - lhs.start + 1),
  )
}

/**
 * Convert sample name to its display name.
 *
 * Basically, this is only needed for output of the SNAPPY Pipeline.
 *
 * @param name The sample name to format.
 * @returns Sample name ready for display.
 */
export function displayName(name: string): string {
  if (name) {
    const re = /-N\d+-(DNA|RNA)\d+-(WES|WGS|Panel_seq)\d+$/
    return name.replace(re, '')
  } else {
    return name
  }
}

/**
 * Format large integers using thousands separators.
 *
 * @param value Value to format.
 * @param nullValue String to use if `value` is nullish.
 * @returns Formatted integer.
 */
export function formatLargeInt(value: number, nullValue: string = '-'): string {
  if (value === null || value === undefined) {
    return nullValue
  } else {
    return value.toLocaleString('en-US')
  }
}

/**
 * Parse and format date for "ago" display.
 *
 * @param time Time string to parse and format.
 * @param nullValue String to use if `time` is falsy.
 * @returns Formatted date/time.
 */
export function formatTimeAgo(time: string, nullValue: string = '-') {
  const t = Date.parse(time)
  if (!t) {
    return nullValue
  } else {
    return timeAgo.format(Date.parse(time))
  }
}

/**
 * Parse and format float for display.
 *
 * @param value The value to format.
 * @param n The number of fixed values
 * @returns Fixed representation.
 */
export function formatFloat(value: string, n: number): string {
  return parseFloat(value).toFixed(n)
}

/**
 * Parse time and prepare for display.
 *
 * @param time The time string to parse.
 * @returns Date/time in `en-US` locale.
 */
export function formatTime(time: string): string {
  const t = new Date(time)
  return t.toLocaleString('en-US')
}

/**
 * Truncate text and append ellipsis.
 *
 * @param text Text to truncate.
 * @param length Maximal length of text
 * @param ellipsisText Ellipsis text.
 * @param nullValue Value if text is falsy.
 * @returns Possibly truncated text, `nullValue` if text is falsy.
 */
export function truncateText(
  text: string | null,
  length: number,
  ellipsisText: string = '...',
  nullValue: string = '-',
): string {
  if (!text) {
    return nullValue
  } else {
    return text.length > length ? text.slice(0, length) + ellipsisText : text
  }
}

// sort array ascendingly
const asc = (arr: number[]): number[] => arr.sort((a, b) => a - b)

// compute array sum
const sum = (arr: number[]): number => arr.reduce((a, b) => a + b, 0)

// compute array mean
const mean = (arr: number[]): number => sum(arr) / arr.length

/**
 * Compute sample standard deviation.
 *
 * @param arr The nubers to compute the standard deviation for.
 * @returns Standard deviation value.
 */
export function std(arr: number[]): number {
  const mu = mean(arr)
  const diffArr = arr.map((a) => (a - mu) ** 2)
  return Math.sqrt(sum(diffArr) / (arr.length - 1))
}

/**
 * Compute a single quantile.
 *
 * @param arr The numbers to compute quantile for.
 * @param qs The quantile to compute
 * @return Quantile value.
 */
export function quantile(arr: number[], q: number): number {
  const sorted = asc(arr)
  const pos = (sorted.length - 1) * q
  const base = Math.floor(pos)
  const rest = pos - base
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base])
  } else {
    return sorted[base]
  }
}

/**
 * Compute multiple quantile values at once.
 *
 * @param arr The numbers to compute quantiles for.
 * @param qs The quantiles to compute
 * @returns Array of quantile values.
 */
export function quantiles(arr: number[], qs: number[]): number[] {
  const sorted = asc(arr)
  return qs.map((q) => {
    const pos = (sorted.length - 1) * q
    const base = Math.floor(pos)
    const rest = pos - base
    if (sorted[base + 1] !== undefined) {
      return sorted[base] + rest * (sorted[base + 1] - sorted[base])
    } else {
      return sorted[base]
    }
  })
}

/**
 * Performs a deep copy via serialization to JSON.
 *
 * @param val The value to copy.
 * @returns A copy of `val` that has no relation to `val` any more.
 */
export function copy<T>(val: T): T {
  return JSON.parse(JSON.stringify(val))
}

import TimeAgo from 'javascript-time-ago'
import en from 'javascript-time-ago/locale/en'

TimeAgo.addDefaultLocale(en)
const timeAgo = new TimeAgo('en-US')

export function displayName(name) {
  if (name) {
    const re = /-N\d+-(DNA|RNA)\d+-(WES|WGS|Panel_seq)\d+$/
    return name.replace(re, '')
  } else {
    return name
  }
}

/** Format large integers using thousands separators. */
export function formatLargeInt(value) {
  if (value === null || value === undefined) {
    return '-'
  } else {
    return value.toLocaleString('en-US')
  }
}

/** Parse and format date for "ago" display. */
export function formatTimeAgo(time) {
  const t = Date.parse(time)
  if (!t) {
    return '-'
  } else {
    return timeAgo.format(Date.parse(time))
  }
}

/** Parse and for display. */
export function formatTime(time) {
  const t = new Date(time)
  return t.toLocaleString('en-US')
}

// sort array ascending
const asc = (arr) => arr.sort((a, b) => a - b)

const sum = (arr) => arr.reduce((a, b) => a + b, 0)

const mean = (arr) => sum(arr) / arr.length

// sample standard deviation
export const std = (arr) => {
  const mu = mean(arr)
  const diffArr = arr.map((a) => (a - mu) ** 2)
  return Math.sqrt(sum(diffArr) / (arr.length - 1))
}

export const quantile = (arr, q) => {
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

export const quantiles = (arr, qs) => {
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
// const q25 = arr => quantile(arr, .25);
//
// const q50 = arr => quantile(arr, .50);
//
// const q75 = arr => quantile(arr, .75);
//
// const median = arr => q50(arr);

export const copy = (val) => JSON.parse(JSON.stringify(val))

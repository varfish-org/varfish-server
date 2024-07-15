import isEqual from 'fast-deep-equal'

export function matchesFrequencyPreset(value: unknown, preset: unknown) {
  return isEqual(value, preset)
}

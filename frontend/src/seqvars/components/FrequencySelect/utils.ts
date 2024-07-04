import isEqual from 'fast-deep-equal'

import {
  FREQUENCY_DB_K_SIZES,
  FREQUENCY_PRESETS,
  FrequencyModel,
  FrequencyPresetKey,
  FrequencyDB_Values,
  FrequencyDB_Numbers,
} from './constants'

export function getFrequencyValueFromPreset(
  key: FrequencyPresetKey,
): FrequencyModel {
  const frequencyPreset = FREQUENCY_PRESETS[key]
  return {
    preset: key,
    values: Object.fromEntries(
      Object.keys(FREQUENCY_DB_K_SIZES).map((key) => [
        key,
        key in frequencyPreset
          ? {
              checked: true,
              numbers: {
                ...(frequencyPreset[
                  key as keyof typeof frequencyPreset
                ] as object),
              },
            }
          : { checked: false, numbers: {} },
      ]),
    ) as FrequencyDB_Values,
  }
}

export function matchesFrequencyPreset(
  value: FrequencyModel,
  presetKey: FrequencyPresetKey,
) {
  const preset = FREQUENCY_PRESETS[presetKey]
  return Object.entries(value.values).every(([key, value]) => {
    if (!value.checked) {
      const isKeyCheckedInPreset = key in preset
      // if the key is present in the preset, it should be checked to match
      return !isKeyCheckedInPreset
    }
    const presetNumbers = preset[key as never] as Partial<FrequencyDB_Numbers>
    return isEqual(presetNumbers, value.numbers)
  })
}

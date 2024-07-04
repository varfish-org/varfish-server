import {
  FREQUENCY_DB_K_SIZES,
  FREQUENCY_PRESETS,
  FrequencyModel,
  FrequencyPresetKey,
  FrequencyDB_Values,
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
              numbers: frequencyPreset[key as keyof typeof frequencyPreset],
            }
          : { checked: false, numbers: {} },
      ]),
    ) as FrequencyDB_Values,
  }
}

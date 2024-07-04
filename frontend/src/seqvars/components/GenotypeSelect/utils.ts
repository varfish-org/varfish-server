import isEqual from 'fast-deep-equal/es6'
import {
  GENOTYPE_PRESETS,
  GenotypeModel,
  GenotypePresetKey,
  Pedigree,
  PedigreeModel,
} from './constants'

export const getGenotypeValueFromPreset = (
  key: GenotypePresetKey,
): GenotypeModel => ({
  preset: key,
  value: Object.fromEntries(
    Object.entries(GENOTYPE_PRESETS[key]).map(([name, mode]) => [
      name,
      { checked: true, mode },
    ]),
  ) as PedigreeModel,
})

export const matchesGenotypePreset = (
  value: GenotypeModel,
  presetKey: GenotypePresetKey,
) =>
  Object.entries(GENOTYPE_PRESETS[presetKey]).every(([name, mode]) =>
    isEqual(mode, value.value[name as Pedigree].mode),
  )

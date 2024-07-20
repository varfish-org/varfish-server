import isEqual from 'fast-deep-equal/es6'

import {
  SeqvarsGenotypePresetChoice,
  SeqvarsQuerySettingsGenotype,
} from '@varfish-org/varfish-api/lib'

import { LocalFields } from '@/seqvars/types'
import { GENOTYPE_PRESETS, Pedigree } from './constants'

export function getGenotypeSettingsFromPreset(
  key: SeqvarsGenotypePresetChoice,
): LocalFields<SeqvarsQuerySettingsGenotype> {
  const preset = GENOTYPE_PRESETS[key]
  return {
    recessive_mode: preset.recessiveMode,
    sample_genotype_choices: (['index', 'father', 'mother'] as Pedigree[]).map(
      (sample) => ({
        enabled: true,
        sample,
        genotype: preset.samples[sample],
        include_no_call: false,
      }),
    ),
  }
}

export const matchesGenotypePreset = (
  value: LocalFields<SeqvarsQuerySettingsGenotype>,
  presetKey: SeqvarsGenotypePresetChoice,
) => isEqual(value, getGenotypeSettingsFromPreset(presetKey))

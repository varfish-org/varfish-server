import { GENOTYPE_PRESETS, Pedigree } from './constants'
import { FilterGroup } from '../FilterGroup'
import GenotypeControls from './GenotypeControls.vue'
import { Query } from '@/seqvars/types'

export const genotypeFilterGroup = new FilterGroup({
  id: 'genotype',
  title: 'Genotype',
  createFromPreset: (_, value) => {
    const preset = GENOTYPE_PRESETS[value?.choice ?? 'any']
    return {
      recessive_mode: preset.recessiveMode,
      sample_genotype_choices: (
        ['index', 'father', 'mother'] as Pedigree[]
      ).map((sample) => ({
        enabled: true,
        sample,
        genotype: preset.samples[sample],
        include_no_call: false,
      })),
    }
  },
  getCompareFields: (v) => [v.recessive_mode, v.sample_genotype_choices],
  Component: GenotypeControls,
})

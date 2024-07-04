import { GENOTYPE_PRESETS } from '../GenotypeSelect/constants'
import { QuickPreset } from './types'

export const QUICK_PRESETS: QuickPreset[] = [
  {
    label: 'de-novo',
    genotype: GENOTYPE_PRESETS.DE_NOVO,
    frequency: 'dominant strict',
  },
  {
    label: 'dominant',
    genotype: GENOTYPE_PRESETS.DOMINANT,
    frequency: 'dominant strict',
  },
  {
    label: 'homozygous recessive',
    genotype: GENOTYPE_PRESETS.HOMOZYGOUS_RECESSIVE,
    frequency: 'recessive strict',
  },
  {
    label: 'compound recessive',
    genotype: GENOTYPE_PRESETS.COMPOUND_RECESSIVE,
    frequency: 'recessive strict',
  },
]

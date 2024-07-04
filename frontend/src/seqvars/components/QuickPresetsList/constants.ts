import { GENOTYPE_PRESETS } from '../GenotypeSelect/constants'
import { QuickPreset } from './types'

export const QUICK_PRESETS: QuickPreset[] = [
  {
    label: 'de-novo',
    genotype: 'DE_NOVO',
    frequency: 'dominant strict',
  },
  {
    label: 'dominant',
    genotype: 'DOMINANT',
    frequency: 'dominant strict',
  },
  {
    label: 'homozygous recessive',
    genotype: 'HOMOZYGOUS_RECESSIVE',
    frequency: 'recessive strict',
  },
  {
    label: 'compound recessive',
    genotype: 'COMPOUND_RECESSIVE',
    frequency: 'recessive strict',
  },
]

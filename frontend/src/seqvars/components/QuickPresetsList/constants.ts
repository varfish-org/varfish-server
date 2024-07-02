import { GENOTYPE_PRESETS } from '../GenotypeSelect/constants'
import { QuickPreset } from './types'

export const QUICK_PRESETS: QuickPreset[] = [
  { label: 'de-novo', genotype: GENOTYPE_PRESETS.DE_NOVO },
  { label: 'dominant', genotype: GENOTYPE_PRESETS.DOMINANT },
  {
    label: 'homozygous recessive',
    genotype: GENOTYPE_PRESETS.HOMOZYGOUS_RECESSIVE,
  },
  {
    label: 'compound recessive',
    genotype: GENOTYPE_PRESETS.COMPOUND_RECESSIVE,
  },
]

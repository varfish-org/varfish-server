import { FrequencyModel } from '@/seqvars/components/FrequencySelect/constants'
import { GenotypeModel } from '@/seqvars/components/GenotypeSelect/types'
import { QuickPreset } from '@/seqvars/components/QuickPresetsList/types'

export type Query = {
  preset: QuickPreset
  value: {
    genotype: GenotypeModel
    frequency: FrequencyModel
  }
  isRunning: boolean
}

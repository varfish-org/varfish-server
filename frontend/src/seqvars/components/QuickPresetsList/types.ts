import { PedigreeInheritanceMode } from '@/seqvars/components/GenotypeSelect/types'
import { FrequencyPresetKey } from '@/seqvars/components/FrequencySelect/constants'

export type QuickPreset = {
  label: string
  genotype: PedigreeInheritanceMode
  frequency: FrequencyPresetKey
}

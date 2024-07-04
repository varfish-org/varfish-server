import { GenotypePresetKey } from '@/seqvars/components/GenotypeSelect/constants'
import { FrequencyPresetKey } from '@/seqvars/components/FrequencySelect/constants'

export type QuickPreset = {
  label: string
  genotype: GenotypePresetKey
  frequency: FrequencyPresetKey
}

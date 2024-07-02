import { GenotypeState } from '@/seqvars/components/GenotypeSelect/types'
import { QuickPreset } from '@/seqvars/components/QuickPresetsList/types'

export type Query = {
  preset: QuickPreset
  value: { genotype: GenotypeState }
  isRunning: boolean
}

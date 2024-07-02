import { areSetsEqual } from '@/seqvars/utils'
import { GenotypeState, Pedigree, PedigreeInheritanceMode } from './types'

export const doesValueMatchGenotypePreset = (
  value: GenotypeState,
  preset: PedigreeInheritanceMode,
) =>
  Object.entries(preset).every(([name, mode]) =>
    areSetsEqual(mode, value[name as Pedigree].mode),
  )

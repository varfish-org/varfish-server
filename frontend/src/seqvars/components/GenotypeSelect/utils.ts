import { areSetsEqual } from '@/seqvars/utils'
import { GenotypeModel, Pedigree, PedigreeInheritanceMode } from './types'

export const doesValueMatchGenotypePreset = (
  value: GenotypeModel,
  preset: PedigreeInheritanceMode,
) =>
  Object.entries(preset).every(([name, mode]) =>
    areSetsEqual(mode, value[name as Pedigree].mode),
  )

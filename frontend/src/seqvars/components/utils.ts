import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import { matchesFrequencyPreset } from './FrequencySelect/utils'
import { matchesGenotypePreset } from './GenotypeSelect/utils'

export function matchesPredefinedQuery(
  presets: SeqvarsQueryPresetsSetVersionDetails,
  query: Query,
  pq: SeqvarsPredefinedQuery,
): boolean {
  const genotype = pq.genotype?.choice
  const frequency = presets.seqvarsquerypresetsfrequency_set.find(
    (f) => f.sodar_uuid === pq.frequency,
  )
  return (
    !!genotype &&
    matchesGenotypePreset(query.genotype, genotype) &&
    !!frequency &&
    matchesFrequencyPreset(query.frequency, frequency)
  )
}

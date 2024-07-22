import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import { matchesFrequencyPreset } from './FrequencySelect/utils'
import { matchesGenotypePreset } from './GenotypeSelect/utils'
import { matchesPathogenicityPrioPreset } from './PathogenicityPrioSelect/utils'
import { matchesPhenotypePrioPreset } from './PhenotypePrioSelect/utils'

export function matchesPredefinedQuery(
  presets: SeqvarsQueryPresetsSetVersionDetails,
  query: Query,
  pq: SeqvarsPredefinedQuery,
): boolean {
  const genotype = pq.genotype?.choice
  const frequency = presets.seqvarsquerypresetsfrequency_set.find(
    (f) => f.sodar_uuid === pq.frequency,
  )
  const phenotypePrio = presets.seqvarsquerypresetsphenotypeprio_set.find(
    (p) => p.sodar_uuid === pq.phenotypeprio,
  )
  const pathogenicityPrio = presets.seqvarsquerypresetsvariantprio_set.find(
    (p) => p.sodar_uuid === pq.variantprio,
  )
  return (
    !!genotype &&
    matchesGenotypePreset(query.genotype, genotype) &&
    !!frequency &&
    matchesFrequencyPreset(query.frequency, frequency) &&
    !!phenotypePrio &&
    matchesPhenotypePrioPreset(query.phenotypeprio, phenotypePrio) &&
    !!pathogenicityPrio &&
    matchesPathogenicityPrioPreset(query.variantprio, pathogenicityPrio)
  )
}

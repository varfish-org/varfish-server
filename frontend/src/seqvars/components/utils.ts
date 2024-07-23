import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsQuerySettingsDetails,
} from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import { matchesFrequencyPreset } from './FrequencySelect/utils'
import { matchesGenotypePreset } from './GenotypeSelect/utils'
import { matchesPathogenicityPrioPreset } from './PathogenicityPrioSelect/utils'
import { matchesPhenotypePrioPreset } from './PhenotypePrioSelect/utils'
import { matchesEffectsPreset } from './EffectsSelect/utils'

export const getReferencedPresets = (
  presets: SeqvarsQueryPresetsSetVersionDetails,
  pq: SeqvarsPredefinedQuery,
) =>
  ({
    frequency: presets.seqvarsquerypresetsfrequency_set.find(
      (f) => f.sodar_uuid === pq.frequency,
    ),
    phenotypeprio: presets.seqvarsquerypresetsphenotypeprio_set.find(
      (p) => p.sodar_uuid === pq.phenotypeprio,
    ),
    variantprio: presets.seqvarsquerypresetsvariantprio_set.find(
      (p) => p.sodar_uuid === pq.variantprio,
    ),
    consequence: presets.seqvarsquerypresetsconsequence_set.find(
      (c) => c.sodar_uuid === pq.consequence,
    ),
  }) satisfies Partial<Record<keyof Query, unknown>>

export function matchesPredefinedQuery(
  presets: SeqvarsQueryPresetsSetVersionDetails,
  query: Query,
  pq: SeqvarsPredefinedQuery,
): boolean {
  const genotype = pq.genotype?.choice

  const { frequency, phenotypeprio, variantprio, consequence } =
    getReferencedPresets(presets, pq)
  return (
    !!genotype &&
    matchesGenotypePreset(query.genotype, genotype) &&
    !!frequency &&
    matchesFrequencyPreset(query.frequency, frequency) &&
    !!phenotypeprio &&
    matchesPhenotypePrioPreset(query.phenotypeprio, phenotypeprio) &&
    !!variantprio &&
    matchesPathogenicityPrioPreset(query.variantprio, variantprio) &&
    !!consequence &&
    matchesEffectsPreset(query.consequence, consequence)
  )
}

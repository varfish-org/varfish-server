import isEqual from 'fast-deep-equal/es6'

import { LocalFields } from '@/seqvars/types'
import {
  SeqvarsQueryPresetsConsequence,
  SeqvarsQuerySettingsConsequence,
} from '@varfish-org/varfish-api/lib'

export function matchesEffectsPreset(
  value: LocalFields<SeqvarsQuerySettingsConsequence>,
  preset: SeqvarsQueryPresetsConsequence,
) {
  return isEqual(
    ...([value, preset].map((v) => [
      v.max_distance_to_exon,
      new Set(v.variant_types),
      new Set(v.transcript_types),
      new Set(v.variant_consequences),
    ]) as [unknown, unknown]),
  )
}

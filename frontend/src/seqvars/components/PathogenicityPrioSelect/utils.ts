import isEqual from 'fast-deep-equal'

import { LocalFields } from '@/seqvars/types'
import {
  SeqvarsQueryPresetsVariantPrio,
  SeqvarsQuerySettingsVariantPrio,
} from '@varfish-org/varfish-api/lib'

export function matchesPathogenicityPrioPreset(
  value: LocalFields<SeqvarsQuerySettingsVariantPrio>,
  preset: SeqvarsQueryPresetsVariantPrio,
) {
  return isEqual(
    ...([value, preset].map((v) => [v.variant_prio_enabled, v.services]) as [
      unknown,
      unknown,
    ]),
  )
}

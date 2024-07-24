import isEqual from 'fast-deep-equal/es6'

import { LocalFields } from '@/seqvars/types'
import {
  SeqvarsQueryPresetsQuality,
  SeqvarsQuerySettingsQuality,
} from '@varfish-org/varfish-api/lib'

export function matchesQualityPreset(
  value: LocalFields<SeqvarsQuerySettingsQuality>,
  preset: SeqvarsQueryPresetsQuality,
) {
  if (!value.sample_quality_filters) return true
  return value.sample_quality_filters.every((v) =>
    isEqual(
      ...([v, preset].map((v) => [
        v.filter_active,
        v.max_ad,
        v.min_ab_het,
        v.min_ad,
        v.min_dp_het,
        v.min_dp_hom,
        v.min_gq,
      ]) as [unknown, unknown]),
    ),
  )
}

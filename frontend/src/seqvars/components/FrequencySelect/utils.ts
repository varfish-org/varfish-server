import isEqual from 'fast-deep-equal'

import {
  SeqvarsQueryPresetsFrequency,
  SeqvarsQuerySettingsFrequency,
} from '@varfish-org/varfish-api/lib'
import { LocalFields } from '@/seqvars/types'

export function matchesFrequencyPreset(
  value: LocalFields<SeqvarsQuerySettingsFrequency>,
  preset: SeqvarsQueryPresetsFrequency,
) {
  return isEqual(
    ...([value, preset].map((v) => [
      v.gnomad_exomes,
      v.gnomad_genomes,
      v.gnomad_mitochondrial,
      v.helixmtdb,
      v.inhouse,
    ]) as [unknown, unknown]),
  )
}

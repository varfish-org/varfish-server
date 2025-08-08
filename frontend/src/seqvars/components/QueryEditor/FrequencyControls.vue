<script setup lang="ts">
/**
 * This components only arranges a `FrequencyControlsRow` instances to display
 * frequency editor table but contains no logic itself.
 */
import { SeqvarsQueryDetails } from '@varfish-org/varfish-api/lib'

import FrequencyControlsRow from './FrequencyControlsRow.vue'
import { FrequencyDb } from './lib'
import AbbrHint from './ui/AbbrHint.vue'
import SmallText from './ui/SmallText.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue: SeqvarsQueryDetails
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Database information */
interface DbInfo {
  /** Label for the database. */
  label: string
  /** Key into the `modelValue.settings.frequency` object. */
  db: FrequencyDb
  /** Number of samples in database. */
  size?: number
}

/** The database information to display. */
const DB_INFOS = [
  { label: 'gnomAD exomes', db: 'gnomad_exomes', size: 16 },
  { label: 'gnomAD genomes', db: 'gnomad_genomes', size: 126 },
  { label: 'gnomAD mitochondrial', db: 'gnomad_mtdna', size: 56 },
  { label: 'HelixMTdb', db: 'helixmtdb', size: 197 },
  { label: 'in-house DB', db: 'inhouse', size: undefined },
] as const satisfies DbInfo[]
</script>

<template>
  <div
    style="
      width: fit-content;
      display: grid;
      grid-template-columns: 1fr auto auto auto auto;
      gap: 4px;
      font-size: var(--font-size-sm);
    "
  >
    <SmallText style="grid-column: 2">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal population frequency percentage to allow."
      >
        Max freq.
      </AbbrHint>
    </SmallText>
    <SmallText style="grid-column: span 3; text-align: center">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal het./hom./hemi. count to allow."
      >
        Max count
      </AbbrHint>
    </SmallText>

    <SmallText style="grid-column: 3">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of heterozygous carriers to allow."
      >
        het
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of homozygous alternative carriers to allow."
      >
        hom
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of hemizygous carriers to allow."
      >
        hemi
      </AbbrHint>
    </SmallText>

    <template v-for="{ label, db, size } in DB_INFOS" :key="label">
      <FrequencyControlsRow
        :model-value="modelValue"
        :label="label"
        :db="db"
        :size="size"
      />
    </template>
  </div>
</template>

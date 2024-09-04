<script setup lang="ts">
import {
  ClingenDosageScoreChoice,
  SeqvarsResultRow,
} from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

import AbbrHint from '../QueryEditor/ui/AbbrHint.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The result row item to display the cell for. */
    item: SeqvarsResultRow
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
    /** Which event. */
    event: 'haploinsufficiency' | 'triplosensitivity'
  }>(),
  {
    hintsEnabled: false,
  },
)

const eventLabel = computed<string>(() => {
  if (props.event === 'haploinsufficiency') {
    return 'Haploinsufficiency'
  } else {
    return 'Triplosensitivity'
  }
})

const score = computed<ClingenDosageScoreChoice>(() => {
  if (props.event === 'haploinsufficiency') {
    return (
      props.item?.payload?.variant_annotation?.gene?.constraints?.clingen
        ?.haplo ?? 'no_evidence_available'
    )
  } else {
    return (
      props.item?.payload?.variant_annotation?.gene?.constraints?.clingen
        ?.triplo ?? 'no_evidence_available'
    )
  }
})

const LABELS: { [ClingenDosageScoreChoice]: string } = {
  sufficient_evidence_available: 'Sufficient Evidence',
  some_evidence_available: 'Emerging Evidence',
  little_evidence: 'Little Evidence',
  no_evidence_available: 'No Evidence',
  recessive: 'Autosomal Recessive',
  unlikely: 'Sensitivity Unlikely',
}

const SCORES: { [ClingenDosageScoreChoice]: number } = {
  sufficient_evidence_available: 3,
  some_evidence_available: 2,
  little_evidence: 1,
  no_evidence_available: 0,
  recessive: 30,
  unlikely: 40,
}

const COLORS: { [ClingenDosageScoreChoice]: string } = {
  sufficient_evidence_available: 'red',
  some_evidence_available: 'orange',
  little_evidence: 'yellow',
  no_evidence_available: 'grey-darken-3',
  recessive: 'blue',
  unlikely: 'green',
}
</script>

<template>
  <AbbrHint
    :hint="`${SCORES[score]} (${LABELS[score]})`"
    :hints-enabled="hintsEnabled"
  >
    <v-chip variant="tonal" :color="COLORS[score]">
      {{ LABELS[score] }}
    </v-chip>
  </AbbrHint>
</template>

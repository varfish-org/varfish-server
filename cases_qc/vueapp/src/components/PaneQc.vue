<script setup lang="ts">
import { computed } from 'vue'

import ReadStatsCard from '@cases_qc/components/PaneQc/ReadStatsCard.vue'
import { type VarfishStats } from '@cases_qc/api/types'

export interface Props {
  stats?: VarfishStats | null
}
const props = withDefaults(defineProps<Props>(), {
  stats: null,
})

/** All sample names from `props.stats.readstats`, ordered lexicographically */
const sampleNames = computed<string[]>(() => {
  if (props.stats?.readstats) {
    const unsorted = props.stats.readstats.map((s) => s.sample)
    unsorted.sort()
    return unsorted
  } else {
    return []
  }
})
</script>

<template>
  <div class="container-fluid">
    <div class="row" v-if="!stats || !sampleNames.length">
      <div class="col text-center text-muted font-italic">
        No QC data available.
      </div>
    </div>
    <ReadStatsCard :sample-names="sampleNames" :read-stats="stats?.readstats" />
  </div>
</template>

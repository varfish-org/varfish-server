<script setup lang="ts">
import { computed } from 'vue'

import AlignmentsSummaryCard from '@cases_qc/components/PaneQc/AlignmentsSummaryCard.vue'
import AlignmentsCoverageCard from '@cases_qc/components/PaneQc/AlignmentsCoverageCard.vue'
import AlignmentsFragmentHistCard from '@cases_qc/components/PaneQc/AlignmentsFragmentHistCard.vue'
import ReadsCard from '@cases_qc/components/PaneQc/ReadsCard.vue'
import SeqvarCard from '@cases_qc/components/PaneQc/SeqvarCard.vue'
import StrucvarCard from '@cases_qc/components/PaneQc/StrucvarCard.vue'
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
    <div class="row" v-else>
      <ReadsCard :sample-names="sampleNames" :read-stats="stats?.readstats" />
      <AlignmentsSummaryCard
        :sample-names="sampleNames"
        :alignment-stats="stats?.alignmentstats"
      />
      <AlignmentsCoverageCard
        :sample-names="sampleNames"
        :alignment-stats="stats?.alignmentstats"
      />
      <AlignmentsFragmentHistCard
        :sample-names="sampleNames"
        :alignment-stats="stats?.alignmentstats"
      />
      <SeqvarCard
        :sample-names="sampleNames"
        :seqvar-stats="stats?.seqvarstats"
      />
      <StrucvarCard
        :sample-names="sampleNames"
        :strucvar-stats="stats?.strucvarstats"
      />
    </div>
  </div>
</template>

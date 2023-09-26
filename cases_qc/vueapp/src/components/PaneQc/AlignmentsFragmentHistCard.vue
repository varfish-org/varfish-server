<script setup lang="ts">
/** Display summary read statistics for all samples in a table.
 */
import { type SampleAlignmentStats } from '@cases_qc/api/types'
import SimpleCard from '@varfish/components/SimpleCard.vue'
import DistDensPlot from '@cases_qc/components/DistDensPlot.vue'
import { computed } from 'vue'

export interface Props {
  sampleNames: string[]
  alignmentStats?: SampleAlignmentStats[]
}
const props = defineProps<Props>()

/** Per-sample (fragment length density) statistics to display in this card */
interface PlotDataset {
  label: string
  keys: number[]
  values: number[]
}

/** Row-wise read sample statistics, samples ordreed as in `sampleNames.value` */
const datasets = computed<PlotDataset[]>(() => {
  const theNames = props.sampleNames
  const result: { [key: string]: PlotDataset } = {}

  for (const stats of props.alignmentStats ?? []) {
    const entry: PlotDataset = {
      label: stats.sample,
      keys: [],
      values: [],
    }
    for (const [key, value] of stats.insert_size_stats.insert_size_histogram) {
      entry.keys.push(key)
      entry.values.push(value)
    }
    result[stats.sample] = entry
  }

  return theNames.map((name) => result[name]).filter((x) => x)
})
</script>

<template>
  <SimpleCard id="alignmentstats-summary" title="Library Fragment Lengths" class="col-6 pr-0">
    <DistDensPlot
      title="insert size distribution"
      :datasets="datasets"
      x-label="insert size (bp)"
      y-label="frequency"
      :x-min="0"
      :x-max="1000"
    />
  </SimpleCard>
</template>

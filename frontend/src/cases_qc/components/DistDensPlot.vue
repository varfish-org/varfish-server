<script setup lang="ts">
import { computed } from 'vue'

import VegaPlot from '@/varfish/components/VegaPlot.vue'

export interface Dataset {
  label: string
  keys: number[]
  values: number[]
}

const props = withDefaults(
  defineProps<{
    datasets: Dataset[]
    title?: string
    xLabel?: string
    yLabel?: string
    xMin?: number | null
    xMax?: number | null
  }>(),
  {
    xMin: null,
    xMax: null,
  },
)

interface DataForVegaLite {
  key: number
  value: number
  label: string
}

const vegaData = computed<DataForVegaLite[]>(() => {
  const result: DataForVegaLite[] = []
  for (const dataset of props.datasets) {
    for (let i = 0; i < dataset.keys.length; ++i) {
      if (props.xMin !== null && dataset.keys[i] < props.xMin) {
        continue
      } else if (props.xMax !== null && dataset.keys[i] > props.xMax) {
        continue
      }
      {
        result.push({
          key: dataset.keys[i],
          value: dataset.values[i],
          label: dataset.label,
        })
      }
    }
  }
  return result
})

const vegaEncoding = {
  x: {
    field: 'key',
    type: 'quantitative',
    title: props?.xLabel,
    axis: { domain: false, grid: false, ticks: false },
  },
  y: {
    field: 'value',
    type: 'quantitative',
    title: props?.yLabel,
    axis: { domain: false, grid: false, ticks: false },
  },
  color: {
    field: 'label',
    type: 'nominal',
  },
}
</script>

<template>
  <VegaPlot
    :title="props.title"
    :data-values="vegaData"
    :encoding="vegaEncoding"
    :width="400"
    :height="400"
    :mark="{ type: 'line' }"
    renderer="svg"
  />
</template>

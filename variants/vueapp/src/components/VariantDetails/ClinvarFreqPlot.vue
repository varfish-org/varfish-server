<script setup lang="ts">
import * as vega from 'vega'
import { computed, ref } from 'vue'

import VegaPlot from '@varfish/components/VegaPlot.vue'

const coarseClinsigLabels = ['benign', 'uncertain', 'pathogenic']

const bucketLabels = [
  'no frequency',
  '<0.00001',
  '<0.00025',
  '<0.0005',
  '<0.0001',
  '<0.00025',
  '<0.0005',
  '<0.001',
  '<0.0025',
  '<0.005',
  '<0.01',
  '<0.025',
  '<0.05',
  '<0.1',
  '<0.25',
  '<0.5',
  '<1.0',
]

export interface CountsRecord {
  /** Coarse clinical significance ID */
  coarse_clinsig: number
  /** Counts per bucket */
  counts: number[]
}

export interface Props {
  /** Gene symbol */
  geneSymbol: string
  /** Expression records */
  perFreqCounts: CountsRecord[]
}

const props = withDefaults(defineProps<Props>(), {})

const vegaData = computed(() => {
  const values = []
  for (const record of props?.perFreqCounts || []) {
    for (let i = 0; i < record.counts.length; i++) {
      if (record.counts[i] > 0) {
        values.push({
          coarseClinsig: coarseClinsigLabels[record.coarse_clinsig],
          coarseClinsigNo: record.coarse_clinsig,
          freqBucket: bucketLabels[i],
          freqBucketNo: i,
          value: record.counts[i],
        })
      }
    }
  }
  if (values.length) {
    return values
  } else {
    return null
  }
})

const vegaLayer = [
  {
    mark: { type: 'bar', tooltip: true },
  },
  {
    mark: {
      type: 'text',
      align: 'center',
      baseline: 'middle',
      dy: -10,
    },
    encoding: {
      text: { field: 'value', type: 'quantitative', fontSize: 8 },
    },
  },
]

const vegaEncoding = {
  x: {
    field: 'freqBucket',
    title: 'population frequency',
    type: 'nominal',
    sort: bucketLabels,
    axis: { labelAngle: 45 },
  },
  y: {
    field: 'value',
    scale: { type: 'log' },
    title: 'variant count',
    axis: {
      grid: false,
      tickExtra: false,
    },
  },
  xOffset: {
    field: 'coarseClinsig',
    type: 'nominal',
    sort: coarseClinsigLabels,
  },
  color: {
    field: 'coarseClinsig',
    title: 'clinical sig.',
    type: 'nominal',
    sort: coarseClinsigLabels,
    scale: {
      domain: coarseClinsigLabels,
      range: ['#5d9936', '#f5c964', '#b05454'],
    },
  },
}

/** Ref to the VegaPlot (for testing). */
const vegaPlotRef = ref(null)
</script>

<template>
  <figure class="figure border rounded pl-2 pt-2 mr-3 w-100 col">
    <figcaption class="figure-caption text-center">
      Population frequency of ClinVar variants
    </figcaption>
    <VegaPlot
      :data-values="vegaData"
      :encoding="vegaEncoding"
      :mark="false"
      :layer="vegaLayer"
      :width="800"
      :height="300"
      renderer="svg"
    />
  </figure>
</template>

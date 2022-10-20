<script setup>
import { computed, ref } from 'vue'

import VegaPlot from './VegaPlot.vue'
import { displayName } from '@varfish/helpers.js'

/** Define the props. */
const props = defineProps({
  variantStats: Object,
  renderer: String,
})

const vegaMark = {
  type: 'bar',
}

const vegaParams = [
  {
    name: 'grid',
    select: 'interval',
    bind: 'scales',
  },
]

const variantTypes = Object.freeze(['SNV', 'InDel', 'MNV'])

const vegaEncoding = {
  x: {
    field: 'variantType',
    title: 'variant type',
    type: 'nominal',
    scale: {
      domain: variantTypes,
    },
    axis: {
      labelAngle: 0,
    },
  },
  y: {
    field: 'variantCount',
    title: 'variant count',
    type: 'quantitative',
  },
  xOffset: {
    field: 'sampleName',
  },
  color: {
    field: 'sampleName',
    title: 'sample name',
  },
  tooltip: {
    field: 'variantCountLabel',
    type: 'nominal',
  },
}

const vegaData = computed(() => {
  if (!props.variantStats) {
    return []
  } else {
    const result = []
    for (const [sampleName, stats] of Object.entries(props.variantStats)) {
      for (const variantType of variantTypes) {
        const variantCount =
          stats['ontarget_' + variantType.toLowerCase() + 's']
        const variantCountLabel = variantCount.toLocaleString('en-US')
        result.push({
          sampleName: displayName(sampleName),
          variantType,
          variantCount,
          variantCountLabel,
        })
      }
    }
    return result
  }
})

/** Ref to the VegaPlot (for testing). */
const vegaPlotRef = ref(null)

/** Return vegaPlot. */
const getVegaPlot = () => vegaPlotRef.value

/** Expose getVegaPlot() for tests. */
defineExpose({
  getVegaPlot,
})
</script>

<template>
  <figure class="figure border rounded pl-2 pt-2 mr-3">
    <figcaption class="figure-caption text-center">
      Histograms with variant type counts for each sample
    </figcaption>
    <VegaPlot
      ref="vegaPlotRef"
      :width="350"
      :height="300"
      description="variant types"
      data-name="variantTypes"
      :data-values="vegaData"
      :mark="vegaMark"
      :params="vegaParams"
      :encoding="vegaEncoding"
      :renderer="props.renderer"
    />
  </figure>
</template>

<script setup>
import { computed, ref } from 'vue'

import VegaPlot from '@/varfish/components/VegaPlot.vue'
import { displayName } from '@/varfish/helpers'

/** Define the props. */
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  variantStats: Object,
  // eslint-disable-next-line vue/require-default-prop
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

const vegaEncoding = {
  x: {
    field: 'variantEffect',
    title: 'variant effect',
    type: 'nominal',
    axis: {
      labelAngle: 35,
    },
  },
  y: {
    field: 'variantCount',
    title: 'variant count',
    type: 'quantitative',
    scale: { type: 'log' },
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
      for (const [variantEffect, variantCount] of Object.entries(
        stats.ontarget_effect_counts,
      )) {
        const variantCountLabel = variantCount.toLocaleString('en-US')
        if (variantCount > 0) {
          result.push({
            sampleName: displayName(sampleName),
            variantEffect,
            variantCount,
            variantCountLabel,
          })
        }
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
      Histograms with variant effect counts for each sample
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

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

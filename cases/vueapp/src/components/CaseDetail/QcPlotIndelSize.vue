<script setup>
import { computed, ref } from 'vue'

import VegaPlot from '@varfish/components/VegaPlot.vue'
import { displayName } from '@varfish/helpers'

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

const indelSizeToLabel = Object.freeze({
  '-10': '≤10',
  '-9': '-9',
  '-8': '-8',
  '-7': '-7',
  '-6': '-6',
  '-5': '-5',
  '-4': '-4',
  '-3': '-3',
  '-2': '-2',
  '-1': '-1',
  0: '0',
  1: '1',
  2: '2',
  3: '3',
  4: '4',
  5: '5',
  6: '6',
  7: '7',
  8: '8',
  9: '9',
  10: '≥10',
})

const indelSizeLabels = Object.freeze([
  '≤10',
  '-9',
  '-8',
  '-7',
  '-6',
  '-5',
  '-4',
  '-3',
  '-2',
  '-1',
  '0',
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '≥10',
])

const vegaEncoding = {
  x: {
    field: 'indelSize',
    title: 'indel size',
    type: 'nominal',
    scale: {
      domain: Object.values(indelSizeLabels),
    },
    axis: {
      labelAngle: 0,
    },
  },
  y: {
    field: 'count',
    title: 'count',
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
    field: 'countLabel',
    type: 'nominal',
  },
}

const vegaData = computed(() => {
  if (!props.variantStats) {
    return []
  } else {
    const result = []
    for (const [sampleName, stats] of Object.entries(props.variantStats)) {
      const indelSizes = stats.ontarget_indel_sizes
      const counters = {}
      for (const [indelSize, count] of Object.entries(indelSizes)) {
        if (indelSize <= -10) {
          indelSize = -10
        } else if (indelSize >= 10) {
          indelSize = 10
        }
        const indelSizeLabel = indelSizeToLabel[String(indelSize)]
        counters[indelSizeLabel] = (counters[indelSizeLabel] ?? 0) + count
      }

      for (const [indelSize, count] of Object.entries(counters)) {
        const countLabel = count.toLocaleString('en-US')
        result.push({
          sampleName: displayName(sampleName),
          indelSize,
          count,
          countLabel,
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
      Histograms with indel sizes for each sample
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

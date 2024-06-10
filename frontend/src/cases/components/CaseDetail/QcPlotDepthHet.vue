<script setup>
import * as vega from 'vega'
import { computed, ref } from 'vue'

import VegaPlot from '@/varfish/components/VegaPlot.vue'

/** Define the props. */
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  hetRatioQuantiles: Array,
  // eslint-disable-next-line vue/require-default-prop
  dpQuantiles: Array,
  // eslint-disable-next-line vue/require-default-prop
  dpHetData: Array,
  // eslint-disable-next-line vue/require-default-prop
  renderer: String,
})

vega.scheme('outlierOutlierOk', ['#ff6767', '#ce3bff', '#71a571'])

const depthHetMark = {
  type: 'circle',
  size: 100,
}
const depthHetParams = [
  {
    name: 'grid',
    select: 'interval',
    bind: 'scales',
  },
]
const depthHetEncoding = {
  x: {
    field: 'median depth',
    type: 'quantitative',
  },
  y: {
    field: 'het genotype ratio',
    type: 'quantitative',
  },
  color: {
    field: 'status',
    type: 'nominal',
    scale: {
      scheme: 'outlierOutlierOk',
      domain: ['depth outlier', 'het. outlier', 'OK'],
    },
  },
  tooltip: {
    field: 'label',
    type: 'nominal',
  },
}
const depthHetData = computed(() => {
  if (!props.hetRatioQuantiles || !props.dpQuantiles || !props.dpHetData) {
    return []
  } else {
    const dpQuantiles = props.dpQuantiles
    const dpIqr = dpQuantiles[3] - dpQuantiles[1]
    const hetRatioQuantiles = props.hetRatioQuantiles
    const hetRatioIqr = hetRatioQuantiles[3] - hetRatioQuantiles[1]

    const result = []

    for (const data of props.dpHetData) {
      let status
      if (Math.abs(dpQuantiles[2] - data.x) > 3 * dpIqr) {
        status = 'depth outlier'
      } else if (Math.abs(hetRatioQuantiles[2] - data.y) > 3 * hetRatioIqr) {
        status = 'het. outlier'
      } else {
        status = 'OK'
      }

      result.push({
        'median depth': data.x,
        'het genotype ratio': data.y,
        status: status,
        label: data.sample,
      })
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
      Plot of heterozygous genotype ratio to depth of coverage
    </figcaption>
    <VegaPlot
      ref="vegaPlotRef"
      :width="400"
      :height="300"
      description="depthHet"
      data-name="depthHet"
      :data-values="depthHetData"
      :mark="depthHetMark"
      :params="depthHetParams"
      :encoding="depthHetEncoding"
      :renderer="props.renderer"
    />
  </figure>
</template>

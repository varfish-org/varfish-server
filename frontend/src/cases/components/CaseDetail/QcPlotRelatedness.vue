<script setup>
import { computed, ref } from 'vue'

import VegaPlot from '@/varfish/components/VegaPlot.vue'

/** Define the props. */
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  renderer: String,
  // eslint-disable-next-line vue/require-default-prop
  relData: Object,
})

const relatednessMark = {
  type: 'circle',
  size: 100,
}
const relatednessParams = [
  {
    name: 'grid',
    select: 'interval',
    bind: 'scales',
  },
]
const relatednessEncoding = {
  x: {
    field: 'IBS0',
    type: 'quantitative',
  },
  y: {
    field: 'relatedness',
    type: 'quantitative',
  },
  color: {
    field: 'relationship',
    type: 'nominal',
    scale: {
      scheme: 'set1',
      domain: ['parent-child', 'siblings', 'other'],
    },
  },
  tooltip: {
    field: 'label',
    type: 'nominal',
  },
}

const relatednessData = computed(() => {
  const getRel = (parentChild, sibSib) => {
    if (parentChild) {
      return 'parent-child'
    } else if (sibSib) {
      return 'siblings'
    } else {
      return 'other'
    }
  }

  if (!props.relData) {
    return []
  } else {
    return props.relData.map(
      ({ ibs0, parentChild, rel, sample0, sample1, sibSib }) => {
        return {
          IBS0: ibs0,
          relatedness: rel,
          label: `${sample0} - ${sample1}`,
          relationship: getRel(parentChild, sibSib),
        }
      },
    )
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
      Plot of relatedness coefficient vs. IBS0 (inherited-by-no-shared allele)
    </figcaption>
    <VegaPlot
      ref="vegaPlotRef"
      :width="400"
      :height="300"
      description="Relatedness"
      data-name="relatedness"
      :data-values="relatednessData"
      :mark="relatednessMark"
      :params="relatednessParams"
      :encoding="relatednessEncoding"
      :renderer="props.renderer"
    />
  </figure>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

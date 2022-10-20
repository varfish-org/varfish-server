<script setup>
import * as vega from 'vega'
import { computed, ref } from 'vue'

import VegaPlot from './VegaPlot.vue'
import { displayName } from '@varfish/helpers.js'

/** Define the props. */
const props = defineProps({
  pedigree: Array,
  sexErrors: Object,
  chrXHetHomRatio: Object,
  renderer: String,
})

vega.scheme('okUnknownError', ['#71a571', '#7E7E7EFF', '#ff6767'])

const chrXRatioMark = {
  type: 'circle',
  size: 100,
}
const chrXRatioParams = [
  {
    name: 'grid',
    select: 'interval',
    bind: 'scales',
  },
]
const chrXRatioEncoding = {
  x: {
    field: 'sex from pedigree',
    type: 'nominal',
    scale: {
      domain: ['male', 'unknown', 'female'],
    },
    axis: {
      labelAngle: 0,
    },
  },
  xOffset: { field: 'offset', scale: { domain: [0, 1] }, type: 'quantitative' },
  y: {
    field: 'het hom alt ratio',
    title: 'het. / hom. alt. ratio',
    type: 'quantitative',
  },
  color: {
    field: 'status',
    type: 'nominal',
    scale: {
      scheme: 'okUnknownError',
      domain: ['OK', 'unknown', 'error'],
    },
  },
  tooltip: {
    field: 'label',
    type: 'nominal',
  },
}

const chrXRatioTransform = [{ calculate: 'random()', as: 'offset' }]

const chrXRatioData = computed(() => {
  const SEX = Object.freeze({
    0: 'unknown',
    1: 'male',
    2: 'female',
  })

  if (!props.pedigree || !props.sexErrors || !props.chrXHetHomRatio) {
    return []
  } else {
    const ped = props.pedigree
    const sexErrors = props.sexErrors
    const chrXHetHomRatio = props.chrXHetHomRatio

    return ped
      .filter((line) => line.has_gt_entries)
      .map((line) => {
        let status
        if (line.sex === 0) {
          status = 'unknown'
        } else if (sexErrors && (line.patient ?? line.name) in sexErrors) {
          status = 'error'
        } else {
          status = 'OK'
        }

        return {
          'sex from pedigree': SEX[line.sex],
          'het hom alt ratio': chrXHetHomRatio[line.patient ?? line.name],
          status,
          label: displayName(line.patient ?? line.name),
        }
      })
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
      Plot of het. call ratio on chrX (outside of PAR)
    </figcaption>
    <VegaPlot
      ref="vegaPlotRef"
      :width="400"
      :height="300"
      description="chrXRatio"
      data-name="chrXRatio"
      :data-values="chrXRatioData"
      :mark="chrXRatioMark"
      :params="chrXRatioParams"
      :encoding="chrXRatioEncoding"
      :transform="chrXRatioTransform"
      :renderer="props.renderer"
    />
  </figure>
</template>

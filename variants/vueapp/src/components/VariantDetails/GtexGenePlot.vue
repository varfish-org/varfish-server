<script setup lang="ts">
import * as vega from 'vega'
import { computed, ref } from 'vue'

import VegaPlot from '@varfish/components/VegaPlot.vue'

export interface ExpressionRecord {
  /** Tissue id */
  tissue: number
  /** Detailed tissue id */
  tissue_detailed: number
  /** TPM quantiles (0, 0.25, 0.5, 0.75, 1.0) */
  tpms: number[]
}

export interface Props {
  /** Gene symbol */
  geneSymbol: string
  /** Expression records */
  expressionRecords: ExpressionRecord[]
}

const props = withDefaults(defineProps<Props>(), {})

const tissueLabels = [
  'Adipose Tissue',
  'Adrenal Gland',
  'Bladder',
  'Blood',
  'Blood Vessel',
  'Bone Marrow',
  'Brain',
  'Breast',
  'Cervix Uteri',
  'Colon',
  'Esophagus',
  'Fallopian Tube',
  'Heart',
  'Kidney',
  'Liver',
  'Lung',
  'Muscle',
  'Nerve',
  'Ovary',
  'Pancreas',
  'Pituitary',
  'Prostate',
  'Salivary Gland',
  'Skin',
  'Small Intestine',
  'Spleen',
  'Stomach',
  'Testis',
  'Thyroid',
  'Uterus',
  'Vagina',
]

const tissueDetailedLabels = [
  'Adipose - Subcutaneous',
  'Adipose - Visceral (Omentum)',
  'Adrenal Gland',
  'Artery - Aorta',
  'Artery - Coronary',
  'Artery - Tibial',
  'Bladder',
  'Brain - Amygdala',
  'Brain - Anterior cingulate cortex (BA24)',
  'Brain - Caudate (basal ganglia)',
  'Brain - Cerebellar Hemisphere',
  'Brain - Cerebellum',
  'Brain - Cortex',
  'Brain - Frontal Cortex (BA9)',
  'Brain - Hippocampus',
  'Brain - Hypothalamus',
  'Brain - Nucleus accumbens (basal ganglia)',
  'Brain - Putamen (basal ganglia)',
  'Brain - Spinal cord (cervical c-1)',
  'Brain - Substantia nigra',
  'Breast - Mammary Tissue',
  'Cells - Cultured fibroblasts',
  'Cells - EBV-transformed lymphocytes',
  'Cells - Leukemia cell line (CML)',
  'Cervix - Ectocervix',
  'Cervix - Endocervix',
  'Colon - Sigmoid',
  'Colon - Transverse',
  'Esophagus - Gastroesophageal Junction',
  'Esophagus - Mucosa',
  'Esophagus - Muscularis',
  'Fallopian Tube',
  'Heart - Atrial Appendage',
  'Heart - Left Ventricle',
  'Kidney - Cortex',
  'Kidney - Medulla',
  'Liver',
  'Lung',
  'Minor Salivary Gland',
  'Muscle - Skeletal',
  'Nerve - Tibial',
  'Ovary',
  'Pancreas',
  'Pituitary',
  'Prostate',
  'Salivary Gland',
  'Skin - Not Sun Exposed (Suprapubic)',
  'Skin - Sun Exposed (Lower leg)',
  'Small Intestine - Terminal Ileum',
  'Spleen',
  'Stomach',
  'Testis',
  'Thyroid',
  'Uterus',
  'Vagina',
  'Whole Blood',
]

const vegaData = computed(() => {
  return props?.expressionRecords?.map((record) => ({
    tissue: tissueLabels[record.tissue],
    tissueDetailed: tissueDetailedLabels[record.tissue_detailed],
    lower: record.tpms[0],
    q1: record.tpms[1],
    median: record.tpms[2],
    q3: record.tpms[3],
    upper: record.tpms[4],
  }))
})

const vegaEncoding = {
  x: {
    field: 'tissueDetailed',
    type: 'nominal',
    title: null,
    axis: { labelAngle: 45 },
  },
}

const vegaLayer = [
  {
    mark: { type: 'rule', tooltip: { content: 'data' } },
    encoding: {
      y: {
        field: 'lower',
        type: 'quantitative',
        scale: { zero: false },
        title: 'TPM',
      },
      y2: { field: 'upper' },
    },
  },
  {
    mark: { type: 'bar', size: 14, tooltip: { content: 'data' } },
    encoding: {
      y: { field: 'q1', type: 'quantitative' },
      y2: { field: 'q3' },
      color: { field: 'tissue', type: 'nominal', legend: null },
    },
  },
  {
    mark: {
      type: 'tick',
      color: 'white',
      size: 14,
      tooltip: { content: 'data' },
    },
    encoding: {
      y: { field: 'median', type: 'quantitative' },
    },
  },
]

/** Ref to the VegaPlot (for testing). */
const vegaPlotRef = ref(null)
</script>

<template>
  <figure class="figure border rounded pl-2 pt-2 mr-3 w-100 col">
    <figcaption class="figure-caption text-center">
      Bulk tissue gene expression for gene {{ props.geneSymbol }}
    </figcaption>
    <VegaPlot
      :data-values="vegaData"
      :encoding="vegaEncoding"
      :layer="vegaLayer"
      :mark="false"
      :width="1000"
      :height="300"
      renderer="svg"
    />
  </figure>
</template>

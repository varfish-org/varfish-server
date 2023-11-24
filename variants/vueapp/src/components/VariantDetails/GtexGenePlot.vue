<script setup lang="ts">
import * as vega from 'vega'
import { computed, ref } from 'vue'

import VegaPlot from '@varfish/components/VegaPlot.vue'

export interface ExpressionRecord {
  /** Tissue id */
  tissue: number
  /** Detailed tissue id */
  tissueDetailed: number
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

const tissueLabels: { [key: string]: string } = {
  GTEX_TISSUE_UNKNOWN: 'Unknown',
  GTEX_TISSUE_ADIPOSE_TISSUE: 'Adipose Tissue',
  GTEX_TISSUE_ADRENAL_GLAND: 'Adrenal Gland',
  GTEX_TISSUE_BLOOD: 'Blood',
  GTEX_TISSUE_BLOOD_VESSEL: 'Blood Vessel',
  GTEX_TISSUE_BONE_MARROW: 'Bone Marrow',
  GTEX_TISSUE_BRAIN: 'Brain',
  GTEX_TISSUE_BREAST: 'Breast',
  GTEX_TISSUE_CERVIX_UTERI: 'Cervix Uteri',
  GTEX_TISSUE_COLON: 'Colon',
  GTEX_TISSUE_ESOPHAGUS: 'Esophagus',
  GTEX_TISSUE_FALLOPIAN_TUBE: 'Fallopian Tube',
  GTEX_TISSUE_HEART: 'Heart',
  GTEX_TISSUE_KIDNEY: 'Kidney',
  GTEX_TISSUE_LIVER: 'Liver',
  GTEX_TISSUE_LUNG: 'Lung',
  GTEX_TISSUE_MUSCLE: 'Muscle',
  GTEX_TISSUE_NERVE: 'Nerve',
  GTEX_TISSUE_OVARY: 'Ovary',
  GTEX_TISSUE_PANCREAS: 'Pancreas',
  GTEX_TISSUE_PITUITARY: 'Pituitary',
  GTEX_TISSUE_PROSTATE: 'Prostate',
  GTEX_TISSUE_SALIVARY_GLAND: 'Salivary Gland',
  GTEX_TISSUE_SKIN: 'Skin',
  GTEX_TISSUE_SMALL_INTESTINE: 'Small Intestine',
  GTEX_TISSUE_SPLEEN: 'Spleen',
  GTEX_TISSUE_STOMACH: 'Stomach',
  GTEX_TISSUE_TESTIS: 'Testis',
  GTEX_TISSUE_THYROID: 'Thyroid',
  GTEX_TISSUE_UTERUS: 'Uterus',
  GTEX_TISSUE_VAGINA: 'Vagina',
}

const tissueDetailedLabels: { [key: string]: string } = {
  GTEX_TISSUE_DETAILED_UNKNOWN: 'Unknown',
  GTEX_TISSUE_DETAILED_ADIPOSE_SUBCUTANEOUS: 'Adipose - Subcutaneous',
  GTEX_TISSUE_DETAILED_ADIPOSE_VISCERAL_OMENTUM: 'Adipose - Visceral (Omentum)',
  GTEX_TISSUE_DETAILED_ADRENAL_GLAND: 'Adrenal Gland',
  GTEX_TISSUE_DETAILED_ARTERY_AORTA: 'Artery - Aorta',
  GTEX_TISSUE_DETAILED_ARTERY_CORONARY: 'Artery - Coronary',
  GTEX_TISSUE_DETAILED_ARTERY_TIBIAL: 'Artery - Tibial',
  GTEX_TISSUE_DETAILED_BLADDER: 'Bladder',
  GTEX_TISSUE_DETAILED_BRAIN_AMYGDALA: 'Brain - Amygdala',
  GTEX_TISSUE_DETAILED_BRAIN_ANTERIOR_CINGULATE_CORTEX:
    'Brain - Anterior cingulate cortex (BA24)',
  GTEX_TISSUE_DETAILED_BRAIN_CAUDATE_BASAL_GANGLIA:
    'Brain - Caudate (basal ganglia)',
  GTEX_TISSUE_DETAILED_BRAIN_CEREBELLAR_HEMISPHERE:
    'Brain - Cerebellar Hemisphere',
  GTEX_TISSUE_DETAILED_BRAIN_CEREBELLUM: 'Brain - Cerebellum',
  GTEX_TISSUE_DETAILED_BRAIN_CORTEX: 'Brain - Cortex',
  GTEX_TISSUE_DETAILED_BRAIN_FRONTAL_CORTEX: 'Brain - Frontal Cortex (BA9)',
  GTEX_TISSUE_DETAILED_BRAIN_HIPPOCAMPUS: 'Brain - Hippocampus',
  GTEX_TISSUE_DETAILED_BRAIN_HYPOTHALAMUS: 'Brain - Hypothalamus',
  GTEX_TISSUE_DETAILED_BRAIN_NUCLEUS_ACCUMBENS:
    'Brain - Nucleus accumbens (basal ganglia)',
  GTEX_TISSUE_DETAILED_BRAIN_PUTAMEN_BASAL_GANGLIA:
    'Brain - Putamen (basal ganglia)',
  GTEX_TISSUE_DETAILED_BRAIN_SPINAL_CORD: 'Brain - Spinal cord (cervical c-1)',
  GTEX_TISSUE_DETAILED_BRAIN_SUBSTANTIA_NIGRA: 'Brain - Substantia nigra',
  GTEX_TISSUE_DETAILED_BREAST_MAMMARY_TISSUE: 'Breast - Mammary Tissue',
  GTEX_TISSUE_DETAILED_CELLS_CULTURED_FIBROBLASTS:
    'Cells - Cultured fibroblasts',
  GTEX_TISSUE_DETAILED_CELLS_EBV_TRANSFORMED_LYMPHOCYTES:
    'Cells - EBV-transformed lymphocytes',
  GTEX_TISSUE_DETAILED_CELLS_LEUKEMIA_CELL_LINE:
    'Cells - Leukemia cell line (CML)',
  GTEX_TISSUE_DETAILED_CERVIX_ECTOCERVIX: 'Cervix - Ectocervix',
  GTEX_TISSUE_DETAILED_CERVIX_ENDOCERVIX: 'Cervix - Endocervix',
  GTEX_TISSUE_DETAILED_COLON_SIGMOID: 'Colon - Sigmoid',
  GTEX_TISSUE_DETAILED_COLON_TRANSVERSE: 'Colon - Transverse',
  GTEX_TISSUE_DETAILED_ESOPHAGUS_GASTROESOPHAGEAL_JUNCTION:
    'Esophagus - Gastroesophageal Junction',
  GTEX_TISSUE_DETAILED_ESOPHAGUS_MUCOSA: 'Esophagus - Mucosa',
  GTEX_TISSUE_DETAILED_ESOPHAGUS_MUSCULARIS: 'Esophagus - Muscularis',
  GTEX_TISSUE_DETAILED_FALLOPIAN_TUBE: 'Fallopian Tube',
  GTEX_TISSUE_DETAILED_HEART_ATRIAL_APPENDAGE: 'Heart - Atrial Appendage',
  GTEX_TISSUE_DETAILED_HEART_LEFT_VENTRICLE: 'Heart - Left Ventricle',
  GTEX_TISSUE_DETAILED_KIDNEY_CORTEX: 'Kidney - Cortex',
  GTEX_TISSUE_DETAILED_KIDNEY_MEDULLA: 'Kidney - Medulla',
  GTEX_TISSUE_DETAILED_LIVER: 'Liver',
  GTEX_TISSUE_DETAILED_LUNG: 'Lung',
  GTEX_TISSUE_DETAILED_MINOR_SALIVARY_GLAND: 'Minor Salivary Gland',
  GTEX_TISSUE_DETAILED_MUSCLE_SKELETAL: 'Muscle - Skeletal',
  GTEX_TISSUE_DETAILED_NERVE_TIBIAL: 'Nerve - Tibial',
  GTEX_TISSUE_DETAILED_OVARY: 'Ovary',
  GTEX_TISSUE_DETAILED_PANCREAS: 'Pancreas',
  GTEX_TISSUE_DETAILED_PITUITARY: 'Pituitary',
  GTEX_TISSUE_DETAILED_PROSTATE: 'Prostate',
  GTEX_TISSUE_DETAILED_SALIVARY_GLAND: 'Salivary Gland',
  GTEX_TISSUE_DETAILED_SKIN_NOT_SUN_EXPOSED_SUPRAPUBIC:
    'Skin - Not Sun Exposed (Suprapubic)',
  GTEX_TISSUE_DETAILED_SKIN_SUN_EXPOSED_LOWER_LEG:
    'Skin - Sun Exposed (Lower leg)',
  GTEX_TISSUE_DETAILED_SMALL_INTESTINE_TERMINAL_ILEUM:
    'Small Intestine - Terminal Ileum',
  GTEX_TISSUE_DETAILED_SPLEEN: 'Spleen',
  GTEX_TISSUE_DETAILED_STOMACH: 'Stomach',
  GTEX_TISSUE_DETAILED_TESTIS: 'Testis',
  GTEX_TISSUE_DETAILED_THYROID: 'Thyroid',
  GTEX_TISSUE_DETAILED_UTERUS: 'Uterus',
  GTEX_TISSUE_DETAILED_VAGINA: 'Vagina',
  GTEX_TISSUE_DETAILED_WHOLE_BLOOD: 'Whole Blood',
}

const vegaData = computed(() => {
  return props?.expressionRecords?.map((record) => ({
    tissue: tissueLabels[record.tissue],
    tissueDetailed: tissueDetailedLabels[record.tissueDetailed],
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

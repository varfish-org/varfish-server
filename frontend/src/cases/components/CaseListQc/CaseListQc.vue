<script setup>
import { computed, onMounted } from 'vue'

import { useCaseListStore } from '@/cases/stores/caseList'
import { useCasesQcStore } from '@/cases/stores/caseListQc'
import QcPlotRelatedness from '@/cases/components/CaseDetail/QcPlotRelatedness.vue'
import QcPlotDepthHet from '@/cases/components/CaseDetail/QcPlotDepthHet.vue'
import QcPlotChrXRatio from '@/cases/components/CaseDetail/QcPlotChrXRatio.vue'
import QcTableVarStats from '@/cases/components/CaseDetail/QcTableVarStats.vue'
import Overlay from '@/varfish/components/Overlay.vue'
import { downloadPerSampleMetrics, downloadRelatedness } from '@/cases/common'

// Store-related.

const caseListStore = useCaseListStore()
const casesQcStore = useCasesQcStore()

// Component state.

const overlayShow = computed(() => casesQcStore.qcValues === null)

const varStats = computed(() => {
  if (!casesQcStore.qcValues) {
    return []
  } else {
    return casesQcStore.qcValues.varStats
  }
})

const relData = computed(() => {
  if (!casesQcStore.qcValues || !casesQcStore.qcValues.relData) {
    return []
  } else {
    return casesQcStore.qcValues.relData
  }
})

// Function definitions.

const qcStoreEntry = (key) =>
  computed(() => {
    if (casesQcStore.qcValues) {
      return casesQcStore.qcValues[key]
    } else {
      return []
    }
  })

// Watching and lifecycle hooks.

onMounted(() => {
  casesQcStore.initialize()
})
</script>

<template>
  <div class="position-relative mb-3">
    <div class="row pt-3">
      <div class="col">
        <h5>Project-wide Variant Statistics</h5>

        <!-- inline help -->
        <div
          v-if="caseListStore.showInlineHelp"
          class="alert alert-secondary small p-2"
        >
          <i-mdi-information />
          You can pan the plots by dragging them with your mouse and zoom in and
          out using the your mouse's scroll wheel. Use double-click to reset the
          zoom and pan.
        </div>

        <QcPlotRelatedness :rel-data="relData" />
        <QcPlotDepthHet
          :het-ratio-quantiles="qcStoreEntry('hetRatioQuantiles').value"
          :dp-quantiles="qcStoreEntry('dpQuantiles').value"
          :dp-het-data="qcStoreEntry('dpHetData').value"
        />
        <QcPlotChrXRatio
          :pedigree="qcStoreEntry('pedigree').value"
          :sex-errors="qcStoreEntry('sexErrors').value"
          :chr-x-het-hom-ratio="qcStoreEntry('chrXHetHomRatio').value"
        />

        <h5 class="mt-3">Variant Quality Control</h5>

        <div
          v-if="caseListStore.showInlineHelp"
          class="alert alert-secondary small p-2"
        >
          <i-mdi-information />
          The following table shows some overall statistics on your samples.
          <strong> Ts </strong> - number of transitions; <strong> Tv </strong> -
          number of transversions; <strong> Ts/Tv </strong> - Ratio of
          transitions to transversions, should be between 2.0 and 2.9;
          <strong> SNVs </strong> - number of single nucleotide variants;
          <strong> indels </strong> - number of small insertions and deletions
          (usually 1/10th of SNVs); <strong> MNVS </strong> - number of multi
          nucleotie variants (e.g., AT&gt;CG), many variant callers will conver
          to adjacent SNVs and you will see 0 here;
          <strong> X hom./het. </strong> - ratio of homozygous to heterozygous
          calls on the X chromosome outside of the pseudoautosomal region, can
          be used for sanity checks on the molecular sex karyotype.
        </div>

        <QcTableVarStats :var-stats="varStats" />

        <h5 class="mt-4">Download Variant Control Metrics</h5>

        <div
          v-if="caseListStore.showInlineHelp"
          class="alert alert-secondary small p-2"
        >
          <i-mdi-information />
          Download the raw metrics used to generate the plots from above using
          the buttons below.
        </div>

        <div>
          <a
            class="btn btn-sm btn-secondary mr-2 download-per-sample"
            @click="downloadPerSampleMetrics(varStats)"
          >
            <i-mdi-cloud-download />
            Per-Sample Metrics
          </a>
          <a
            class="btn btn-sm btn-secondary download-relatedness"
            @click="downloadRelatedness(relData)"
          >
            <i-mdi-cloud-download />
            Relatedness
          </a>
        </div>
      </div>
    </div>
    <Overlay v-if="overlayShow" message="Loading QC metrics..." />
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

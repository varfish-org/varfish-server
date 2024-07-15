<script setup>
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { computed, reactive } from 'vue'

import QcPlotRelatedness from '@/cases/components/CaseDetail/QcPlotRelatedness.vue'
import QcPlotDepthHet from '@/cases/components/CaseDetail/QcPlotDepthHet.vue'
import QcPlotChrXRatio from '@/cases/components/CaseDetail/QcPlotChrXRatio.vue'
import QcPlotVarType from '@/cases/components/CaseDetail/QcPlotVarType.vue'
import QcPlotVarEffect from '@/cases/components/CaseDetail/QcPlotVarEffect.vue'
import QcPlotIndelSize from '@/cases/components/CaseDetail/QcPlotIndelSize.vue'
import QcTableVarStats from '@/cases/components/CaseDetail/QcTableVarStats.vue'
import QcTableAlignmentStats from '@/cases/components/CaseDetail/QcTableAlignmentStats.vue'
import { displayName, quantiles } from '@/varfish/helpers'
import { downloadPerSampleMetrics, downloadRelatedness } from '@/cases/common'

const caseListStore = useCaseListStore()
const caseDetailsStore = useCaseDetailsStore()

const relData = computed(() => {
  if (!caseDetailsStore.caseObj) {
    return []
  }
  const pedigree = caseDetailsStore.caseObj.pedigree
  const pedLineBySample = Object.fromEntries(
    pedigree.map((line) => [line.name, line]),
  )

  const getRel = (sample1, sample2) => {
    const pedLine1 = pedLineBySample[sample1]
    const pedLine2 = pedLineBySample[sample2]
    if (
      pedLine1.father === pedLine2.father &&
      pedLine1.mother === pedLine2.mother &&
      pedLine1.father !== '0' &&
      pedLine1.mother !== '0'
    ) {
      return { sibSib: true, parentChild: false }
    } else if (
      pedLine1.father === pedLine2.name ||
      pedLine1.mother === pedLine2.name ||
      pedLine2.father === pedLine1.name ||
      pedLine2.mother === pedLine1.name
    ) {
      return { sibSib: false, parentChild: true }
    } else {
      return { sibSib: false, parentChild: false }
    }
  }

  const computeRelatedness = ({ n_ibs0, het_1_2, het_1, het_2 }) => {
    if (het_1 * het_2) {
      return ((het_1_2 - 2 * n_ibs0) * 2) / Math.sqrt(het_1 * het_2)
    } else {
      return 0.0
    }
  }

  return caseDetailsStore.caseRelatedness.map(
    ({ n_ibs0, het_1_2, het_1, het_2, sample1, sample2 }) => {
      const sample0$ = displayName(sample1)
      const sample1$ = displayName(sample2)
      const relationship = getRel(sample1, sample2)
      return {
        ibs0: n_ibs0,
        rel: computeRelatedness({ n_ibs0, het_1_2, het_1, het_2 }),
        sample0: sample0$,
        sample1: sample1$,
        ...relationship,
      }
    },
  )
})

const dpHetData = computed(() => {
  if (!caseDetailsStore.caseObj) {
    return []
  } else {
    return Object.entries(caseDetailsStore.caseVariantStats).map(
      ([sample, { het_ratio, ontarget_dp_quantiles }]) => {
        return {
          x: ontarget_dp_quantiles[2],
          y: het_ratio,
          sample: displayName(sample),
        }
      },
    )
  }
})

const hetRatioQuantiles = computed(() => {
  return quantiles(
    dpHetData.value.map(({ y }) => y),
    [0.0, 0.25, 0.5, 0.75, 1.0],
  )
})

const dpQuantiles = computed(() => {
  return quantiles(
    dpHetData.value.map(({ x }) => x),
    [0.0, 0.25, 0.5, 0.75, 1.0],
  )
})

const caseObjEntry = (key) =>
  computed(() => {
    if (!caseDetailsStore.caseObj) {
      return null
    } else {
      return caseDetailsStore.caseObj[key]
    }
  })

const chrXHetHomRatio = computed(() => {
  if (!caseDetailsStore.caseObj) {
    return null
  } else {
    const resultEntries = Object.entries(caseDetailsStore.caseVariantStats).map(
      ([name, stats]) => [name, stats.chrx_het_hom],
    )
    return reactive(Object.fromEntries(resultEntries))
  }
})

const varStats = computed(() => {
  if (!caseDetailsStore.caseObj) {
    return []
  } else {
    return Object.entries(caseDetailsStore.caseVariantStats).map(
      ([name, stats]) => {
        return {
          sample_name: displayName(name),
          ...stats,
        }
      },
    )
  }
})
</script>

<template>
  <div class="position-relative mb-3">
    <div class="row pt-3">
      <div class="col">
        <h5>Variant Statistics</h5>

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
          :het-ratio-quantiles="hetRatioQuantiles"
          :dp-quantiles="dpQuantiles"
          :dp-het-data="dpHetData"
        />
        <QcPlotChrXRatio
          :pedigree="caseObjEntry('pedigree').value"
          :sex-errors="caseObjEntry('sex_errors').value"
          :chr-x-het-hom-ratio="chrXHetHomRatio"
        />
        <QcPlotVarType :variant-stats="caseDetailsStore.caseVariantStats" />
        <QcPlotVarEffect :variant-stats="caseDetailsStore.caseVariantStats" />
        <QcPlotIndelSize :variant-stats="caseDetailsStore.caseVariantStats" />

        <h5 class="mt-3">Variant Quality Control</h5>

        <div
          v-if="caseListStore.showInlineHelp"
          class="alert alert-secondary small p-2"
        >
          <i-mdi-information />
          The following table shows some overall variant statistics on your
          samples.
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

        <h5 class="mt-3">Alignment Quality Control</h5>

        <div
          v-if="caseListStore.showInlineHelp"
          class="alert alert-secondary small p-2"
        >
          <i-mdi-information />
          The following table shows some overall alignment statistics on your
          samples and the minimal exon coverage.
        </div>

        <QcTableAlignmentStats />

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
  </div>
</template>

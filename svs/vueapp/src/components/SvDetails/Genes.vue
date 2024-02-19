<script setup lang="ts">
import { useSvDetailsStore } from '@svs/stores/svDetails'
import { computed, ComputedRef, Ref, ref } from 'vue'
import { roundIt } from '@varfish/moreUtils'

import EasyDataTable from 'vue3-easy-data-table'
import type { ClickRowArgument, Header, Item } from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import VariantDetailsGene from '@variants/components/VariantDetails/Gene.vue'

/** `GeneInfo` is a type alias for easier future interface definition. */
type GeneInfo = any
/** `SvRecord` is a type alias for easier future interface definition. */
type SvRecord = any

const props = defineProps<{
  genesInfos?: GeneInfo[]
  currentSvRecord?: SvRecord
}>()

const clingenDosageScore: { [key: string]: number } = {
  CLINGEN_DOSAGE_SCORE_UNKNOWN: 0,
  CLINGEN_DOSAGE_SCORE_SUFFICIENT_EVIDENCE_AVAILABLE: 3,
  CLINGEN_DOSAGE_SCORE_SOME_EVIDENCE_AVAILABLE: 2,
  CLINGEN_DOSAGE_SCORE_LITTLE_EVIDENCE: 1,
  CLINGEN_DOSAGE_SCORE_NO_EVIDENCE_AVAILABLE: 0,
  CLINGEN_DOSAGE_SCORE_RECESSIVE: 30,
  CLINGEN_DOSAGE_SCORE_UNLIKELY: 40,
}
const clingenDosageLabel: { [key: string]: string } = {
  CLINGEN_DOSAGE_SCORE_UNKNOWN: 'unknown',
  CLINGEN_DOSAGE_SCORE_SUFFICIENT_EVIDENCE_AVAILABLE:
    'sufficient evidence for dosage pathogenicity',
  CLINGEN_DOSAGE_SCORE_SOME_EVIDENCE_AVAILABLE:
    'some evidence for dosage pathogenicity',
  CLINGEN_DOSAGE_SCORE_LITTLE_EVIDENCE:
    'little evidence for dosage pathogenicity',
  CLINGEN_DOSAGE_SCORE_NO_EVIDENCE_AVAILABLE:
    'no evidence for dosage pathogenicity',
  CLINGEN_DOSAGE_SCORE_RECESSIVE:
    'gene associated with autosomal recessive phenotype',
  CLINGEN_DOSAGE_SCORE_UNLIKELY: 'dosage sensitivity unlikely',
}

const currentGeneInfos: Ref<any> = ref(undefined)
const currentGeneClinvar: Ref<any> = ref(undefined)

const genesInfosByHgnc: ComputedRef<Map<string, any>> = computed(
  (): Map<string, any> => {
    const result = new Map()
    for (const record of props.genesInfos ?? []) {
      result.set(record.hgnc.hgnc_id, record)
    }
    return result
  },
)

const headers: Header[] = [
  {
    text: 'symbol',
    value: 'dbnsfp.geneName',
    width: 150,
    sortable: true,
  },
  {
    text: 'name',
    value: 'dbnsfp.geneFullName',
    width: 200,
  },
  {
    text: 'OMIM',
    value: 'omim',
    sortable: true,
  },
  {
    text: 'Orphanet',
    value: 'orpha',
    sortable: true,
  },
  {
    text: 'pLI',
    value: 'gnomadConstraints.pli',
    width: 50,
    sortable: true,
  },
  {
    text: 'o/e LoF (upper)',
    value: 'gnomadConstraints.oeLofUpper',
    width: 100,
    sortable: true,
  },
  {
    text: 'P(HI)',
    width: 50,
    value: 'dbnsfp.haploinsufficiency',
  },
  {
    text: 'sHet',
    width: 100,
    value: 'shet.s_het',
    sortable: true,
  },
  {
    text: 'pHaplo',
    width: 100,
    value: 'rcnv.pHaplo',
    sortable: true,
  },
  {
    text: 'pTriplo',
    width: 100,
    value: 'rcnv.pTriplo',
    sortable: true,
  },
  {
    text: 'CG haploin.',
    width: 100,
    value: 'clingen.haploSummary',
  },
  {
    text: 'CG triploin.',
    width: 100,
    value: 'clingen.triploSummary',
  },
]

/** The SV details store. */
const svDetailsStore = useSvDetailsStore()

/** Helper type for `resultsInfos`. */
type ResultsInfo = {
  isDiseaseGene: boolean
  txEffect?: string
}

/**
 * Compute mapping from HGNC gene ID to transcript effect and disease gene property
 * so we can display the same information as in the SV results table.
 */
const resultsInfos: ComputedRef<Map<string, ResultsInfo>> = computed(() => {
  const result = new Map()
  for (const txEffect of svDetailsStore.currentSvRecord?.payload?.tx_effects ??
    []) {
    const value: ResultsInfo = {
      isDiseaseGene: txEffect.gene.is_disease_gene,
      txEffect: txEffect.transcript_effects[0],
    }
    result.set(txEffect.gene.hgnc_id, value)
  }
  return result
})

/** Compute geneInfo's class. */
const geneInfoClass = (geneInfo: any): string | undefined => {
  const resultsInfo = resultsInfos.value.get(geneInfo.hgnc.hgnc_id)
  if (resultsInfo?.isDiseaseGene) {
    return 'text-danger'
  } else {
    return
  }
}

/** Compute geneInfo's badge HTML (if any). */
const geneInfoBadge = (geneInfo: any): string | undefined => {
  const badge = (color: string, title: string, text: string): string => {
    return `<span class="badge badge-${color}" title="${title}">${text}</span>&nbsp;`
  }

  const resultsInfo = resultsInfos.value.get(geneInfo.hgnc.hgnc_id)
  switch (resultsInfo?.txEffect) {
    case 'transcript_variant':
      return badge('danger', 'whole transcript is affected', 'tx')
    case 'exon_variant':
      return badge('danger', 'exonic for gene', 'ex')
    case 'splice_region_variant':
      return badge('danger', 'affects splice region for gene', 'sr')
    case 'intron_variant':
      return badge('warning', 'intronic for gene', 'in')
    case 'upstream_variant':
      return badge('secondary', 'upstream of gene', 'up')
    case 'downstream_variant':
      return badge('secondary', 'downstream of gene gene', 'dw')
    default:
      return ''
  }
}

const onRowClicked = (item: ClickRowArgument) => {
  currentGeneInfos.value = item
}
</script>

<template>
  <div>
    <div class="p-2">
      <EasyDataTable
        :headers="headers"
        :items="props.genesInfos ?? []"
        :loading="!props.genesInfos?.length"
        buttons-pagination
        show-index
        @click-row="onRowClicked"
      >
        <template #empty-message>
          <em class="ml-2 text-dark">
            <strong>No genes available.</strong>
          </em>
        </template>
        <template #item-dbnsfp.gene_name="geneInfo">
          <span v-html="geneInfoBadge(geneInfo)" />
          <span :class="geneInfoClass(geneInfo)">
            {{ geneInfo.dbnsfp?.gene_name }}
          </span>
        </template>

        <template #item-omim="{ omim }">
          <template v-if="omim?.omim_diseases?.length">
            <template v-for="(disease, idx) in omim?.omim_diseases">
              <template v-if="idx > 0">, </template>
              <a
                :href="`https://www.omim.org/entry/${disease.omim_id.replace(
                  'OMIM:',
                  '',
                )}`"
                target="_blank"
              >
                {{ disease.label }}
              </a>
            </template>
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-orpha="{ orpha }">
          <template v-if="orpha?.orpha_diseases?.length">
            <template v-for="(disease, idx) in orpha?.orpha_diseases">
              <template v-if="idx > 0">, </template>
              <a
                :href="`https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Expert=${disease.orpha_id.replace(
                  'ORPHA:',
                  '',
                )}`"
                target="_blank"
              >
                {{ disease.label }}
              </a>
            </template>
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-gnomad_constraints.pli="{ gnomad_constraints }">
          <template v-if="gnomad_constraints">
            <span v-html="roundIt(gnomad_constraints.pli, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template
          #item-gnomad_constraints.oe_lof_upper="{ gnomad_constraints }"
        >
          <template v-if="gnomad_constraints">
            <span v-html="roundIt(gnomad_constraints.oe_lof_upper, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-dbnsfp.haploinsufficiency="{ dbnsfp }">
          <template v-if="dbnsfp?.haploinsufficiency">
            <span v-html="roundIt(dbnsfp.haploinsufficiency, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-shet.s_het="{ shet }">
          <template v-if="shet?.s_het">
            <span v-html="roundIt(shet.s_het, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-rcnv.p_haplo="{ rcnv }">
          <template v-if="rcnv?.p_haplo">
            <span v-html="roundIt(rcnv.p_haplo, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-rcnv.p_triplo="{ rcnv }">
          <template v-if="rcnv?.p_triplo">
            <span v-html="roundIt(rcnv.p_triplo, 3)" />
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-clingen.haplo_summary="{ clingen }">
          <template v-if="clingen?.haplo_summary">
            <abbr :title="clingen.haplo_label">{{
              clingen.haplo_summary
            }}</abbr>
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-clingen.triplo_summary="{ clingen }">
          <template v-if="clingen?.triplo_summary">
            <abbr :title="clingen.triplo_label">{{
              clingen.triplo_summary
            }}</abbr>
          </template>
          <template v-else> &mdash; </template>
        </template>
      </EasyDataTable>
    </div>

    <div v-if="currentGeneInfos">
      <div
        class="ml-2 mr-2"
        style="
          font-weight: bolder;
          font-size: 120%;
          border-bottom: 1px solid #aaaaaa;
        "
      >
        Gene Details: {{ currentGeneInfos.hgnc.symbol }}
      </div>
      <VariantDetailsGene :gene="currentGeneInfos" :gene-clinvar="undefined" />
    </div>
    <div v-else class="text-muted text-center font-italic pt-2">
      Select gene in table above to see details.
    </div>
  </div>
</template>

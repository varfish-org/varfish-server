<script setup lang="ts">
import { useSvDetailsStore } from '@svs/stores/detailsSv'
import { computed, ComputedRef, Ref, ref } from 'vue'
import { roundIt } from '@varfish/more-utils'

import EasyDataTable from 'vue3-easy-data-table'
import type { ClickRowArgument, Header, Item } from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

import VariantDetailsGene from '@variants/components/VariantDetailsGene.vue'

/** `GeneInfo` is a type alias for easier future interface definition. */
type GeneInfo = any
/** `SvRecord` is a type alias for easier future interface definition. */
type SvRecord = any

const props = defineProps<{
  genesInfos?: GeneInfo[]
  currentSvRecord?: SvRecord
}>()

const currentGeneInfos: Ref<any> = ref(null)

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
    value: 'dbnsfp.gene_name',
    width: 150,
    sortable: true,
  },
  {
    text: 'name',
    value: 'dbnsfp.gene_full_name',
    width: 200,
  },
  {
    text: 'OMIM',
    value: 'dbnsfp.mim_disease.length',
    sortable: true,
  },
  {
    text: 'Orphanet',
    value: 'dbnsfp.orphanet_disorder.length',
    sortable: true,
  },
  {
    text: 'pLI',
    value: 'gnomad_constraints.pli',
    width: 50,
    sortable: true,
  },
  {
    text: 'o/e LoF (upper)',
    value: 'gnomad_constraints.oe_lof_upper',
    width: 100,
    sortable: true,
  },
  {
    text: 'P(HI)',
    width: 50,
    value: 'dbnsfp.haploinsufficiency',
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
const geneInfoClass = (geneInfo: any): string | null => {
  let resultsInfo = resultsInfos.value.get(geneInfo.hgnc.hgnc_id)
  if (resultsInfo?.isDiseaseGene) {
    return 'text-danger'
  } else {
    return
  }
}

/** Compute geneInfo's badge HTML (if any). */
const geneInfoBadge = (geneInfo: any): string | null => {
  const badge = (color: string, title: string, text: string): string => {
    return `<span class="badge badge-${color}" title="${title}">${text}</span>&nbsp;`
  }

  let resultsInfo = resultsInfos.value.get(geneInfo.hgnc.hgnc_id)
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

/** Compute list of gene infos to protect against empty `props.genesInfos`. */
const items: ComputedRef<GeneInfo[]> = computed(() => {
  if (props.genesInfos) {
    return props.genesInfos
  } else {
    return []
  }
})

/** Helper formats the dbNSFP `FUNCTION` strings. */
const formatFunctions = (strs: string[]): string => {
  const mapped = strs.map((s) => {
    // strip prefix
    const preStripped = s.replace(/^FUNCTION: /, '')
    // strip source/evidence suffix
    const sufStripped = preStripped.replace(/ {([^},]+)(, ([^},]+))*}\.$/, '')
    // format links into pubmed
    return sufStripped.replace(/PubMed:(\d+)/g, (match) => {
      const pmid = match.replace('PubMed:', '')
      return `<a href="https://pubmed.ncbi.nlm.nih.gov/${pmid}/" target="_blank">${pmid}</a>`
    })
  })
  return mapped.join(' // ')
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
        :items="items"
        :loading="!items"
        buttons-pagination
        show-index
        @click-row="onRowClicked"
      >
        <template #item-dbnsfp.gene_name="geneInfo">
          <span v-html="geneInfoBadge(geneInfo)" />
          <span :class="geneInfoClass(geneInfo)">
            {{ geneInfo.dbnsfp?.gene_name }}
          </span>
        </template>

        <template #item-dbnsfp.mim_disease.length="geneInfo">
          <template v-if="geneInfo.dbnsfp?.mim_disease.length">
            {{ geneInfo.dbnsfp?.mim_disease.join(' // ') }}
          </template>
          <template v-else> &mdash; </template>
        </template>

        <template #item-dbnsfp.orphanet_disorder.length="geneInfo">
          <template v-if="geneInfo.dbnsfp?.orphanet_disorder.length">
            {{ geneInfo.dbnsfp?.orphanet_disorder.join(' // ') }}
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
      <VariantDetailsGene :gene="currentGeneInfos" />
    </div>
    <div v-else class="text-muted text-center font-italic pt-2">
      Select gene in table above to see details.
    </div>
  </div>
</template>

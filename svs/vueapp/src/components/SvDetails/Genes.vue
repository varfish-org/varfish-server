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
  {
    text: 'sHet',
    width: 100,
    value: 'shet.s_het',
    sortable: true,
  },
  {
    text: 'pHaplo',
    width: 100,
    value: 'rcnv.p_haplo',
    sortable: true,
  },
  {
    text: 'pTriplo',
    width: 100,
    value: 'rcnv.p_triplo',
    sortable: true,
  },
  {
    text: 'CG haploin.',
    width: 100,
    value: 'clingen.haplo_summary',
  },
  {
    text: 'CG triploin.',
    width: 100,
    value: 'clingen.triplo_summary',
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
    const genesInfos = JSON.parse(JSON.stringify(props.genesInfos))
    for (const geneInfo of genesInfos) {
      if (geneInfo.clingen) {
        const haploLabels = new Map<number, string>()
        const triploLabels = new Map<number, string>()

        for (const diseaseRecord of geneInfo.clingen.disease_records) {
          if (diseaseRecord.dosage_haploinsufficiency_assertion?.length) {
            const val = parseInt(
              diseaseRecord.dosage_haploinsufficiency_assertion.split(' ')[0],
            )
            haploLabels.set(
              val,
              diseaseRecord.dosage_haploinsufficiency_assertion,
            )
          }
          if (diseaseRecord.dosage_triplosensitivity_assertion?.length) {
            const val = parseInt(
              diseaseRecord.dosage_triplosensitivity_assertion.split(' ')[0],
            )
            triploLabels.set(
              val,
              diseaseRecord.dosage_triplosensitivity_assertion,
            )
          }
        }

        if (haploLabels.size) {
          geneInfo.clingen.haplo_summary = Math.max(...haploLabels.keys())
          geneInfo.clingen.haplo_label = haploLabels.get(
            geneInfo.clingen.haplo_summary,
          )
        } else {
          geneInfo.clingen.haplo_summary = null
          geneInfo.clingen.haplo_label = null
        }
        if (triploLabels.size) {
          geneInfo.clingen.triplo_summary = Math.max(...triploLabels.keys())
          geneInfo.clingen.triplo_label = triploLabels.get(
            geneInfo.clingen.triplo_summary,
          )
        } else {
          geneInfo.clingen.triplo_summary = null
          geneInfo.clingen.triplo_label = null
        }
      }
    }
    return genesInfos
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
      <VariantDetailsGene :gene="currentGeneInfos" />
    </div>
    <div v-else class="text-muted text-center font-italic pt-2">
      Select gene in table above to see details.
    </div>
  </div>
</template>

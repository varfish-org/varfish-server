<script setup lang="ts">
/**
 * Detailed display of strucvar information.
 *
 * Used in the strucvar filtration app and displayed when the user selects a variant to display
 * the details for.
 *
 * Also used in the case details view for displaying all user-annotated variants.
 *
 * See `SeqvarDetails` for a peer app for sequence variants
 */
import GeneClinvarCard from '@bihealth/reev-frontend-lib/components/GeneClinvarCard/GeneClinvarCard.vue'
import GeneConditionsCard from '@bihealth/reev-frontend-lib/components/GeneConditionsCard/GeneConditionsCard.vue'
import GeneExpressionCard from '@bihealth/reev-frontend-lib/components/GeneExpressionCard/GeneExpressionCard.vue'
import GeneLiteratureCard from '@bihealth/reev-frontend-lib/components/GeneLiteratureCard/GeneLiteratureCard.vue'
import GeneOverviewCard from '@bihealth/reev-frontend-lib/components/GeneOverviewCard/GeneOverviewCard.vue'
import GenePathogenicityCard from '@bihealth/reev-frontend-lib/components/GenePathogenicityCard/GenePathogenicityCard.vue'
import GenomeBrowserCard from '@bihealth/reev-frontend-lib/components/GenomeBrowserCard/GenomeBrowserCard.vue'
import StrucvarClinvarCard from '@bihealth/reev-frontend-lib/components/StrucvarClinvarCard/StrucvarClinvarCard.vue'
import StrucvarGeneListCard from '@bihealth/reev-frontend-lib/components/StrucvarGeneListCard/StrucvarGeneListCard.vue'
import StrucvarToolsCard from '@bihealth/reev-frontend-lib/components/StrucvarToolsCard/StrucvarToolsCard.vue'
import {
  BreakendStrucvarImpl,
  LinearStrucvarImpl,
  Strucvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { StoreState } from '@bihealth/reev-frontend-lib/stores'
import { useGeneInfoStore } from '@bihealth/reev-frontend-lib/stores/geneInfo'
import { usePubtatorStore } from '@bihealth/reev-frontend-lib/stores/pubtator'
import { useStrucvarInfoStore } from '@bihealth/reev-frontend-lib/stores/strucvarInfo'
import { computed, onMounted, ref, watch } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import AcmgRatingCard from '@/svs/components/StrucvarAcmgRatingCard/StrucvarAcmgRatingCard.vue'
import StrucvarDetailsHeader from '@/svs/components/StrucvarDetailsHeader/StrucvarDetailsHeader.vue'
import StrucvarDetailsNavi from '@/svs/components/StrucvarDetailsNavi/StrucvarDetailsNavi.vue'
import StrucvarGenotypeCallCard from '@/svs/components/StrucvarGenotypeCallCard/StrucvarGenotypeCallCard.vue'
import { useSvFlagsStore } from '@/svs/stores/strucvarFlags'
import { useSvCommentsStore } from '@/svs/stores/svComments'
import { useSvDetailsStore } from '@/svs/stores/svDetails'
import { useSvResultSetStore } from '@/svs/stores/svResultSet'
import CommentsCard from '@/varfish/components/CommentsCard/CommentsCard.vue'
import FlagsCard from '@/varfish/components/FlagsCard/FlagsCard.vue'
import { State } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'

import { svLocus } from './lib'

const props = defineProps<{
  /** Project UUID. */
  projectUuid: string
  /** UUID of the result row to display. */
  resultRowUuid?: string
  /** Identifier of the selected section. */
  selectedSection?: string
}>()

// Store-related

/** Application context. */
const ctxStore = useCtxStore()

/** Information about the strucvar, used to fetch information on load. */
const strucvarInfoStore = useStrucvarInfoStore()
/** Information about the genes. */
const geneInfoStore = useGeneInfoStore()

const caseDetailsStore = useCaseDetailsStore()
/** Management of strucvar results ets. */
const svResultSetStore = useSvResultSetStore()
/** Management of strucvar details. */
const svDetailsStore = useSvDetailsStore()
/** Management of strucvar flags. */
const svFlagsStore = useSvFlagsStore()
/** Management of strucvar comments. */
const svCommentsStore = useSvCommentsStore()
/** Management of PubTator store. */
const pubtatorStore = usePubtatorStore()

/** Component state; HGNC identifier of selected gene. */
const selectedGeneHgncId = ref<string | undefined>(undefined)
/** Selected gene information. */
const selectedGeneInfo = computed<any | undefined>(() => {
  return (strucvarInfoStore.genesInfos || []).find((geneInfo) => {
    return geneInfo.hgnc?.hgncId === selectedGeneHgncId.value
  })
})

/**
 * Load data for the given gene into the gene info store.
 *
 * This is done every time the user selects a new gene.
 */
const loadGeneToStore = async (hgncId: string) => {
  if (strucvarInfoStore.strucvar !== undefined) {
    await geneInfoStore.initialize(
      hgncId,
      strucvarInfoStore.strucvar.genomeBuild,
    )
  }
}

/** Refresh the stores. */
const refreshStores = async () => {
  if (props.resultRowUuid && props.selectedSection) {
    await svResultSetStore.initialize()
    await svResultSetStore.fetchResultSetViaRow(props.resultRowUuid)
    if (!svResultSetStore.caseUuid) {
      throw new Error('caseUuid not set')
    }
    await caseDetailsStore.initialize(
      props.projectUuid,
      svResultSetStore.caseUuid,
    )
    let strucvar: Strucvar
    if (svResultSetStore.resultRow.sv_type === 'BND') {
      strucvar = new BreakendStrucvarImpl(
        svResultSetStore.resultRow.release === 'GRCh37' ? 'grch37' : 'grch38',
        svResultSetStore.resultRow.chromosome.replace('chr', ''),
        svResultSetStore.resultRow.chromosome2.replace('chr', ''),
        svResultSetStore.resultRow.start,
        svResultSetStore.resultRow.end,
      )
    } else {
      strucvar = new LinearStrucvarImpl(
        svResultSetStore.resultRow.sv_type,
        svResultSetStore.resultRow.release === 'GRCh37' ? 'grch37' : 'grch38',
        svResultSetStore.resultRow.chromosome,
        svResultSetStore.resultRow.start,
        svResultSetStore.resultRow.end,
      )
    }
    await Promise.all([
      strucvarInfoStore.initialize(strucvar),
      svFlagsStore.initialize(props.projectUuid, svResultSetStore.caseUuid),
      svCommentsStore.initialize(props.projectUuid, svResultSetStore.caseUuid),
      svDetailsStore.initialize(props.projectUuid, svResultSetStore.caseUuid),
    ])
    await svDetailsStore.fetchSvDetails(svResultSetStore.resultRow)
  }

  document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
}

/** Watch change in properties to reload data. */
watch(
  () => [props.resultRowUuid, props.selectedSection],
  async () => {
    await refreshStores()
  },
)

watch(
  () => [
    svResultSetStore.storeState.state,
    pubtatorStore.storeState,
    geneInfoStore.storeState,
    strucvarInfoStore.storeState,
    svCommentsStore.storeState,
    svDetailsStore.storeState,
  ],
  () => {
    const completeStates = [State.Active, State.Error]
    const completeStoreStates = [StoreState.Active, StoreState.Error]
    if (
      completeStates.includes(svResultSetStore.storeState.state) &&
      completeStoreStates.includes(pubtatorStore.storeState) &&
      completeStoreStates.includes(geneInfoStore.storeState) &&
      completeStoreStates.includes(strucvarInfoStore.storeState) &&
      completeStates.includes(svCommentsStore.storeState.state) &&
      completeStates.includes(svDetailsStore.storeState.state)
    ) {
      setTimeout(() => {
        document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
      }, 500)
    }
  },
)

/** When mounted, scroll to the selected element if any.
 */
onMounted(async () => {
  await refreshStores()
})

// Watch changes of selected HGNC ID and load gene.
watch(
  () => selectedGeneHgncId.value,
  async (newHgncId: string | undefined) => {
    if (newHgncId !== undefined) {
      await loadGeneToStore(newHgncId)
      document.querySelector(`#gene-overview`)?.scrollIntoView()
    }
  },
)
</script>

<template>
  <v-app>
    <v-main>
      <v-container fluid class="pa-0">
        <v-row no-gutters>
          <v-col cols="2" class="pr-3">
            <div style="position: sticky; top: 20px">
              <StrucvarDetailsNavi
                :strucvar="strucvarInfoStore.strucvar"
                :case-uuid="svResultSetStore.caseUuid ?? undefined"
              />
            </div>
          </v-col>
          <v-col cols="10">
            <div id="top" class="mt-6 mb-3 ml-1">
              <StrucvarDetailsHeader
                :strucvar="strucvarInfoStore.strucvar"
                :result-row-payload="svResultSetStore?.resultRow?.payload"
              />
            </div>
            <div id="gene-list">
              <StrucvarGeneListCard
                v-model:selected-gene-hgnc-id="selectedGeneHgncId"
                :current-strucvar-record="strucvarInfoStore.strucvar"
                :csq="strucvarInfoStore.csq"
                :genes-infos="strucvarInfoStore.genesInfos"
                :store-state="strucvarInfoStore.storeState"
                entry-column-width="260px"
              />
            </div>

            <template v-if="!selectedGeneInfo">
              <div class="text-h5 mt-2 mb-3 ml-1">No Gene</div>
            </template>
            <template v-else>
              <div class="text-h5 mt-3 mb-2 ml-1">
                Gene
                <span class="font-italic">
                  {{ selectedGeneInfo?.hgnc!.symbol }}
                </span>
              </div>
              <div id="gene-overview" class="mt-3">
                <GeneOverviewCard :gene-info="selectedGeneInfo" />
              </div>
              <div id="gene-pathogenicity" class="mt-3">
                <GenePathogenicityCard :gene-info="selectedGeneInfo" />
              </div>
              <div id="gene-conditions" class="mt-3">
                <GeneConditionsCard :gene-info="selectedGeneInfo">
                  <CadaRanking
                    :hgnc-id="geneInfoStore.geneInfo?.hgnc!.hgncId"
                  />
                </GeneConditionsCard>
              </div>
              <div id="gene-expression" class="mt-3">
                <GeneExpressionCard
                  :gene-symbol="selectedGeneInfo?.hgnc?.symbol"
                  :expression-records="selectedGeneInfo?.gtex?.records"
                  :ensembl-gene-id="selectedGeneInfo?.gtex?.ensemblGeneId"
                />
              </div>
              <div
                v-if="geneInfoStore?.geneClinvar"
                id="gene-clinvar"
                class="mt-3"
              >
                <GeneClinvarCard
                  :clinvar-per-gene="geneInfoStore.geneClinvar"
                  :transcripts="geneInfoStore.transcripts"
                  :genome-build="strucvarInfoStore.strucvar?.genomeBuild"
                  :gene-info="geneInfoStore.geneInfo"
                  :per-freq-counts="geneInfoStore?.geneClinvar?.perFreqCounts"
                />
              </div>
              <div id="gene-literature" class="mt-3">
                <GeneLiteratureCard :gene-info="geneInfoStore.geneInfo" />
              </div>
            </template>

            <div>
              <div class="text-h5 mt-3 mb-2 ml-1">
                Structural Variant Details
              </div>

              <div id="strucvar-calldetails" class="mt-3">
                <StrucvarGenotypeCallCard
                  :result-row="svResultSetStore.resultRow ?? undefined"
                />
              </div>
              <div id="strucvar-clinvar" class="mt-3">
                <StrucvarClinvarCard
                  :strucvar="strucvarInfoStore.strucvar"
                  :clinvar-sv-records="strucvarInfoStore.clinvarSvRecords"
                />
              </div>
              <div id="strucvar-tools" class="mt-3">
                <StrucvarToolsCard :strucvar="strucvarInfoStore.strucvar" />
              </div>
              <div id="strucvar-flags" class="mt-3">
                <FlagsCard
                  :flags-store="svFlagsStore"
                  :variant="strucvarInfoStore.strucvar"
                  :result-row-uuid="props.resultRowUuid ?? ''"
                  :case-uuid="caseDetailsStore.caseUuid ?? undefined"
                />
              </div>
              <div id="strucvar-comments" class="mt-3">
                <CommentsCard
                  :comments-store="svCommentsStore"
                  :variant="strucvarInfoStore.strucvar"
                  :result-row-uuid="props.resultRowUuid ?? ''"
                  :case-uuid="caseDetailsStore.caseUuid ?? undefined"
                />
              </div>
              <div id="strucvar-acmgrating" class="mt-3">
                <AcmgRatingCard
                  :project-uuid="props.projectUuid"
                  :case-uuid="caseDetailsStore.caseUuid ?? undefined"
                  :strucvar="strucvarInfoStore.strucvar"
                  :result-row-uuid="props.resultRowUuid ?? ''"
                />
              </div>
              <div id="strucvar-genomebrowser">
                <GenomeBrowserCard
                  :genome-build="strucvarInfoStore.strucvar?.genomeBuild"
                  :locus="svLocus(strucvarInfoStore.strucvar) as string"
                />
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style>
/** Adjust styles in StrucvarGeneListCard to fix leaking bootstrap4 styles. */
#gene-list
  > div
  > div.v-card-text
  > div
  > div
  > div
  > div.v-col.v-col-10.d-flex.flex-column.pa-0
  > div {
  margin: 10px;
}
</style>

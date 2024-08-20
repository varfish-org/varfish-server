<script setup lang="ts">
/**
 * Detailed display of variant information.
 *
 * Used in the variant filtration app and displayed when the user selects a variant to display
 * the details for.
 *
 * Also used in the case details view for displyaing all user-annotated variants.
 *
 * See `StrucvarDetails` for a peer app for structural variants
 */
import GeneClinvarCard from '@bihealth/reev-frontend-lib/components/GeneClinvarCard/GeneClinvarCard.vue'
import GeneConditionsCard from '@bihealth/reev-frontend-lib/components/GeneConditionsCard/GeneConditionsCard.vue'
import GeneExpressionCard from '@bihealth/reev-frontend-lib/components/GeneExpressionCard/GeneExpressionCard.vue'
import GeneLiteratureCard from '@bihealth/reev-frontend-lib/components/GeneLiteratureCard/GeneLiteratureCard.vue'
import GeneOverviewCard from '@bihealth/reev-frontend-lib/components/GeneOverviewCard/GeneOverviewCard.vue'
import GenePathogenicityCard from '@bihealth/reev-frontend-lib/components/GenePathogenicityCard/GenePathogenicityCard.vue'
import SeqvarBeaconNetworkCard from '@bihealth/reev-frontend-lib/components/SeqvarBeaconNetworkCard/SeqvarBeaconNetworkCard.vue'
import SeqvarClinvarCard from '@bihealth/reev-frontend-lib/components/SeqvarClinvarCard/SeqvarClinvarCard.vue'
import SeqvarConsequencesCard from '@bihealth/reev-frontend-lib/components/SeqvarConsequencesCard/SeqvarConsequencesCard.vue'
import SeqvarFreqsCard from '@bihealth/reev-frontend-lib/components/SeqvarFreqsCard/SeqvarFreqsCard.vue'
import SeqvarScoresCard from '@bihealth/reev-frontend-lib/components/SeqvarScoresCard/SeqvarScoresCard.vue'
import SeqvarToolsCard from '@bihealth/reev-frontend-lib/components/SeqvarToolsCard/SeqvarToolsCard.vue'
import SeqvarVariantValidatorCard from '@bihealth/reev-frontend-lib/components/SeqvarVariantValidatorCard/SeqvarVariantValidatorCard.vue'
import { Seqvar, SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { StoreState } from '@bihealth/reev-frontend-lib/stores'
import { useGeneInfoStore } from '@bihealth/reev-frontend-lib/stores/geneInfo'
import { usePubtatorStore } from '@bihealth/reev-frontend-lib/stores/pubtator'
import { useSeqvarInfoStore } from '@bihealth/reev-frontend-lib/stores/seqvarInfo'
import { computed, onMounted, ref } from 'vue'
import { watch } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import CommentsCard from '@/varfish/components/CommentsCard/CommentsCard.vue'
import FlagsCard from '@/varfish/components/FlagsCard/FlagsCard.vue'
import { State } from '@/varfish/storeUtils'
import AcmgRatingCard from '@/variants/components/AcmgRatingCard/AcmgRatingCard.vue'
import SeqvarDetailsHeader from '@/variants/components/SeqvarDetailsHeader/SeqvarDetailsHeader.vue'
import SeqvarDetailsNavi from '@/variants/components/SeqvarDetailsNavi/SeqvarDetailsNavi.vue'
import SeqvarGenotypeCallCard from '@/variants/components/SeqvarGenotypeCallCard/SeqvarGenotypeCallCard.vue'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { useVariantCommentsStore } from '@/variants/stores/variantComments'
import { useVariantDetailsStore } from '@/variants/stores/variantDetails'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'

/** This component's props. */
const props = defineProps<{
  /** Project UUID. */
  projectUuid: string
  /** UUID of the result row to display. */
  resultRowUuid: string
  /** Identifier of the selected section. */
  selectedSection?: string
  /** Hide back button */
  hideBackButton?: boolean
}>()

// Store-related

/** Information about the sequence variant, used to fetch information on load. */
const seqvarInfoStore = useSeqvarInfoStore()
/** Information about the affected gene, used to fetch information on load. */
const geneInfoStore = useGeneInfoStore()

const caseDetailsStore = useCaseDetailsStore()
const variantResultSetStore = useVariantResultSetStore()
const variantDetailsStore = useVariantDetailsStore()
const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const variantAcmgRatingStore = useVariantAcmgRatingStore()
const pubtatorStore = usePubtatorStore()

const storesLoading = ref(true)

/** Currently displayed Seqvar. */
const seqvar = computed<Seqvar | undefined>(() => {
  if (!variantResultSetStore.resultRow) {
    return undefined
  } else {
    return new SeqvarImpl(
      variantResultSetStore.resultRow.release === 'GRCh37'
        ? 'grch37'
        : 'grch38',
      variantResultSetStore.resultRow.chromosome,
      variantResultSetStore.resultRow.start,
      variantResultSetStore.resultRow.reference,
      variantResultSetStore.resultRow.alternative,
    )
  }
})

/** Refresh the stores. */
const refreshStores = async () => {
  console.log('Refreshing stores')
  console.log(props.resultRowUuid)
  if (props.resultRowUuid) {
    await variantResultSetStore.initialize()
    await variantResultSetStore.fetchResultSetViaRow(props.resultRowUuid)
    if (!variantResultSetStore.caseUuid) {
      throw new Error('No case UUID found')
    }
    await caseDetailsStore.initialize(
      props.projectUuid,
      variantResultSetStore.caseUuid,
    )
    await Promise.all([
      variantFlagsStore.initialize(
        props.projectUuid,
        variantResultSetStore.caseUuid,
      ),
      variantCommentsStore.initialize(
        props.projectUuid,
        variantResultSetStore.caseUuid,
      ),
      variantAcmgRatingStore.initialize(
        props.projectUuid,
        variantResultSetStore.caseUuid,
      ),
      variantDetailsStore.initialize(
        props.projectUuid,
        variantResultSetStore.caseUuid,
      ),
      pubtatorStore.initialize(
        variantResultSetStore.resultRow.payload!.hgnc_symbol,
      ),
    ])
    await variantDetailsStore.fetchVariantDetails(
      variantResultSetStore.resultRow,
    )
    // TODO: properly use types
    if (!seqvar.value) {
      throw new Error('No seqvar found')
    }
    if (variantResultSetStore.resultRow !== undefined) {
      await Promise.all([
        seqvarInfoStore.initialize(
          seqvar.value,
          variantResultSetStore.resultRow.payload!.hgnc_id,
        ),
        geneInfoStore.initialize(
          variantResultSetStore.resultRow.payload!.hgnc_id,
          seqvar.value.genomeBuild,
        ),
      ])
    }
  }
}

/** Watch change in properties to reload data. */
watch(
  () => props.resultRowUuid,
  async () => {
    console.log('watch: resultRowUuid changed')
    await refreshStores()
  },
)

watch(
  () => [
    variantResultSetStore.storeState.state,
    geneInfoStore.storeState,
    seqvarInfoStore.storeState,
    variantDetailsStore.storeState.state,
  ],
  () => {
    storesLoading.value = true
    const completeStoreStates = [StoreState.Active, StoreState.Error]
    const completeStates = [State.Active, State.Error]
    console.log('1', variantResultSetStore.storeState.state)
    console.log('2', geneInfoStore.storeState)
    console.log('3', seqvarInfoStore.storeState)
    console.log('4', variantDetailsStore.storeState.state)
    if (
      completeStates.includes(variantResultSetStore.storeState.state) &&
      completeStoreStates.includes(geneInfoStore.storeState) &&
      completeStoreStates.includes(seqvarInfoStore.storeState) &&
      completeStates.includes(variantDetailsStore.storeState.state)
    ) {
      storesLoading.value = false
      setTimeout(() => {
        document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
      }, 500)
    }
  },
)

watch(
  () => props.selectedSection,
  () => {
    setTimeout(() => {
      document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
    }, 0)
  },
)

/** When mounted, scroll to the selected element if any.
 */
onMounted(async () => {
  console.log('On mounted')
  await refreshStores()
})
</script>

<template>
  <v-app>
    <v-main>
      <v-container v-if="!storesLoading" fluid class="pa-0">
        <v-row no-gutters>
          <v-col cols="2" class="pr-3">
            <div style="position: sticky; top: 20px">
              <SeqvarDetailsNavi
                :seqvar="seqvarInfoStore.seqvar"
                :hgnc-id="geneInfoStore.geneInfo?.hgnc!.hgncId"
                :case-uuid="variantResultSetStore.caseUuid ?? undefined"
                :hide-back-button="props.hideBackButton"
              />
            </div>
          </v-col>
          <v-col cols="10">
            <div id="top" class="mt-6 mb-3 ml-1">
              <SeqvarDetailsHeader
                :seqvar="seqvarInfoStore.seqvar"
                :result-row-payload="variantResultSetStore?.resultRow?.payload"
              />
            </div>
            <template v-if="!seqvarInfoStore?.geneInfo">
              <div class="text-h5 mt-6 mb-3 ml-1">No Gene</div>
            </template>
            <template v-else>
              <div class="text-h5 mt-6 mb-3 ml-1">
                Gene
                <span class="font-italic">
                  {{ seqvarInfoStore?.geneInfo.hgnc!.symbol }}
                </span>
              </div>
              <div id="gene-overview">
                <GeneOverviewCard :gene-info="seqvarInfoStore?.geneInfo" />
              </div>
              <div id="gene-pathogenicity" class="mt-3">
                <GenePathogenicityCard :gene-info="seqvarInfoStore?.geneInfo" />
              </div>
              <div id="gene-conditions" class="mt-3">
                <GeneConditionsCard
                  :gene-info="seqvarInfoStore?.geneInfo"
                  :hpo-terms="seqvarInfoStore.hpoTerms"
                />
              </div>
              <div id="gene-expression" class="mt-3">
                <GeneExpressionCard
                  :gene-symbol="seqvarInfoStore?.geneInfo?.hgnc?.symbol"
                  :expression-records="seqvarInfoStore?.geneInfo?.gtex?.records"
                  :ensembl-gene-id="
                    seqvarInfoStore?.geneInfo?.gtex?.ensemblGeneId
                  "
                />
              </div>
              <div
                v-if="geneInfoStore?.geneClinvar && seqvar?.genomeBuild"
                id="gene-clinvar"
                class="mt-3"
              >
                <GeneClinvarCard
                  :clinvar-per-gene="geneInfoStore.geneClinvar"
                  :transcripts="geneInfoStore.transcripts"
                  :genome-build="seqvar.genomeBuild"
                  :gene-info="geneInfoStore.geneInfo"
                  :per-freq-counts="geneInfoStore?.geneClinvar?.perFreqCounts"
                />
              </div>
              <div id="gene-literature" class="mt-3 mb-3">
                <GeneLiteratureCard :gene-info="geneInfoStore.geneInfo" />
              </div>
            </template>

            <template v-if="!seqvarInfoStore.seqvar">
              <div class="text-h5 mt-6 mb-3 ml-1">No Variant Information</div>
            </template>
            <template v-else>
              <div class="text-h5 mt-6 mb-3 ml-1">Variant Details</div>
              <div id="seqvar-calldetails" class="mt-3">
                <SeqvarGenotypeCallCard
                  :result-row="variantResultSetStore.resultRow"
                />
              </div>
              <div id="seqvar-csq" class="mt-3">
                <SeqvarConsequencesCard :consequences="seqvarInfoStore.txCsq" />
              </div>
              <div id="seqvar-clinvar" class="mt-3">
                <SeqvarClinvarCard
                  :clinvar-records="seqvarInfoStore.varAnnos?.clinvar"
                />
              </div>
              <div id="seqvar-scores" class="mt-3">
                <SeqvarScoresCard :var-annos="seqvarInfoStore.varAnnos" />
              </div>
              <div id="seqvar-freqs" class="mt-3">
                <SeqvarFreqsCard
                  :seqvar="seqvarInfoStore.seqvar"
                  :var-annos="seqvarInfoStore.varAnnos"
                />
              </div>
              <div id="seqvar-tools" class="mt-3">
                <SeqvarToolsCard
                  :seqvar="seqvarInfoStore.seqvar"
                  :var-annos="seqvarInfoStore.varAnnos"
                />
              </div>
              <div id="seqvar-flags" class="mt-3">
                <FlagsCard
                  :flags-store="variantFlagsStore"
                  :variant="seqvarInfoStore.seqvar"
                  :result-row-uuid="props.resultRowUuid"
                  :case-uuid="caseDetailsStore.caseUuid ?? undefined"
                />
              </div>
              <div id="seqvar-comments" class="mt-3">
                <CommentsCard
                  :comments-store="variantCommentsStore"
                  :variant="seqvarInfoStore.seqvar"
                  :result-row-uuid="props.resultRowUuid"
                  :case-uuid="caseDetailsStore.caseUuid ?? undefined"
                />
              </div>
              <div id="seqvar-acmg" class="mt-3">
                <AcmgRatingCard
                  :project-uuid="props.projectUuid"
                  :case-uuid="variantResultSetStore.caseUuid ?? undefined"
                  :seqvar="seqvarInfoStore.seqvar"
                  :result-row-uuid="props.resultRowUuid"
                />
              </div>
              <div id="seqvar-ga4ghbeacons" class="mt-3">
                <SeqvarBeaconNetworkCard :seqvar="seqvarInfoStore.seqvar" />
              </div>
              <div id="seqvar-variantvalidator" class="mt-3">
                <SeqvarVariantValidatorCard :seqvar="seqvarInfoStore.seqvar" />
              </div>
            </template>
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else fluid class="pa-0">
        <v-row no-gutters>
          <v-col cols="12">
            <v-progress-linear indeterminate color="blue-lighten-1" />
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12">
            <v-alert
              dense
              outlined
              elevation="2"
              type="info"
              icon="mdi-information"
              class="m-3 text-light"
            >
              Loading variant details ...
            </v-alert>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

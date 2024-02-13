<script setup lang="ts">
/**
 * Detailed display of variant information.
 *
 * Used in the variant filtration app and displayed when the user selects a variant to display
 * the details for.
 *
 * Also used in the case details view for displyaing all user-annotated variants.
 *
 * See `SvDetails` for a peer app for structural variants
 */

import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { StoreState, seqvarInfo } from '@bihealth/reev-frontend-lib/stores'
import { useGeneInfoStore } from '@bihealth/reev-frontend-lib/stores/geneInfo'
import { useSeqvarInfoStore } from '@bihealth/reev-frontend-lib/stores/seqvarInfo'
import { Seqvar, SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { useVariantQueryStore } from '@variants/stores/variantQuery'
import { useVariantCommentsStore } from '@variants/stores/variantComments'
import { useVariantFlagsStore } from '@variants/stores/variantFlags'
import { useHistoryStore } from '@varfish/stores/history'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { useVariantResultSetStore } from '@variants/stores/variantResultSet'
import { State } from '@varfish/storeUtils'

import Header from '@variants/components/VariantDetails/Header.vue'
import VariantDetailsGene from '@variants/components/VariantDetails/Gene.vue'
import VariantDetailsClinvar from '@variants/components/VariantDetails/Clinvar.vue'
import VariantDetailsFreqs from '@variants/components/VariantDetails/Freqs.vue'
import CommentsCard from '@varfish/components/CommentsCard/CommentsCard.vue'
import FlagsCard from '@varfish/components/FlagsCard/FlagsCard.vue'
import SimpleCard from '@varfish/components/SimpleCard.vue'

import VariantDetailsCallDetails from '@variants/components/VariantDetails/CallDetails.vue'
import VariantDetailsConservation from '@variants/components/VariantDetails/Conservation.vue'
import VariantDetailsVariantTools from '@variants/components/VariantDetails/VariantTools.vue'
import VariantDetailsGa4ghBeacons from '@variants/components/VariantDetails/Ga4ghBeacons.vue'
import VariantDetailsTxCsq from '@variants/components/VariantDetails/TxCsq.vue'
import VariantDetailsVariantValidator from '@variants/components/VariantDetails/VariantValidator.vue'
import VariantDetailsAcmgRating from '@variants/components/VariantDetails/AcmgRating.vue'
import Overlay from '@varfish/components/Overlay.vue'
import { allNavItems } from '@variants/components/VariantDetails.fields'
import { watch } from 'vue'

const GeneOverviewCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GeneOverviewCard/GeneOverviewCard.vue'
    ),
)
const GenePathogenicityCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GenePathogenicityCard/GenePathogenicityCard.vue'
    ),
)
const GeneConditionsCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GeneConditionsCard/GeneConditionsCard.vue'
    ),
)
// const CadaRanking = defineAsyncComponent(() => import('@/components/CadaRanking/CadaRanking.vue'))
const GeneExpressionCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GeneExpressionCard/GeneExpressionCard.vue'
    ),
)
const GeneClinvarCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GeneClinvarCard/GeneClinvarCard.vue'
    ),
)
const GeneLiteratureCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/GeneLiteratureCard/GeneLiteratureCard.vue'
    ),
)

const SeqvarBeaconNetworkCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarBeaconNetworkCard/SeqvarBeaconNetworkCard.vue'
    ),
)
const SeqvarClinvarCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarClinvarCard/SeqvarClinvarCard.vue'
    ),
)
const SeqvarConsequencesCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarConsequencesCard/SeqvarConsequencesCard.vue'
    ),
)
const SeqvarFreqsCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarFreqsCard/SeqvarFreqsCard.vue'
    ),
)
const SeqvarToolsCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarToolsCard/SeqvarToolsCard.vue'
    ),
)
const SeqvarScoresCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarScoresCard/SeqvarScoresCard.vue'
    ),
)
const SeqvarVariantValidatorCard = defineAsyncComponent(
  () =>
    import(
      '@bihealth/reev-frontend-lib/components/SeqvarVariantValidatorCard/SeqvarVariantValidatorCard.vue'
    ),
)

/** This component's props. */
const props = defineProps<{
  /** UUID of the result row to display. */
  resultRowUuid?: string
  /** Identifier of the selected section. */
  selectedSection?: string
}>()

/** Obtain global application content (as for all entry level components) */
const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)

// Routing-related

const router = useRouter()

// Store-related

/** Information about the sequence variant, used to fetch information on load. */
const seqvarInfoStore = useSeqvarInfoStore()
/** Information about the affected gene, used to fetch information on load. */
const geneInfoStore = useGeneInfoStore()

const historyStore = useHistoryStore()

const caseDetailsStore = useCaseDetailsStore()
const variantResultSetStore = useVariantResultSetStore()
const variantDetailsStore = useVariantDetailsStore()
const queryStore = useVariantQueryStore()
const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const variantAcmgRatingStore = useVariantAcmgRatingStore()

/** Component state; use for opening sections by default. */
const openedSection = ref<string[]>(['gene', 'seqvar'])
/** Component state; any error message. */
const errorMessage = ref<string>('')
/** Component state; control snackbar display. */
const errSnackbarShow = ref<boolean>(false)
/** Component state; error message for snack bar. */
const errSnackbarMsg = ref<string>('')

/**
 * Handler for `@display-error` event.
 */
const handleDisplayError = async (msg: string) => {
  errSnackbarMsg.value = msg
  errSnackbarShow.value = true
}

const overlayShow = computed(() => {
  return (
    variantResultSetStore.storeState.state === State.Fetching ||
    variantDetailsStore.storeState.state === State.Fetching ||
    variantFlagsStore.storeState.state === State.Fetching ||
    variantCommentsStore.storeState.state === State.Fetching
  )
})

const overlayMessage = computed(() => {
  if (overlayShow.value) {
    return 'Loading...'
  } else {
    return ''
  }
})

const navItems = computed(() =>
  allNavItems.filter((navItem) => {
    if (navItem.name === 'beacon-network') {
      return queryStore.ga4ghBeaconNetworkWidgetEnabled
    } else {
      return true
    }
  }),
)

/** Event handler for clicking on the given tab.
 *
 * Will select the tab by pushing a route.
 */
const onTabClick = (selectedSection: string) => {
  router.push({
    name: 'variant-details',
    params: {
      row: props.resultRowUuid,
      selectedSection,
    },
  })
}

const navigateBack = () => {
  const dest = historyStore.lastWithDifferentName('variant-details')
  if (dest) {
    router.push(dest)
  } else {
    router.push(`/variants/filter/${caseDetailsStore.caseObj?.sodar_uuid}`)
  }
}

/** Currently displayed seqvar. */
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
/** HGVS description of SeqVar from result row. */
const seqvarHgvs = computed<string | undefined>(() => {
  if (!variantResultSetStore.resultRow?.payload) {
    return undefined
  } else {
    const arr = [variantResultSetStore.resultRow?.payload?.transcript_id]
    if (variantResultSetStore.resultRow?.payload?.symbol?.length) {
      arr.push(...['(', variantResultSetStore.resultRow?.payload?.symbol, ')'])
    }
    if (variantResultSetStore.resultRow?.payload?.hgvs_p?.length) {
      arr.push(
        ...[
          ':',
          variantResultSetStore.resultRow?.payload?.hgvs_p,
          ' (',
          variantResultSetStore.resultRow?.payload?.hgvs_c,
          ')',
        ],
      )
    } else {
      arr.push(...[':', variantResultSetStore.resultRow?.payload?.hgvs_c])
    }
    return arr.join('')
  }
})

/** Refresh the stores. */
const refreshStores = async () => {
  if (props.resultRowUuid && props.selectedSection) {
    await variantResultSetStore.initialize(appContext.csrf_token)
    await variantResultSetStore.fetchResultSetViaRow(props.resultRowUuid)
    await Promise.all([
      variantFlagsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        variantResultSetStore.caseUuid,
      ),
      variantCommentsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        variantResultSetStore.caseUuid,
      ),
      variantAcmgRatingStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        variantResultSetStore.caseUuid,
      ),
      variantDetailsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        variantResultSetStore.caseUuid,
      ),
    ])
    await variantDetailsStore.fetchVariantDetails(
      variantResultSetStore.resultRow,
    )
    // TODO: properly use types
    if (variantResultSetStore.resultRow !== undefined) {
      await Promise.all([
        seqvarInfoStore.initialize(seqvar.value),
        geneInfoStore.initialize(
          variantResultSetStore.resultRow.payload!.hgnc_id,
          seqvar.value.genomeBuild,
        ),
      ])
    }
  }

  document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
}

/** Watch change in properties to reload data. */
watch(
  () => [props.resultRowUuid, props.selectedSection],
  () => {
    refreshStores()
  },
)

/** When mounted, scroll to the selected element if any.
 */
onMounted(() => {
  refreshStores()
  document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
})
</script>

<template>
  <v-app>
    <div class="text-h4 mt-6 mb-3 ml-1">
      Variant Details
      <template v-if="seqvarHgvs">
        <small class="font-italic">
          {{ seqvarHgvs }}
          [{{ seqvar.userRepr }}]
        </small>
      </template>
      <template v-else>
        <small class="font-italic">
          {{ seqvar?.userRepr }}
        </small>
      </template>
    </div>
    <template v-if="!seqvarInfoStore?.geneInfo">
      <div class="text-h5 mt-6 mb-3 ml-1">No Gene</div>
    </template>
    <template v-else>
      <!-- <div class="text-h5 mt-6 mb-3 ml-1">
        Gene <span class="font-italic"> {{  seqvarInfoStore?.geneInfo.hgnc!.symbol }} </span>
      </div>
      <div id="gene-overview">
        <GeneOverviewCard :gene-info="seqvarInfoStore?.geneInfo" />
      </div>
      <div id="gene-pathogenicity" class="mt-3">
        <GenePathogenicityCard :gene-info="seqvarInfoStore?.geneInfo">
          <CadaRanking :hgnc-id="geneInfoStore.geneInfo?.hgnc!.hgncId" />
        </GenePathogenicityCard>
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
          :ensembl-gene-id="seqvarInfoStore?.geneInfo?.gtex?.ensemblGeneId"
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
      </div> -->
    </template>

    <template v-if="!seqvarInfoStore.seqvar">
      <div class="text-h5 mt-6 mb-3 ml-1">No Variant Information</div>
    </template>
    <template v-else>
      <!-- <div class="text-h5 mt-6 mb-3 ml-1">
        Variant Details
      </div>
      <div id="seqvar-clinsig">
      <SeqvarClinsigCard
          :seqvar="seqvarInfoStore.seqvar"
          @error-display="handleDisplayError"
        />
      </div>
      <div id="seqvar-csq" class="mt-3">
        <SeqvarConsequencesCard :consequences="seqvarInfoStore.txCsq" />
      </div>
      <div id="seqvar-clinvar" class="mt-3">
        <SeqvarClinvarCard :clinvar-record="seqvarInfoStore.varAnnos?.clinvar" />
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
      <div id="flags">
        <FlagsCard
          :flags-store="variantFlagsStore"
          :variant="seqvarInfoStore.seqvar"
        />
      </div> -->
      <div id="comments">
        <CommentsCard
          :comments-store="variantCommentsStore"
          :variant="seqvarInfoStore.seqvar"
        />
      </div>
      <!--
      <div id="seqvar-ga4ghbeacons" class="mt-3">
        <SeqvarBeaconNetworkCard :seqvar="seqvarInfoStore.seqvar" />
      </div>
      <div id="seqvar-variantvalidator" class="mt-3">
        <SeqvarVariantValidatorCard :seqvar="seqvarInfoStore.seqvar" />
      </div> -->
    </template>
  </v-app>
</template>

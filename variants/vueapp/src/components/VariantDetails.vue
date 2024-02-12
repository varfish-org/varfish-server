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

import { computed, defineAsyncComponent, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { StoreState } from '@bihealth/reev-frontend-lib/stores'
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
import VariantDetailsComments from '@varfish/components/VariantDetails/Comments.vue'
import VariantDetailsFlags from '@varfish/components/VariantDetails/Flags.vue'
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

/** Refresh the stores. */
const refreshStores = async () => {
  if (props.resultRowUuid && props.selectedSection) {
    await variantResultSetStore.initialize(appContext.csrf_token)
    await variantResultSetStore.fetchResultSetViaRow(props.resultRowUuid)
    console.log(
      'variantResultSetStore.resultRow',
      variantResultSetStore.resultRow,
    )
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
      const seqvar: Seqvar = new SeqvarImpl(
        variantResultSetStore.resultRow.release === 'GRCh37'
          ? 'grch37'
          : 'grch38',
        variantResultSetStore.resultRow.chromosome,
        variantResultSetStore.resultRow.start,
        variantResultSetStore.resultRow.reference,
        variantResultSetStore.resultRow.alternative,
      )
      await Promise.all([
        seqvarInfoStore.initialize(seqvar),
        geneInfoStore.initialize(
          variantResultSetStore.resultRow.payload!.hgnc_id,
          seqvar.genomeBuild,
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
    <GeneOverviewCard :gene-info="seqvarInfoStore?.geneInfo" />
  </v-app>

  <!--
  <div
    v-if="caseDetailsStore.caseObj && variantDetailsStore.smallVariant"
    class="d-flex flex-column h-100"
  >
    <Header
      :small-var="variantDetailsStore.smallVariant"
      :case="caseDetailsStore.caseObj"
    />
    <div class="container-fluid">
      <div class="row">
        <div
          class="col-10 pl-0 pr-0 pt-2"
          v-if="variantDetailsStore.smallVariant"
        >
          <div>
            <SimpleCard id="gene" title="Gene">
              <VariantDetailsGene
                :gene="variantDetailsStore.gene"
                :geneClinvar="variantDetailsStore.geneClinvar"
                :small-var="variantDetailsStore.smallVariant"
                :hgmd-pro-enabled="queryStore.hgmdProEnabled"
                :hgmd-pro-prefix="queryStore.hgmdProPrefix"
              />
            </SimpleCard>
            <SimpleCard
              id="beacon-network"
              title="Beacon Network"
              v-if="queryStore.ga4ghBeaconNetworkWidgetEnabled"
            >
              <VariantDetailsGa4ghBeacons
                :small-variant="variantDetailsStore.smallVariant"
              />
            </SimpleCard>
            <SimpleCard id="clinvar" title="ClinVar">
              <VariantDetailsClinvar />
            </SimpleCard>
            <SimpleCard id="freqs" title="Population Frequencies">
              <VariantDetailsFreqs
                :small-var="variantDetailsStore.smallVariant"
                :var-annos="variantDetailsStore.varAnnos"
              />
            </SimpleCard>
            <SimpleCard id="variant-tools" title="Variant Tools">
              <VariantDetailsVariantTools
                :small-var="variantDetailsStore.smallVariant"
                :var-annos="variantDetailsStore.varAnnos"
                :umd-predictor-api-token="queryStore.umdPredictorApiToken"
              />
            </SimpleCard>
            <SimpleCard id="tx-csq" title="Consequences">
              <VariantDetailsTxCsq :tx-csq="variantDetailsStore.txCsq" />
            </SimpleCard>
            <SimpleCard id="call-details" title="Call Details">
              <VariantDetailsCallDetails
                :case-description="caseDetailsStore.caseObj"
                :small-variant="variantDetailsStore.smallVariant?.payload"
              />
            </SimpleCard>
            <SimpleCard id="conservation" title="Conservation">
              <VariantDetailsConservation
                :var-annos="variantDetailsStore.varAnnos"
              />
            </SimpleCard>
            <SimpleCard id="flags" title="Flags">
              <VariantDetailsFlags
                :flags-store="variantFlagsStore"
                :variant="variantDetailsStore.smallVariant"
              />
            </SimpleCard>
            <SimpleCard id="comments" title="Comments">
              <VariantDetailsComments
                :comments-store="variantCommentsStore"
                :variant="variantDetailsStore.smallVariant"
              />
            </SimpleCard>
            <SimpleCard id="acmg-rating" title="ACMG Rating">
              <VariantDetailsAcmgRating
                :small-variant="variantDetailsStore.smallVariant"
              />
            </SimpleCard>
            <SimpleCard id="second-hit" title="Second Hit">
              <div class="alert alert-secondary">
                <i-mdi-clock />
                Work in progress ...
              </div>
            </SimpleCard>
            <SimpleCard id="other-carriers" title="OtherCarriers">
              <div class="alert alert-secondary">
                <i-mdi-clock />
                Work in progress ...
              </div>
            </SimpleCard>
            <SimpleCard id="variant-validator" title="VariantValidator">
              <VariantDetailsVariantValidator
                :small-variant="variantDetailsStore.smallVariant"
              />
            </SimpleCard>
          </div>
          <Overlay v-if="overlayShow" :message="overlayMessage" />
        </div>

        <div class="col-2 pr-0">
          <ul
            class="nav flex-column nav-pills position-sticky pt-2"
            style="top: 0px"
          >
            <li class="nav-item mt-0 mb-3">
              <a
                class="nav-link user-select-none btn btn-secondary"
                @click.prevent="navigateBack()"
                type="button"
              >
                <i-mdi-arrow-left-circle />
                Back
              </a>
            </li>
            <li class="nav-item mt-0" v-for="{ name, title } in navItems">
              <a
                class="nav-link user-select-none"
                :class="{ active: props.selectedSection === name }"
                @click="onTabClick(name)"
                type="button"
              >
                {{ title }}
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  -->
</template>

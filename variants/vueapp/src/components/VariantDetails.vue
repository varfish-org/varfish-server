<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useVariantDetailsStore } from '@variants/stores/variantDetails.js'
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'
import { useVariantCommentsStore } from '@variants/stores/variantComments.js'
import { useVariantFlagsStore } from '@variants/stores/variantFlags.js'

import VariantDetailsGene from './VariantDetailsGene.vue'
import VariantDetailsClinvar from './VariantDetailsClinvar.vue'
import VariantDetailsFreqs from './VariantDetailsFreqs.vue'
import VariantDetailsComments from '@varfish/components/VariantDetailsComments.vue'
import VariantDetailsFlags from '@varfish/components/VariantDetailsFlags.vue'
import SimpleCard from '@varfish/components/SimpleCard.vue'

import VariantDetailsCallDetails from './VariantDetailsCallDetails.vue'
import VariantDetailsConservation from './VariantDetailsConservation.vue'
import VariantDetailsPrecomputedScores from './VariantDetailsPrecomputedScores.vue'
import VariantDetailsGa4ghBeacons from './VariantDetailsGa4ghBeacons.vue'
import VariantDetailsTxCsq from './VariantDetailsTxCsq.vue'
import VariantDetailsVariantValidator from './VariantDetailsVariantValidator.vue'
import VariantDetailsAcmgRating from './VariantDetailsAcmgRating.vue'
import VariantDetailsLinkOuts from './VariantDetailsLinkOuts.vue'

import { allNavItems } from './VariantDetails.fields'

const props = defineProps<{
  resultRowUuid?: string
  selectedTab?: string
}>()

const route = useRoute()
const router = useRouter()

const detailsStore = useVariantDetailsStore()
const queryStore = useFilterQueryStore()
const flagsStore = useVariantFlagsStore()
const commentsStore = useVariantCommentsStore()
commentsStore.initialize(
  { csrf_token: queryStore.csrfToken },
  queryStore.caseUuid
)

const navItems = allNavItems.filter((navItem) => {
  if (navItem.name === 'beacon-network') {
    return queryStore.ga4ghBeaconNetworkWidgetEnabled
  } else {
    return true
  }
})

/** Event handler for clicking on the given tab.
 *
 * Will select the tab by pushing a route.
 */
const onTabClick = (selectedTab: string) => {
  router.push({
    name: 'variants-filter-details',
    params: {
      case: queryStore.caseUuid,
      query: queryStore.previousQueryDetails.sodar_uuid,
      row: props.resultRowUuid,
      selectedTab,
    },
  })
}

/** When mounted, scroll to the selected element if any.
 */
onMounted(() => {
  document.querySelector(`#${route.params.selectedTab}`)?.scrollIntoView()
})
</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-10 pl-0 pr-0 pt-2">
        <SimpleCard id="link-outs" title="Link-Outs">
          <VariantDetailsLinkOuts
            :gene="detailsStore.gene"
            :small-variant="detailsStore.smallVariant"
            :hgmd-pro-enabled="queryStore.hgmdProEnabled"
            :hgmd-pro-prefix="queryStore.hgmdProPrefix"
          />
        </SimpleCard>
        <SimpleCard id="gene" title="Gene">
          <VariantDetailsGene
            :gene="detailsStore.gene"
            :small-var="detailsStore.smallVariant"
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
            :small-variant="detailsStore.smallVariant"
          />
        </SimpleCard>
        <SimpleCard id="clinvar" title="ClinVar">
          <VariantDetailsClinvar />
        </SimpleCard>
        <SimpleCard id="freqs" title="Population Frequencies">
          <VariantDetailsFreqs
            :small-var="detailsStore.smallVariant"
            :var-annos="detailsStore.varAnnos"
          />
        </SimpleCard>
        <SimpleCard id="precomputed-scores" title="Precomputed Scores">
          <VariantDetailsPrecomputedScores :var-annos="detailsStore.varAnnos" />
        </SimpleCard>
        <SimpleCard id="tx-csq" title="Consequences">
          <VariantDetailsTxCsq :tx-csq="detailsStore.txCsq" />
        </SimpleCard>
        <SimpleCard id="call-details" title="Call Details">
          <VariantDetailsCallDetails
            :case-description="queryStore.caseObj"
            :small-variant="detailsStore.smallVariant"
          />
        </SimpleCard>
        <SimpleCard id="conservation" title="Conservation">
          <VariantDetailsConservation
            :var-annos="detailsStore.varAnnos"
          />
        </SimpleCard>
        <SimpleCard id="flags" title="Flags">
          <VariantDetailsFlags
            :details-store="detailsStore"
            :flags-store="flagsStore"
            :variant="detailsStore.smallVariant"
          />
        </SimpleCard>
        <SimpleCard id="comments" title="Comments">
          <VariantDetailsComments
            :details-store="detailsStore"
            :comments-store="commentsStore"
            :variant="detailsStore.smallVariant"
          />
        </SimpleCard>
        <SimpleCard id="acmg-rating" title="ACMG Rating">
          <VariantDetailsAcmgRating />
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
            :small-variant="detailsStore.smallVariant"
            v-model:variant-validator-state="detailsStore.variantValidatorState"
            v-model:variant-validator-results="
              detailsStore.variantValidatorResults
            "
          />
        </SimpleCard>
      </div>

      <div class="col-2">
        <ul
          class="nav flex-column nav-pills position-sticky pt-2"
          style="top: 0px"
        >
          <li class="nav-item mt-0" v-for="{ name, title } in navItems">
            <a
              class="nav-link user-select-none"
              :class="{ active: props.selectedTab === name }"
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
</template>

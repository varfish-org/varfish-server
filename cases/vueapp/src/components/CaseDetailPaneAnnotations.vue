<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import variantsApi from '@variants/api/variants.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useVariantDetailsStore } from '@variants/stores/variantDetails.js'
import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
} from '@variants/enums.js'
import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
import VariantDetailsModalWrapper from '@variants/components/VariantDetailsModalWrapper.vue'
import Overlay from '@varfish/components/Overlay.vue'

/** The details columns to show. */
const displayDetails = ref(DisplayDetails.Coordinates.value)
/** The frequency columns to show. */
const displayFrequency = ref(DisplayFrequencies.GnomadExomes.value)
/** The constraint columns to show. */
const displayConstraint = ref(DisplayConstraints.GnomadPli.value)
/** The additional columns to display. */
const displayColumns = ref([DisplayColumns.Effect.value])
/** The fields defined by extraAnnos. */
const extraAnnoFields = ref([])

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()

const currentSmallVariant = ref(null)

const smallVariantDetailsModalWrapperRef = ref(null)

const variantDetailsStore = useVariantDetailsStore()

const filterQueryStore = useFilterQueryStore()

const previousQueryDetails = ref(null)

const props = defineProps({
  /** Whether to show the variant details modal. */
  variantDetailsModalVisible: Boolean,
  /** The UUID of the result row to show in details modal. */
  variantDetailsModalResultRowUuid: String,
  /** Which tab to show in the variant details modal. */
  variantDetailsModalSelectedTab: String,
})

/** The currently used route. */
const route = useRoute()
/** The currently used router. */
const router = useRouter()

const showModal = async (event) => {
  router.push({
    name: 'case-detail-variant-detail',
    params: {
      case: caseDetailsStore.caseObj.sodar_uuid,
      row: event.smallvariantresultrow,
      selectedTab: event.selectedTab ?? null,
    },
  })
}

onMounted(async () => {
  const csrfToken = casesStore.appContext.csrfToken
  const apiQueryResults = await variantsApi.listCaseVariantsUserAnnotated(
    csrfToken,
    caseDetailsStore.caseObj.sodar_uuid
  )
  filterQueryStore.queryResults = apiQueryResults.rows
})
</script>

<template>
  <div class="row pt-3 pb-3 flex-grow-1 d-flex flex-column">
    <div class="col flex-grow-1 d-flex flex-column">
      <h5>User Annotations</h5>

      <template v-if="filterQueryStore.queryResults">
        <FilterResultsTable
          :case="caseDetailsStore.caseObj"
          :query-result-set="caseDetailsStore.caseObj.smallvariantqueryresultset"
          :extra-anno-fields="extraAnnoFields"
          v-model:display-details="displayDetails"
          v-model:display-frequency="displayFrequency"
          v-model:display-constraint="displayConstraint"
          v-model:display-columns="displayColumns"
          @variant-selected="showModal"
        />
      </template>
      <Overlay v-else />
    </div>

    <VariantDetailsModalWrapper
      ref="smallVariantDetailsModalWrapperRef"
      :visible="props.variantDetailsModalVisible"
      :result-row-uuid="props.variantDetailsModalResultRowUuid"
      :selected-tab="props.variantDetailsModalSelectedTab"
    />
  </div>
</template>

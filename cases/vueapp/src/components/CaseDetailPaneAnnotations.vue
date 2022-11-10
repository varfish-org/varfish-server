<script setup>
import { ref, onMounted, reactive } from 'vue'

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
import Overlay from '@cases/components/Overlay.vue'

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

const previousQueryDetails = ref(null)

const showModal = ({ gridRow, gridApi, smallVariant }) => {
  currentSmallVariant.value = smallVariant
  smallVariantDetailsModalWrapperRef.value.showModal()
  variantDetailsStore.fetchVariantDetails(
    { gridRow, gridApi, smallVariant },
    'refseq'
  )
}

const filterQueryStore = useFilterQueryStore()

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
          :query-results="filterQueryStore.queryResults"
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
      :small-variant="currentSmallVariant"
      :fetched="variantDetailsStore.fetched"
    />
  </div>
</template>

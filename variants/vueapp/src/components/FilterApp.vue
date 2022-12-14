<script setup>
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'
import { useVariantDetailsStore } from '@variants/stores/variantDetails.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
import { watch, ref, onMounted, nextTick } from 'vue'
import { updateUserSetting } from '@varfish/user-settings.js'
import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
  QueryStates,
  QueryStateToText,
} from '@variants/enums'

import VariantDetailsModalWrapper from './VariantDetailsModalWrapper.vue'
import FilterAppHeader from './FilterAppHeader.vue'
import FilterForm from './FilterForm.vue'
import FilterResultsTable from './FilterResultsTable.vue'

const components = {
  VariantDetailsModalWrapper,
  FilterForm,
  FilterResultsTable,
}

const currentSmallVariant = ref(null)

const smallVariantDetailsModalWrapperRef = ref(null)

const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}'
)

const variantDetailsStore = useVariantDetailsStore()
variantDetailsStore.initialize(appContext)

// Initialize filter query store.
const filterQueryStore = useFilterQueryStore()
filterQueryStore.initialize(appContext)
// Initialize cases store.
const casesStore = useCasesStore()
casesStore.initialize(appContext)
// Initialize case details store.
const caseDetailsStore = useCaseDetailsStore()
caseDetailsStore.initialize(appContext.case_uuid)

const showModal = ({ gridRow, gridApi, smallVariant }) => {
  currentSmallVariant.value = smallVariant
  smallVariantDetailsModalWrapperRef.value.showModal()
  variantDetailsStore.fetchVariantDetails(
    gridRow,
    gridApi,
    smallVariant,
    filterQueryStore.previousQueryDetails.query_settings.database_select
  )
}

/** Whether the form is visible. */
const formVisible = ref(true)
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
/** Whether the query logs are visible. */
const queryLogsVisible = ref(false)

// Toggle visibility of the form.
const toggleForm = () => {
  formVisible.value = !formVisible.value
}

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => filterQueryStore.showFiltrationInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== oldValue) {
      updateUserSetting(
        filterQueryStore.csrfToken,
        'vueapp.filtration_inline_help',
        newValue
      )
    }
    $('#vueapp-filtration-inline-help').prop('checked', newValue)
  }
)
watch(
  () => filterQueryStore.filtrationComplexityMode,
  (newValue, oldValue) => {
    if (newValue !== oldValue) {
      updateUserSetting(
        filterQueryStore.csrfToken,
        'vueapp.filtration_complexity_mode',
        newValue
      )
    }
    $('#vueapp-filtration-complexity-mode').val(newValue).change()
  }
)

// Vice versa.
onMounted(() => {
  const handleUpdate = () => {
    const filterQueryStore = useFilterQueryStore()
    filterQueryStore.showFiltrationInlineHelp = $(
      '#vueapp-filtration-inline-help'
    ).prop('checked')
    filterQueryStore.filtrationComplexityMode = $(
      '#vueapp-filtration-complexity-mode'
    ).val()
  }
  nextTick(() => {
    handleUpdate()
    $('#vueapp-filtration-inline-help').change(handleUpdate)
    $('#vueapp-filtration-complexity-mode').change(handleUpdate)
  })
})
</script>

<template>
  <div
    v-if="filterQueryStore.caseObj !== null"
    class="d-flex flex-column h-100"
  >
    <!-- title etc. -->
    <FilterAppHeader :form-visible="formVisible" @toggle-form="toggleForm()" />

    <!-- query form -->
    <div v-if="formVisible" class="container-fluid sodar-page-container pt-0">
      <div
        v-if="filterQueryStore.showFiltrationInlineHelp"
        class="alert alert-secondary small p-2"
      >
        <i-mdi-information />
        This is the variant filtration form. You can use the form controls below
        to adjust your filter criteria. The results of your previous query will
        be loaded automatically if there are any. You can toggle these gray
        boxes with verbose information using the
        <span class="badge badge-primary">
          <i-mdi-toggle-switch-outline style="scale: 200%" class="mr-2 ml-1" />
          <i-fa-solid-info />
        </span>
        switch on the top. You can change between simpler and more
        complex/powerful forms using the
        <span class="badge badge-primary">
          <i-mdi-form-dropdown style="scale: 150%" class="mr-2 ml-1" />
          <i-mdi-podium />
        </span>
        input next to it.
        <strong>
          Click the
          <span class="badge badge-primary">
            <i-mdi-refresh />
            Filter &amp; Display
          </span>
          when you are ready!
        </strong>
      </div>

      <FilterForm v-model:store="filterQueryStore" />
    </div>

    <!-- table to fill when query finished -->
    <div
      v-if="filterQueryStore.queryState === QueryStates.Fetched.value"
      class="flex-grow-1 mb-2"
    >
      <FilterResultsTable
        :case="filterQueryStore.caseObj"
        :query-results="filterQueryStore.queryResults"
        :extra-anno-fields="extraAnnoFields"
        v-model:display-details="displayDetails"
        v-model:display-frequency="displayFrequency"
        v-model:display-constraint="displayConstraint"
        v-model:display-columns="displayColumns"
        @variant-selected="showModal"
      />
    </div>
    <div
      v-else-if="
        [
          QueryStates.Running.value,
          QueryStates.Resuming.value,
          QueryStates.Finished.value,
          QueryStates.Fetching.value,
        ].includes(filterQueryStore.queryState)
      "
      class="alert alert-info"
    >
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2"
        >{{ QueryStateToText[filterQueryStore.queryState] }} ...</strong
      >
      <button
        class="ml-3 btn btn-sm btn-info"
        @click="queryLogsVisible = !queryLogsVisible"
      >
        {{ queryLogsVisible ? 'Hide' : 'Show' }} Logs
      </button>
      <pre v-show="queryLogsVisible">{{
        filterQueryStore.queryLogs?.join('\n')
      }}</pre>
    </div>
    <div v-else class="alert alert-info">
      <strong>
        <template
          v-if="filterQueryStore.queryState === QueryStates.Initial.value"
        >
          No query has been started yet.
        </template>
        <template
          v-else-if="
            filterQueryStore.queryState === QueryStates.Cancelled.value
          "
        >
          The query has been canceled.
        </template>
        <template
          v-if="filterQueryStore.queryState === QueryStates.Error.value"
        >
          An error has occured in the query!
        </template>
      </strong>
      <div>
        Click
        <span class="badge badge-primary">
          <i-mdi-refresh />
          Filter &amp; Display
        </span>
        to start filtering and create results to display here. You may want to
        adjust the filter settings to your needs first.
      </div>
    </div>
  </div>
  <div v-else class="alert alert-info">
    <i-fa-solid-circle-notch class="spin" />
    <strong class="pl-2">Loading site ...</strong>
  </div>

  <VariantDetailsModalWrapper
    ref="smallVariantDetailsModalWrapperRef"
    :small-variant="currentSmallVariant"
    :fetched="variantDetailsStore.fetched"
  />
</template>

<style scoped></style>

<script setup>
import { watch, ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import { useSvFilterStore } from '@svs/stores/filterSvs.js'
import { useSvDetailsStore } from '@svs/stores/detailsSv.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
import { updateUserSetting } from '@varfish/user-settings.js'
import { QueryStates, QueryStateToText } from '@variants/enums'

import SvFilterAppHeader from './SvFilterAppHeader.vue'
import SvFilterForm from './SvFilterForm.vue'
import SvFilterResultsTable from './SvFilterResultsTable.vue'
import SvDetailsModalWrapper from './SvDetailsModalWrapper.vue'

const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}'
)

/** The currently used route. */
const route = useRoute()

/** The currently displayed case's UUID, updated from route. */
const caseUuidRef = ref(route.params.case)

// Initialize filter query store.
const svFilterStore = useSvFilterStore()
svFilterStore.initialize(appContext, caseUuidRef.value)
// Initialize SV details store.
const svDetailsStore = useSvDetailsStore()
svDetailsStore.initialize(appContext)
// Initialize cases store.
const casesStore = useCasesStore()
casesStore.initialize(appContext)
// Initialize case details store.
const caseDetailsStore = useCaseDetailsStore()
caseDetailsStore.initialize(caseUuidRef.value)

/** Whether the form is visible. */
const formVisible = ref(true)
/** Whether the query logs are visible. */
const queryLogsVisible = ref(false)

// Toggle visibility of the form.
const toggleForm = () => {
  formVisible.value = !formVisible.value
}

// Ref to modal used to show the SV details
const svDetailsModalWrapperRef = ref(null)

// Display modal for the given variant. */
const showModal = (svRecord) => {
  svDetailsModalWrapperRef.value.showModal()
  svDetailsStore.fetchSvDetails(
    svRecord,
    svFilterStore.previousQueryDetails.query_settings.database
  )
}

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => svFilterStore.showFiltrationInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== oldValue) {
      updateUserSetting(
        svFilterStore.csrfToken,
        'vueapp.filtration_inline_help',
        newValue
      )
    }
    $('#vueapp-filtration-inline-help').prop('checked', newValue)
  }
)
watch(
  () => svFilterStore.filtrationComplexityMode,
  (newValue, oldValue) => {
    if (newValue !== oldValue) {
      updateUserSetting(
        svFilterStore.csrfToken,
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
    const svFilterStore = useSvFilterStore()
    svFilterStore.showFiltrationInlineHelp = $(
      '#vueapp-filtration-inline-help'
    ).prop('checked')
    svFilterStore.filtrationComplexityMode = $(
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
  <div v-if="svFilterStore.caseObj !== null" class="d-flex flex-column h-100">
    <!-- title etc. -->
    <SvFilterAppHeader
      :form-visible="formVisible"
      @toggle-form="toggleForm()"
    />

    <!-- query form -->
    <div v-if="formVisible" class="container-fluid sodar-page-container pt-0">
      <div
        v-if="svFilterStore.showFiltrationInlineHelp"
        class="alert alert-secondary small p-2"
      >
        <i-mdi-information />
        This is the SV filtration form. You can use the form controls below to
        adjust your filter criteria. The results of your previous query will be
        loaded automatically if there are any. You can toggle these gray boxes
        with verbose information using the
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

      <SvFilterForm v-model:store="svFilterStore" />
    </div>

    <!-- table to fill when query finished -->
    <div
      v-if="svFilterStore.queryState === QueryStates.Fetched.value"
      class="flex-grow-1 mb-2"
    >
      <SvFilterResultsTable
        :case-obj="svFilterStore.caseObj"
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
        ].includes(svFilterStore.queryState)
      "
      class="alert alert-info"
    >
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2"
        >{{ QueryStateToText[svFilterStore.queryState] }} ...</strong
      >
      <button
        class="ml-3 btn btn-sm btn-info"
        @click="queryLogsVisible = !queryLogsVisible"
      >
        {{ queryLogsVisible ? 'Hide' : 'Show' }} Logs
      </button>
      <pre v-show="queryLogsVisible">{{
        svFilterStore.queryLogs?.join('\n')
      }}</pre>
    </div>
    <div v-else class="alert alert-info">
      <strong>
        <template v-if="svFilterStore.queryState === QueryStates.None.value">
          No query has been submitted to the server yet.
        </template>
        <template v-if="svFilterStore.queryState === QueryStates.Initial.value">
          The query is sitting in the queue.
        </template>
        <template
          v-else-if="svFilterStore.queryState === QueryStates.Cancelled.value"
        >
          The query has been canceled.
        </template>
        <template v-if="svFilterStore.queryState === QueryStates.Error.value">
          An error has occured in the query!
          {{ svFilterStore.queryStateMsg }}
        </template>
        <template v-if="svFilterStore.queryState === QueryStates.Timeout.value">
          The query has been terminated after running too long.
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

  <SvDetailsModalWrapper
    ref="svDetailsModalWrapperRef"
    :sv-record="svDetailsStore.currentSvRecord"
    :fetched="svDetailsStore.fetched"
  />
</template>

<style scoped></style>

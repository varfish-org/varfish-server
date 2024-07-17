<script setup>
import $ from 'jquery'
import { watch, ref, onMounted, nextTick, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'

import { State } from '@/varfish/storeUtils'
import { useSvQueryStore } from '@/svs/stores/svQuery'
import { useSvResultSetStore } from '@/svs/stores/svResultSet'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { updateUserSetting } from '@/varfish/userSettings'
import { QueryStates, QueryStateToText } from '@/variants/enums'

import SvFilterForm from '@/svs/components/SvFilterForm.vue'
import SvFilterResultsTable from '@/svs/components/SvFilterResultsTable.vue'
import { useSvFlagsStore } from '@/svs/stores/strucvarFlags'
import { useSvCommentsStore } from '@/svs/stores/svComments'
import { useSvAcmgRatingStore } from '@/svs/stores/svAcmgRating'
import { useCtxStore } from '@/varfish/stores/ctx'

const props = defineProps({
  /** The project UUID. */
  projectUuid: String,
  /** The case UUID. */
  caseUuid: String,
})

const router = useRouter()

const ctxStore = useCtxStore()
const svQueryStore = useSvQueryStore()
const svFlagsStore = useSvFlagsStore()
const svCommentsStore = useSvCommentsStore()
const svAcmgRatingStore = useSvAcmgRatingStore()
const caseDetailsStore = useCaseDetailsStore()
const svResultSetStore = useSvResultSetStore()

const showDetails = async (event) => {
  svQueryStore.lastPosition = document.querySelector('div#app').scrollTop
  router.push({
    name: 'strucvar-details',
    params: {
      row: event.svresultrow,
      selectedSection: event.selectedSection ?? null,
    },
  })
}

/** Whether the form is visible. */
const filterFormVisible = defineModel('filterFormVisible', {
  type: Boolean,
  default: true,
})
/** Whether the query logs are visible. */
const queryLogsVisible = defineModel('queryLogsVisible', {
  type: Boolean,
  default: true,
})

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => svQueryStore.showFiltrationInlineHelp,
  (newValue, oldValue) => {
    if (
      newValue !== undefined &&
      newValue !== null &&
      newValue !== oldValue &&
      ctxStore.csrfToken
    ) {
      updateUserSetting(
        ctxStore.csrfToken,
        'vueapp.filtration_inline_help',
        newValue,
      )
    }
    $('#vueapp-filtration-inline-help').prop('checked', newValue)
  },
)
watch(
  () => svQueryStore.filtrationComplexityMode,
  (newValue, oldValue) => {
    if (
      newValue !== null &&
      newValue !== undefined &&
      newValue !== oldValue &&
      ctxStore.csrfToken
    ) {
      updateUserSetting(
        ctxStore.csrfToken,
        'vueapp.filtration_complexity_mode',
        newValue,
      )
    }
    $('#vueapp-filtration-complexity-mode').val(newValue).change()
  },
)

// Vice versa.
onMounted(() => {
  const handleUpdate = () => {
    const svQueryStore = useSvQueryStore()
    svQueryStore.showFiltrationInlineHelp = $(
      '#vueapp-filtration-inline-help',
    ).prop('checked')
    svQueryStore.filtrationComplexityMode = $(
      '#vueapp-filtration-complexity-mode',
    ).val()
  }
  nextTick(() => {
    handleUpdate()
    $('#vueapp-filtration-inline-help').change(handleUpdate)
    $('#vueapp-filtration-complexity-mode').change(handleUpdate)
  })
})

/** Refresh the stores. */
const refreshStores = async () => {
  if (!props.caseUuid) {
    return
  }

  // Reset all stores to avoid artifacts.
  svQueryStore.$reset()

  await caseDetailsStore.initialize(props.projectUuid, props.caseUuid)
  Promise.all([
    svFlagsStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    svCommentsStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    svQueryStore.initialize(props.projectUuid, props.caseUuid),
    svAcmgRatingStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    svResultSetStore.initialize(),
  ]).then(async () => {
    if (svQueryStore.queryUuid) {
      await svResultSetStore.loadResultSetViaQuery(svQueryStore.queryUuid)
    }
  })
}

// Initialize (=refresh) stores when mounted.
onBeforeMount(() => refreshStores())

// Refresh stores when the case UUID changes.
watch(
  () => props.caseUuid,
  () => refreshStores(),
)
</script>

<template>
  <div
    v-if="svQueryStore.storeState.state === State.Active"
    class="d-flex flex-column h-100 mx-3"
  >
    <!-- query form -->
    <div
      v-if="filterFormVisible"
      class="container-fluid sodar-page-container p-0 mb-2"
    >
      <div
        v-if="svQueryStore.showFiltrationInlineHelp"
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

      <SvFilterForm v-model:store="svQueryStore" />
    </div>

    <!-- table to fill when query finished -->
    <div
      v-if="svQueryStore.queryState === QueryStates.Fetched.value"
      class="flex-grow-1 mb-2"
    >
      <pre v-show="queryLogsVisible">{{
        svQueryStore.queryLogs?.join('\n')
      }}</pre>
      <SvFilterResultsTable @variant-selected="showDetails" />
    </div>
    <div
      v-else-if="
        [
          QueryStates.Running.value,
          QueryStates.Resuming.value,
          QueryStates.Finished.value,
          QueryStates.Fetching.value,
        ].includes(svQueryStore.queryState)
      "
      class="alert alert-info"
    >
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2"
        >{{ QueryStateToText[svQueryStore.queryState] }} ...</strong
      >
      <pre>{{ svQueryStore.queryLogs?.join('\n') }}</pre>
    </div>
    <div v-else class="alert alert-info">
      <strong>
        <template v-if="svQueryStore.queryState === QueryStates.None.value">
          No query has been submitted to the server yet.
        </template>
        <template v-if="svQueryStore.queryState === QueryStates.Initial.value">
          The query is sitting in the queue.
        </template>
        <template
          v-else-if="svQueryStore.queryState === QueryStates.Cancelled.value"
        >
          The query has been canceled.
        </template>
        <template v-if="svQueryStore.queryState === QueryStates.Error.value">
          An error has occurred in the query!
          {{ svQueryStore.queryStateMsg }}
        </template>
        <template v-if="svQueryStore.queryState === QueryStates.Timeout.value">
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
  <div v-else class="alert alert-info m-3">
    <i-fa-solid-circle-notch class="spin" />
    <strong class="pl-2">Loading site ...</strong>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

<script setup>
import $ from 'jquery'
import { watch, onMounted, nextTick, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'

import { State } from '@/varfish/storeUtils'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
import { useVariantCommentsStore } from '@/variants/stores/variantComments'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCtxStore } from '@/varfish/stores/ctx'
import { updateUserSetting } from '@/varfish/userSettings'
import { QueryStates, QueryStateToText } from '@/variants/enums'

import FilterForm from '@/variants/components/FilterForm.vue'
import FilterResultsTable from '@/variants/components/FilterResultsTable.vue'

const props = defineProps({
  /** The project UUID. */
  projectUuid: String,
  /** The case UUID. */
  caseUuid: String,
})

const ctxStore = useCtxStore()

const router = useRouter()

const variantQueryStore = useVariantQueryStore()
const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const variantAcmgRatingStore = useVariantAcmgRatingStore()
const caseDetailsStore = useCaseDetailsStore()
const variantResultSetStore = useVariantResultSetStore()

const showDetails = async (event) => {
  variantQueryStore.lastPosition = document.querySelector('div#app').scrollTop
  router.push({
    name: 'seqvar-details',
    params: {
      row: event.smallvariantresultrow,
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
  () => variantQueryStore.showFiltrationInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== undefined && newValue !== null && newValue !== oldValue) {
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
  () => variantQueryStore.filtrationComplexityMode,
  (newValue, oldValue) => {
    if (newValue !== null && newValue !== undefined && newValue !== oldValue) {
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
    const variantQueryStore = useVariantQueryStore()
    variantQueryStore.showFiltrationInlineHelp = $(
      '#vueapp-filtration-inline-help',
    ).prop('checked')
    variantQueryStore.filtrationComplexityMode = $(
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
  variantQueryStore.$reset()
  variantFlagsStore.$reset()
  variantCommentsStore.$reset()
  variantAcmgRatingStore.$reset()
  // Do not reset the result set store, as we need to keep the table settings when returning from
  // variant details.

  await caseDetailsStore.initialize(props.projectUuid, props.caseUuid)

  await Promise.all([
    variantQueryStore.initialize(props.projectUuid, props.caseUuid),
    variantFlagsStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantCommentsStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantAcmgRatingStore.initialize(
      props.projectUuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantResultSetStore.initialize(),
  ])
  if (variantQueryStore.queryUuid) {
    await variantResultSetStore.loadResultSetViaQuery(
      variantQueryStore.queryUuid,
    )
  }
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
    v-if="variantQueryStore.storeState.state === State.Active"
    class="d-flex flex-column h-100 mx-3"
  >
    <!-- query form -->
    <div
      v-if="filterFormVisible"
      class="container-fluid sodar-page-container p-0 mb-2"
    >
      <div
        v-if="variantQueryStore.showFiltrationInlineHelp"
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

      <FilterForm v-model:store="variantQueryStore" />
    </div>

    <!-- table to fill when query finished -->
    <div
      v-if="variantQueryStore.queryState === QueryStates.Fetched.value"
      class="flex-grow-1 mb-2"
    >
      <pre v-show="queryLogsVisible">{{
        variantQueryStore.queryLogs?.join('\n')
      }}</pre>
      <FilterResultsTable
        :patho-enabled="
          variantQueryStore.previousQueryDetails.query_settings.patho_enabled
        "
        :prio-enabled="
          variantQueryStore.previousQueryDetails.query_settings.prio_enabled
        "
        @variant-selected="showDetails"
      />
    </div>
    <div
      v-else-if="
        [
          QueryStates.Running.value,
          QueryStates.Resuming.value,
          QueryStates.Finished.value,
          QueryStates.Fetching.value,
        ].includes(variantQueryStore.queryState)
      "
      class="alert alert-info"
    >
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2"
        >{{ QueryStateToText[variantQueryStore.queryState] }} ...</strong
      >
      <pre>{{ variantQueryStore.queryLogs?.join('\n') }}</pre>
    </div>
    <div v-else class="alert alert-info">
      <strong>
        <template
          v-if="variantQueryStore.queryState === QueryStates.Initial.value"
        >
          No query has been started yet.
        </template>
        <template
          v-else-if="
            variantQueryStore.queryState === QueryStates.Cancelled.value
          "
        >
          The query has been canceled.
        </template>
        <template
          v-if="variantQueryStore.queryState === QueryStates.Error.value"
        >
          An error has occurred in the query!
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

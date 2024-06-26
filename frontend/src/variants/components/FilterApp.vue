<script setup>
import { watch, ref, onMounted, nextTick, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'

import { State } from '@/varfish/storeUtils'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
import { useVariantCommentsStore } from '@/variants/stores/variantComments'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { updateUserSetting } from '@/varfish/userSettings'
import { QueryStates, QueryStateToText } from '@/variants/enums'

import Header from '@/variants/components/FilterApp/Header.vue'
import FilterForm from '@/variants/components/FilterForm.vue'
import FilterResultsTable from '@/variants/components/FilterResultsTable.vue'

const props = defineProps({
  /** The case UUID. */
  caseUuid: String,
})

const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)

const router = useRouter()

const variantQueryStore = useVariantQueryStore()
const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const variantAcmgRatingStore = useVariantAcmgRatingStore()
const caseDetailsStore = useCaseDetailsStore()
const variantResultSetStore = useVariantResultSetStore()

const showDetails = async (event) => {
  variantQueryStore.lastPosition = document.querySelector(
    'div#sodar-app-container',
  ).scrollTop
  router.push({
    name: 'seqvar-details',
    params: {
      row: event.smallvariantresultrow,
      selectedSection: event.selectedSection ?? null,
    },
  })
}

/** Whether the form is visible. */
const formVisible = ref(true)
/** Whether the query logs are visible. */
const queryLogsVisible = ref(false)

// Toggle visibility of the form.
const toggleForm = () => {
  formVisible.value = !formVisible.value
}

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => variantQueryStore.showFiltrationInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== undefined && newValue !== null && newValue !== oldValue) {
      updateUserSetting(
        appContext.csrf_token,
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
        appContext.csrf_token,
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
  variantResultSetStore.$reset()

  await caseDetailsStore.initialize(
    appContext.csrf_token,
    appContext.project?.sodar_uuid,
    props.caseUuid,
  )

  Promise.all([
    variantQueryStore.initialize(
      appContext.csrf_token,
      appContext?.project?.sodar_uuid,
      props.caseUuid,
      appContext,
    ),
    variantFlagsStore.initialize(
      appContext.csrf_token,
      appContext.project?.sodar_uuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantCommentsStore.initialize(
      appContext.csrf_token,
      appContext.project?.sodar_uuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantAcmgRatingStore.initialize(
      appContext.csrf_token,
      appContext.project?.sodar_uuid,
      caseDetailsStore.caseObj.sodar_uuid,
    ),
    variantResultSetStore.initialize(appContext.csrf_token),
  ]).then(async () => {
    await variantResultSetStore.loadResultSetViaQuery(
      variantQueryStore.queryUuid,
    )
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
    v-if="variantQueryStore.storeState.state === State.Active"
    class="d-flex flex-column h-100"
  >
    <!-- title etc. -->
    <Header :form-visible="formVisible" @toggle-form="toggleForm()" />

    <!-- query form -->
    <div v-if="formVisible" class="container-fluid sodar-page-container pt-0">
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
      <button
        class="ml-3 btn btn-sm btn-info"
        @click="queryLogsVisible = !queryLogsVisible"
      >
        {{ queryLogsVisible ? 'Hide' : 'Show' }} Logs
      </button>
      <pre v-show="queryLogsVisible">{{
        variantQueryStore.queryLogs?.join('\n')
      }}</pre>
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
  <div v-else class="alert alert-info">
    <i-fa-solid-circle-notch class="spin" />
    <strong class="pl-2">Loading site ...</strong>
  </div>
</template>

<style scoped></style>

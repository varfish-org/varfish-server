<script setup>
import FilterForm from './FilterForm.vue'
import FilterResultsTable from './FilterResultsTable.vue'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { QueryStates, QueryStateToText } from '@variants/enums'
import VariantDetailsModalWrapper from './VariantDetailsModalWrapper.vue'
import { watch, ref, onMounted, nextTick } from 'vue'
import { updateUserSetting } from '@varfish/user-settings.js'

const components = {
  VariantDetailsModalWrapper,
  FilterForm,
  FilterResultsTable,
}

const currentSmallVariant = ref(null)

const smallVariantDetailsModalWrapperRef = ref(null)

const variantDetailsStore = useVariantDetailsStore()

const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}'
)

const filterQueryStore = useFilterQueryStore()
filterQueryStore.caseUuid = appContext.case_uuid
filterQueryStore.umdPredictorApiToken = appContext.umd_predictor_api_token
filterQueryStore.hgmdProEnabled = appContext.hgmd_pro_enabled
filterQueryStore.hgmdProPrefix = appContext.hgmd_pro_prefix
filterQueryStore.ga4ghBeaconNetworkWidgetEnabled =
  appContext.ga4gh_beacon_network_widget_enabled
filterQueryStore.csrfToken = appContext.csrf_token
filterQueryStore.exomiserEnabled = appContext.exomiser_enabled
filterQueryStore.caddEnabled = appContext.cadd_enabled
filterQueryStore.fetchCase()
filterQueryStore.fetchDefaultSettings()
filterQueryStore.fetchPreviousQueryUuid()
filterQueryStore.fetchPresets()

const showModal = ({ gridRow, gridApi, smallVariant }) => {
  currentSmallVariant.value = smallVariant
  smallVariantDetailsModalWrapperRef.value.showModal()
  variantDetailsStore.fetchVariantDetails(
    { gridRow, gridApi, smallVariant },
    filterQueryStore.previousQueryDetails
  )
}

watch(
  () => filterQueryStore.queryState,
  (newValue, _oldValue) => {
    if (newValue === QueryStates.Finished.value) {
      filterQueryStore.unsetQueryStatusInterval
      filterQueryStore.fetchQueryResults()
      filterQueryStore.fetchHpoTerms()
      filterQueryStore.fetchQueryDetails()
    }
  }
)

watch(
  () => filterQueryStore.queryUuid,
  (newValue, _oldValue) => {
    if (newValue !== null) {
      filterQueryStore.setQueryStatusInterval
    }
  }
)

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

// Visibility of the form.
const formVisible = ref(true)

// Toggle visibility of the form.
const toggleForm = () => {
  formVisible.value = !formVisible.value
}

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
  <div v-if="filterQueryStore.case !== null" class="d-flex flex-column h-100">
    <!-- title etc. -->
    <div class="row sodar-pr-content-title pb-1">
      <!-- TODO buttons from sodar core -->
      <h2 class="sodar-pr-content-title">
        Filter Variants for Case
        <small class="text-muted">{{ filterQueryStore.case.name }}</small>
        <small class="badge badge-primary ml-2" style="font-size: 50%">
          {{ filterQueryStore.case.release }}
        </small>

        <a
          role="submit"
          class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
          id="sodar-pr-btn-copy-uuid"
          data-clipboard-text="{{ filterQueryStore.caseUuid }}"
          title="Copy UUID to clipboard"
          data-toggle="tooltip"
          data-placement="top"
        >
          <i-fa-solid-clipboard class="text-muted" />
        </a>
      </h2>

      <a
        href="#"
        class="btn btn-sm btn-secondary"
        @click.prevent="toggleForm()"
      >
        <i-mdi-button-cursor />
        <span v-if="formVisible">hide form</span>
        <span v-if="!formVisible">show form</span>
      </a>

      <div class="ml-auto btn-group">
        <a
          class="btn btn-secondary"
          :href="`/variants/${filterQueryStore.case.project}/case/${filterQueryStore.case.sodar_uuid}`"
        >
          <i-mdi-arrow-left-circle />
          Back to Case
        </a>
        <a
          class="btn btn-primary"
          :href="`/variants/${filterQueryStore.case.project}/case/filter/${filterQueryStore.case.sodar_uuid}`"
        >
          <i-mdi-filter />
          Legacy Filter
        </a>

        <a
          class="btn btn-primary"
          :href="`/svs/${filterQueryStore.case.project}/case/filter/${filterQueryStore.case.sodar_uuid}`"
        >
          <i class="iconify" data-icon="mdi:filter-variant"></i>
          Filter SVs
        </a>
      </div>
      <!-- TODO case filter buttons as component -->
    </div>

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
        :case="filterQueryStore.case"
        :query-results="filterQueryStore.queryResults"
        v-model:display-details="filterQueryStore.displayDetails"
        v-model:display-frequency="filterQueryStore.displayFrequency"
        v-model:display-constraint="filterQueryStore.displayConstraint"
        v-model:display-columns="filterQueryStore.displayColumns"
        @variant-selected="showModal"
      />
    </div>
    <div
      v-else-if="
        filterQueryStore.queryState === QueryStates.Running.value ||
        filterQueryStore.queryState === QueryStates.Fetching.value
      "
      class="alert alert-info"
    >
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2"
        >{{ QueryStateToText[filterQueryStore.queryState] }} ...</strong
      >
      <button
        class="ml-3 btn btn-sm btn-info"
        @click="
          filterQueryStore.queryLogsVisible = !filterQueryStore.queryLogsVisible
        "
      >
        {{ filterQueryStore.queryLogsVisible ? 'Hide' : 'Show' }} Logs
      </button>
      <pre v-show="filterQueryStore.queryLogsVisible">{{
        filterQueryStore.queryLogs.join('\n')
      }}</pre>
    </div>
    <div v-else class="alert alert-info">
      <strong>No query has been started yet.</strong>
      <div>
        Click
        <span class="badge badge-primary">
          <i-mdi-refresh />
          ilter &amp; Display
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

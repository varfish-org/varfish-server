<script setup>
import SmallVariantFilterForm from './SmallVariantFilterForm.vue'
import SmallVariantFilterResultsTable from './SmallVariantFilterResultsTable.vue'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { QueryStates, QueryStateToText } from '@variants/enums'
import SmallVariantDetailsModalWrapper from './SmallVariantDetailsModalWrapper.vue'
import { watch, ref } from 'vue'

const components = {
  SmallVariantDetailsModalWrapper,
  SmallVariantFilterForm,
  SmallVariantFilterResultsTable,
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
filterQueryStore.fetchCase()
filterQueryStore.fetchDefaultSettings()
filterQueryStore.fetchPreviousQueryUuid()

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
</script>

<template>
  <div v-if="filterQueryStore.case !== null">
    <div class="row sodar-pr-content-title pb-2">
      <!-- TODO buttons from sodar core -->
      <h2 class="sodar-pr-content-title">
        Filter Variants for Case
        <small class="text-muted">{{ filterQueryStore.case.name }}</small>
        <small class="badge badge-primary ml-2" style="font-size: 50%">
          {{ filterQueryStore.case.release }}
        </small>
      </h2>

      <a
        role="submit"
        class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
        id="sodar-pr-btn-copy-uuid"
        data-clipboard-text="{{ filterQueryStore.caseUuid }}"
        title="Copy UUID to clipboard"
        data-toggle="tooltip"
        data-placement="top"
      >
        <i
          class="iconify text-muted"
          data-icon="fa-solid:clipboard"
          aria-hidden="true"
        ></i>
      </a>

      <!-- TODO case filter buttons as component -->
    </div>

    <div class="container-fluid sodar-page-container pt-3">
      <div class="alert alert-secondary small p-2">
        <i class="iconify" data-icon="mdi:information"></i>
        This is the variant filtration form. You can use the form controls below
        to adjust your filter criteria.
        <strong
          >Click the
          <span class="badge badge-primary"
            ><i class="iconify" data-icon="mdi:refresh"></i> Filter &amp;
            Display</span
          >
          when you are ready!</strong
        >
        The results of your previous query will be loaded automatically if there
        are any.
      </div>

      <SmallVariantFilterForm />
    </div>
    <!-- table to fill when query finished -->
    <div v-if="filterQueryStore.queryState === QueryStates.Fetched.value">
      <SmallVariantFilterResultsTable
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
      <i class="iconify spin" data-icon="fa-solid:circle-notch"></i>
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
        <span class="badge badge-primary"
          ><i class="iconify" data-icon="mdi:refresh"></i> Filter &
          Display</span
        >
        to start filtering and create results to display here. You may want to
        adjust the filter settings to your needs first.
      </div>
    </div>
  </div>
  <div v-else class="alert alert-info">
    <i class="iconify spin" data-icon="fa-solid:circle-notch"></i>
    <strong class="pl-2">Loading site ...</strong>
  </div>

  <SmallVariantDetailsModalWrapper
    ref="smallVariantDetailsModalWrapperRef"
    :small-variant="currentSmallVariant"
    :fetched="variantDetailsStore.fetched"
  />
</template>

<style scoped></style>

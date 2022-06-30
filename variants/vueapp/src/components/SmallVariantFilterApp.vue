<template>
  <div v-if="store.case !== null">
    <div class="row sodar-pr-content-title pb-2">
      <!-- TODO buttons from sodar core -->
      <h2 class="sodar-pr-content-title">
        Filter Variants for Case
        <small class="text-muted">{{ store.case.name }}</small>
        <small class="badge badge-primary ml-2" style="font-size: 50%">
          {{ store.case.release }}
        </small>
      </h2>

      <a
        role="submit"
        class="btn btn-link mr-2 sodar-pr-btn-title sodar-pr-btn-copy-uuid sodar-copy-btn"
        id="sodar-pr-btn-copy-uuid"
        data-clipboard-text="{{ store.caseUuid }}"
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
    <div v-if="store.queryState === QueryStates.Fetched.value">
      <SmallVariantFilterResultsTable />
    </div>
    <div
      v-else-if="
        store.queryState === QueryStates.Running.value ||
        store.queryState === QueryStates.Fetching.value
      "
      class="alert alert-info"
    >
      <i class="iconify spin" data-icon="fa-solid:circle-notch"></i>
      <strong class="pl-2">{{ QueryStateToText[store.queryState] }} ...</strong>
      <button
        class="ml-3 btn btn-sm btn-info"
        @click="store.queryLogsVisible = !store.queryLogsVisible"
      >
        {{ store.queryLogsVisible ? "Hide" : "Show" }} Logs
      </button>
      <pre v-show="store.queryLogsVisible">{{
        store.queryLogs.join("\n")
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
</template>

<script>
import SmallVariantFilterForm from "./SmallVariantFilterForm.vue";
import SmallVariantFilterResultsTable from "./SmallVariantFilterResultsTable.vue";
import { filterQueryStore } from "@/stores/filterQuery";
import { QueryStates, QueryStateToText } from "@/enums";
import { storeToRefs } from "pinia";

export default {
  components: {
    SmallVariantFilterForm,
    SmallVariantFilterResultsTable,
  },
  setup() {
    const store = filterQueryStore();
    const appContext = JSON.parse(
      document
        .getElementById("sodar-ss-app-context")
        .getAttribute("app-context") || "{}"
    );
    store.caseUuid = appContext.case_uuid;
    store.umdPredictorApiToken = appContext.umd_predictor_api_token;
    store.hgmdProEnabled = appContext.hgmd_pro_enabled;
    store.hgmdProPrefix = appContext.hgmd_pro_prefix;
    store.ga4ghBeaconNetworkWidgetEnabled =
      appContext.ga4gh_beacon_network_widget_enabled;
    store.csrfToken = appContext.csrf_token;
    store.fetchCase();
    store.fetchDefaultSettings();
    store.fetchPreviousQueryUuid();
    const { queryState, queryUuid } = storeToRefs(store);
    return { store, queryState, queryUuid };
  },
  data() {
    return {
      QueryStates,
      QueryStateToText,
    };
  },
  watch: {
    queryState(newValue, oldValue) {
      if (newValue === QueryStates.Finished.value) {
        this.store.unsetQueryStatusInterval;
        this.store.fetchQueryResults();
        this.store.fetchHpoTerms();
        this.store.fetchQueryDetails();
      }
    },
    queryUuid(newValue, oldValue) {
      if (newValue !== null) {
        this.store.setQueryStatusInterval;
      }
    },
  },
};
</script>

<style scoped></style>

<script setup>
import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import { ref } from 'vue'

const props = defineProps({
  appContext: Object,
  submissionSet: Object,
})

/** Model for the ClinVar report URL input. */
const clinVarReportUrl = ref('')

/** Whether we are fetching or not. */
const isFetching = ref(false)

/** Handler that triggers fetching. */
const doFetch = () => {
  isFetching.value = true
  clinvarExportApi
    .fetchClinVarReport(
      props.appContext,
      props.submissionSet.sodar_uuid,
      clinVarReportUrl.value,
    )
    .then(() => {
      isFetching.value = false
    })
    .catch((error) => {
      console.error('Problem fetching ClinVar report', error)
      isFetching.value = false
    })
}
</script>

<template>
  <div class="form-group">
    <label for="input-fetch-clinvar-report">ClinVar Report URL</label>
    <div class="input-group">
      <input v-model="clinVarReportUrl" class="form-control" />
      <div class="input-group-append">
        <button class="btn btn-primary" @click.prevent="doFetch()">
          <i-mdi-cloud-download v-if="!isFetching" />
          <i-fa-solid-circle-notch v-if="isFetching" class="spin" />
          Fetch
        </button>
      </div>
    </div>
    <small class="form-text text-muted">
      Enter the URL to the ClinVar submission report to import. At the moment,
      you will have to reload the page after fetching to show the reports in the
      submissions.
    </small>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

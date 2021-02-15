<template>
  <div id="#app">
    <div v-if="appState === 'initializing'">
      <div class="text-center">
        <i class="fa fa-4x fa-spin fa-circle-o-notch text-muted mt-5"></i>
        <br />
        <br />
        <span class="text-muted font-italic">Loading...</span>
      </div>
    </div>
    <div v-if="appState !== 'initializing'">
      <submission-set-list
        v-if="appState === 'list'"
      ></submission-set-list>
      <submission-set-wizard
        v-if="['edit', 'add'].includes(appState)"
      ></submission-set-wizard>
    </div>
  </div>
</template>

<script>
import SubmissionSetList from './SubmissionSetList'
import SubmissionSetWizard from './SubmissionSetWizard'
import { mapState } from 'vuex'

export default {
  components: { SubmissionSetWizard, SubmissionSetList },
  computed: mapState({
    appState: state => state.clinvarExport.appState,
    notification: state => state.clinvarExport.notification
  }),
  beforeMount: function () {
    const rawAppContext = JSON.parse(
      document
        .getElementById('sodar-ss-app-context')
        .getAttribute('app-context') || '{}'
    )
    this.$store.dispatch('clinvarExport/initialize', {
      appContext: {
        baseUrl: rawAppContext.base_url,
        csrfToken: rawAppContext.csrf_token
      }
    })
  }
}
</script>

<style scoped>
</style>

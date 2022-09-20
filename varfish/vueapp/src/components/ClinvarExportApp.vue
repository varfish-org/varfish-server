<template>
  <div id="#app">
    <b-overlay :show="showOverlay">
      <submission-set-list
        v-if="['list', 'initializing'].includes(appState)"
      ></submission-set-list>
      <submission-set-wizard
        v-if="['edit', 'add'].includes(appState)"
      ></submission-set-wizard>
    </b-overlay>
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
    notification: state => state.clinvarExport.notification,
    showOverlay (state) {
      if (state.clinvarExport.appState === 'initializing' || state.clinvarExport.serverInteraction) {
        return true
      } else {
        return false
      }
    }
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

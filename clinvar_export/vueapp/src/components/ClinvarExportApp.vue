<template>
  <div id="#app">
    <div class="varfish-overlay-wrap position-relative">
      <submission-set-list
        v-if="['list', 'initializing'].includes(appState)"
      ></submission-set-list>
      <submission-set-wizard
        v-if="['edit', 'add'].includes(appState)"
      ></submission-set-wizard>

      <div
        v-if="showOverlay"
        class="varfish-overlay position-absolute"
        style="inset: 0; z-index: 10"
      >
        <div
          class="position-absolute bg-light"
          style="inset: 0; opacity: 0.85; backdrop-filter: blur(2px)"
        ></div>
        <div
          class="position-absolute"
          style="
            top: 50%;
            left: 50%;
            transform: translateX(-50%) translateY(-50%);
          "
        >
          <span aria-hidden="true" class="spinner-border"><!----></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

import { AppState } from '@/store/modules/clinvarExport'

import SubmissionSetList from './SubmissionSetList'
import SubmissionSetWizard from './SubmissionSetWizard'

export default {
  components: { SubmissionSetWizard, SubmissionSetList },
  computed: mapState({
    appState: (state) => state.clinvarExport.appState,
    notification: (state) => state.clinvarExport.notification,
    showOverlay(state) {
      if (
        state.clinvarExport.appState === AppState.initializing ||
        state.clinvarExport.serverInteraction
      ) {
        return true
      } else {
        return false
      }
    },
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
        csrfToken: rawAppContext.csrf_token,
      },
    })
  },
}
</script>

<style scoped></style>

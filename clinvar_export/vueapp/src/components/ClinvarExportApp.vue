<script setup>
import { computed } from 'vue'

import {
  AppState,
  useClinvarExportStore,
} from '@clinvarexport/stores/clinvar-export'

import SubmissionSetList from './SubmissionSetList.vue'
import SubmissionSetWizard from './SubmissionSetWizard.vue'

/* eslint-disable no-unused-vars */
const components = { SubmissionSetWizard, SubmissionSetList }

const store = useClinvarExportStore()

const rawAppContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)
store.initialize({
  baseUrl: rawAppContext.base_url,
  csrfToken: rawAppContext.csrf_token,
})

const showOverlay = computed(
  () => store.appState === AppState.initializing || store.serverInteraction,
)
</script>

<template>
  <div id="#app">
    <div class="varfish-overlay-wrap position-relative">
      <submission-set-list
        v-if="['list', 'initializing'].includes(store.appState)"
      ></submission-set-list>
      <submission-set-wizard
        v-if="['edit', 'add'].includes(store.appState)"
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

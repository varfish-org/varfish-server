<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watch } from 'vue'
import { useCasesStore } from '../stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details'

import CaseDetailHeader from './CaseDetailHeader.vue'
import CaseDetailContent from './CaseDetailContent.vue'
import Overlay from './Overlay.vue'
import { connectTopRowControls } from '../common'

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()

/** Whether to show the overlay. */
const overlayShow = computed(() => casesStore.serverInteraction > 0)

/** The currently used route. */
const route = useRoute()

/** The currently displayed case's UUID, updated from route. */
const caseUuidRef = ref(route.params.case)

connectTopRowControls()

// We can only finish initialization once the caseDetailsStore has completed loading as we need to initialize
// some stores needed for the details view(s).  We finish by watching the route to update the case.
casesStore.initializeRes.then(() => {
  Promise.all([
    caseDetailsStore.initialize(casesStore.cases[caseUuidRef.value]),
  ])
    .then(() => {
      watch(
        () => route.params,
        (newParams, oldParams) => {
          // reload variant annotation store if necessary
          if (newParams.case && newParams.case !== oldParams.case) {
            caseDetailsStore.initialize(casesStore.cases[caseUuidRef.value])
          }
        }
      )
    })
    .catch((err) => {
      console.error('Problem while initializing case details store', err)
    })
})
</script>

<template>
  <div class="d-flex flex-column h-100">
    <CaseDetailHeader :case-obj="caseDetailsStore.caseObj" />
    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <CaseDetailContent />
      <Overlay v-if="overlayShow" />
    </div>
  </div>
</template>

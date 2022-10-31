<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watch } from 'vue'
import queryPresetsApi from '@variants/api/queryPresets.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details'

import ModalSelect from '@varfish/components/ModalSelect.vue'
import Toast from '@varfish/components/Toast.vue'

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

/** Ref to the modal select input. */
const modalSelectRef = ref(null)
/** Ref to the toast. */
const toastRef = ref(null)

const handleEditQueryPresetsClicked = async () => {
  const csrfToken = casesStore.appContext.csrf_token
  const allPresets = await queryPresetsApi.listPresetSetAll(csrfToken)
  const options = allPresets.map((p) => ({
    value: p.sodar_uuid,
    label: p.label,
  }))

  try {
    const presetSetUuid = await modalSelectRef.value.show({
      title: `Select Query Presets`,
      label: `Query Presets`,
      helpText:
        'The selected presets will apply to future queries of this case by all users.',
      defaultValue: caseDetailsStore.caseObj.presetset ?? null,
      options,
    })

    await caseDetailsStore.updateCase({ presetset: presetSetUuid })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case was successfully updated.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a probelem updating the case.`,
    })
  }
}
</script>

<template>
  <div class="d-flex flex-column h-100">
    <CaseDetailHeader
      :case-obj="caseDetailsStore.caseObj"
      @edit-query-presets-click="handleEditQueryPresetsClicked()"
    />
    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <CaseDetailContent />
      <Overlay v-if="overlayShow" />
    </div>
    <ModalSelect ref="modalSelectRef" />
    <Toast ref="toastRef" :autohide="false" />
  </div>
</template>

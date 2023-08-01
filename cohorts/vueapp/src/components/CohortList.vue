<script setup>
import { computed, ref } from 'vue'

import Toast from '@varfish/components/Toast.vue'

import { connectTopRowControls } from '@cohorts/common'
import Header from '@cohorts/components/CohortList/Header.vue'
import Table from '@cohorts/components/CohortList/Table.vue'
import ModalCohortEditor from '@cohorts/components/ModalCohortEditor.vue'
import { useCohortsStore } from '@cohorts/stores/cohorts'
import Overlay from '@varfish/components/Overlay.vue'

const props = defineProps({})

/** Ref to the cohort editor modal. */
const modalCohortEditorRef = ref(null)

/** Ref to the toast. */
const toastRef = ref(null)

/** Initialize stores. */
const cohortsStore = useCohortsStore()

/** Whether to show the overlay. */
const overlayShow = computed(() => cohortsStore.serverInteractions > 0)

connectTopRowControls()

/** Handle clicks on "create cohort". */
const handleCreateCohortClicked = async () => {
  try {
    const cohort = await modalCohortEditorRef.value.show({
      title: 'Create Cohort',
      modelValue: {
        name: '',
        cases: [],
      },
      projectsCases: cohortsStore.projectsCases,
    })

    await cohortsStore.createCohort(cohort)
    await cohortsStore.loadFromServer()

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: 'The cohort was created successfully.',
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: 'There was a problem creating the cohort.',
    })
  }
}
</script>

<template>
  <div class="d-flex flex-column h-100">
    <Header @create-cohort-click="handleCreateCohortClicked" />

    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <Table />
    </div>
    <ModalCohortEditor ref="modalCohortEditorRef" />
    <Toast ref="toastRef" :autohide="false" />
    <Overlay v-if="overlayShow" />
  </div>
</template>

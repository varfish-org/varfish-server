/** Store for the project-wide quality control.
 */

import casesApi from '@cases/api/cases'
import { useCasesStore } from '@cases/stores/cases'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCasesQcStore = defineStore('casesQc', () => {
  const casesStore = useCasesStore()

  let qcValues = ref(null)
  const initialize = async () => {
    if (qcValues.value === null) {
      qcValues.value = await casesApi.loadProjectQcValues(
        casesStore.appContext.csrf_token,
        casesStore.project.sodar_uuid,
      )
    }
  }

  return { qcValues, initialize }
})

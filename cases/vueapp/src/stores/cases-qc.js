/** Store for the project-wide quality control.
 */

import casesApi from '@cases/api/cases.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { useCasesStore } from './cases.js'

export const useCasesQcStore = defineStore('casesQc', () => {
  const casesStore = useCasesStore()

  let qcValues = ref(null)
  const initialize = async () => {
    if (qcValues.value === null) {
      qcValues.value = await casesApi.loadProjectQcValues(
        casesStore.appContext.csrfToken,
        casesStore.project.sodar_uuid
      )
    }
  }

  return { qcValues, initialize }
})

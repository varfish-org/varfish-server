/** The main store of the cases app.
 *
 * Holds the major app state as well as the overall case list.
 */

import casesApi from '@cases/api/cases.js'
import { sodarObjectListToObject } from '@varfish/api-utils.js'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const AppState = Object.freeze({
  initializing: 'initializing',
  active: 'active',
})

/** Helper "enum" class with the case states. */
export const CaseStates = Object.freeze({
  initial: { label: 'initial', color: 'secondary' },
  active: { label: 'active', color: 'info' },
  'closed-unsolved': { label: 'closed as unsolved', color: 'success' },
  'closed-uncertain': { label: 'closed as uncertain', color: 'warning' },
  'closed-solved': { label: 'closed as solved', color: 'danger' },
})

export const useCasesStore = defineStore(
  {
    id: 'cases',
  },
  () => {
    /** The current application state. */
    const appState = ref(AppState.initializing)
    /** How many server interactions are running */
    const serverInteraction = ref(0)

    /** The application context to use. */
    const appContext = ref(null)
    /** The current project. */
    const project = ref(null)

    /** Whether to show inline help. */
    const showInlineHelp = ref(false)
    /** The complexity mode to use for presentation. */
    const complexityMode = ref('basic')

    /** The cases as sodar_uuid => case mapping. */
    const cases = ref({})
    /** List of the cases. */
    const caseRowData = computed(() => {
      // istanbul ignore if
      if (!cases.value) {
        return []
      } else {
        return Object.values(cases.value)
      }
    })

    /** The permissions that the user has. */
    const userPerms = ref(null)

    /** A promise storing the result of initialize. */
    const initializeRes = ref(null)

    const initialize = async (appContext$) => {
      appContext.value = appContext$
      project.value = appContext.value.project

      appState.value = AppState.initializing
      serverInteraction.value += 1

      initializeRes.value = Promise.all([
        casesApi
          .listCase(appContext.value.csrfToken, project.value.sodar_uuid)
          .then((res) => {
            cases.value = sodarObjectListToObject(res)
          }),
        casesApi
          .fetchPermissions(
            appContext.value.csrfToken,
            project.value.sodar_uuid
          )
          .then((res) => {
            userPerms.value = res
          }),
      ]).then(() => {
        appState.value = AppState.active
        serverInteraction.value -= 1
      })

      return initializeRes.value
    }

    return {
      appState,
      serverInteraction,
      appContext,
      project,
      showInlineHelp,
      complexityMode,
      cases,
      caseRowData,
      userPerms,
      initializeRes,
      initialize,
    }
  }
)

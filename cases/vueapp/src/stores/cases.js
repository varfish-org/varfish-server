/** The main store of the cases app.
 *
 * Holds the major app state as well as the overall case list.
 */

import casesApi from '@cases/api/cases'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

/** Helper "enum" class with the case states. */
export const CaseStates = Object.freeze({
  initial: { label: 'initial', color: 'secondary' },
  active: { label: 'active', color: 'info' },
  'closed-unsolved': { label: 'closed as unsolved', color: 'success' },
  'closed-uncertain': { label: 'closed as uncertain', color: 'warning' },
  'closed-solved': { label: 'closed as solved', color: 'danger' },
})

export const useCasesStore = defineStore('cases', () => {
  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The application context to use. */
  const appContext = ref(null)
  /** The current project. */
  const project = ref(null)

  /** Whether to show inline help. */
  const showInlineHelp = ref(false)
  /** The complexity mode to use for presentation. */
  const complexityMode = ref('simple')

  /** The number of cases in the project. */
  const caseCount = ref(null)

  /** The optional query string. */
  const caseQueryString = ref('')

  /** The permissions that the user has. */
  const userPerms = ref(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /** Initialize the store using the given application context. */
  const initialize = async (appContext$) => {
    if (storeState.value !== 'initial') {
      // only once
      return initializeRes.value
    }
    appContext.value = appContext$
    project.value = appContext.value.project

    storeState.value = StoreState.initializing
    serverInteractions.value += 1

    initializeRes.value = Promise.all([
      casesApi
        .listCase(appContext.value.csrfToken, project.value.sodar_uuid, {
          pageNo: 0,
          pageSize: 1,
          queryString: null,
        })
        .then((res) => {
          caseCount.value = res.count
          serverInteractions.value -= 1
          storeState.value = StoreState.active
        }),
      casesApi
        .fetchPermissions(appContext.value.csrfToken, project.value.sodar_uuid)
        .then((res) => {
          userPerms.value = res
        }),
    ]).catch((err) => {
      console.error('Problem initializing cases store', err)
      serverInteractions.value -= 1
      storeState.value = StoreState.error
    })

    return initializeRes.value
  }

  return {
    // state / data
    storeState,
    serverInteractions,
    appContext,
    project,
    showInlineHelp,
    complexityMode,
    caseCount,
    caseQueryString,
    userPerms,
    initializeRes,
    // functions
    initialize,
  }
})

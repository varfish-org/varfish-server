/** The main store of the cases app.
 *
 * Holds the major app state as well as the overall case list.
 */

import casesApi from '@cases/api/cases.js'
import { sodarObjectListToObject } from '@varfish/api-utils.js'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

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

  /** Ref to the resolve function promise returned by show(). */
  const resolveRef = ref(null)
  /** Ref to the reject function promise returned by show(). */
  const rejectRef = ref(null)
  /** Promise for initialization of the store. */
  const initializeRes = ref(
    new Promise(function (resolve, reject) {
      resolveRef.value = resolve
      rejectRef.value = reject
    })
  )

  const initialize = async (appContext$) => {
    if (storeState.value !== 'initial') {
      // only once
      return initializeRes.value
    }
    appContext.value = appContext$
    project.value = appContext.value.project

    storeState.value = StoreState.initializing
    serverInteraction.value += 1

    Promise.all([
      casesApi
        .listCase(appContext.value.csrfToken, project.value.sodar_uuid)
        .then((res) => {
          cases.value = sodarObjectListToObject(res)
        }),
      casesApi
        .fetchPermissions(appContext.value.csrfToken, project.value.sodar_uuid)
        .then((res) => {
          userPerms.value = res
        }),
    ])
      .then((res) => {
        storeState.value = StoreState.active
        serverInteraction.value -= 1
        if (resolveRef.value) {
          resolveRef.value(res)
        }
      })
      .catch((err) => {
        console.error('Problem initializing casesStore store', err)
        storeState.value = StoreState.error
        if (rejectRef.value) {
          rejectRef.value(err)
        }
      })

    return initializeRes.value
  }

  return {
    storeState,
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
})

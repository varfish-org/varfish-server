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
  const serverInteractions = ref(0)

  /** The application context to use. */
  const appContext = ref(null)
  /** The current project. */
  const project = ref(null)

  /** Whether to show inline help. */
  const showInlineHelp = ref(false)
  /** The complexity mode to use for presentation. */
  const complexityMode = ref('basic')

  /** The optional query string. */
  const caseQueryString = ref('')
  /** Total number of cases matching current criteria. */
  const caseCount = ref(0)
  /** The number of cases on a page. */
  const pageSize = ref(10)
  /** Current case page number. */
  const currentPageNo = ref(0)
  /** Total number of cases. */
  const pageCount = ref(0)
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

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /** Load the current page. */
  const loadCurrentPage = async () => {
    const listResult = await casesApi.listCase(
      appContext.value.csrfToken,
      project.value.sodar_uuid,
      {
        pageNo: currentPageNo.value,
        pageSize: pageSize.value,
        queryString: caseQueryString.value,
      }
    )
    caseCount.value = listResult.count
    pageCount.value = Math.ceil(listResult.count / pageSize.value)
    cases.value = sodarObjectListToObject(listResult.results)
  }

  /** Update the query parameters and wait for update.*/
  const updateQueryParams = async (newPageNo, newPageSize, newQueryString) => {
    let needsReload = false
    if (
      newPageNo !== undefined &&
      newPageNo !== null &&
      newPageNo !== currentPageNo.value
    ) {
      needsReload = true
      currentPageNo.value = newPageNo
    }
    if (
      newPageSize !== undefined &&
      newPageSize !== null &&
      newPageSize !== pageSize.value
    ) {
      needsReload = true
      currentPageNo.value = 0
      pageSize.value = newPageSize
    }
    if (
      newQueryString !== undefined &&
      newQueryString !== null &&
      newQueryString !== caseQueryString.value
    ) {
      needsReload = true
      currentPageNo.value = 0
      caseQueryString.value = newQueryString
    }

    if (needsReload) {
      serverInteractions.value += 1
      try {
        await loadCurrentPage()
      } finally {
        serverInteractions.value -= 1
      }
    }
  }

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
      loadCurrentPage(),
      casesApi
        .fetchPermissions(appContext.value.csrfToken, project.value.sodar_uuid)
        .then((res) => {
          userPerms.value = res
        }),
    ])
      .then(() => {
        serverInteractions.value -= 1
        storeState.value = StoreState.active
      })
      .catch((err) => {
        console.error('Problem initializing casesStore store', err)
        serverInteractions.value -= 1
        storeState.value = StoreState.error
      })

    return initializeRes.value
  }

  return {
    storeState,
    serverInteractions,
    appContext,
    project,
    showInlineHelp,
    complexityMode,
    caseQueryString,
    caseCount,
    pageSize,
    currentPageNo,
    pageCount,
    cases,
    caseRowData,
    userPerms,
    initializeRes,
    initialize,
    loadCurrentPage,
    updateQueryParams,
  }
})

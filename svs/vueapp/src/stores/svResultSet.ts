/**
 * Store with the result set and result set UUID of an SV query.
 */

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { SvClient } from '@svs/api/svClient'

export const useSvResultSetStore = defineStore('svResultSet', () => {
  // no store dependencies

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** Last result row as loaded from server. */
  const resultRow = ref<any | null>(null)
  /** UUID of the result set. */
  const resultSetUuid = ref<string | null>(null)
  /** Result set of query. */
  const resultSet = ref<any | null>(null)
  /** Query of result set, if any. */
  const query = ref<any | null>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    resultSetUuid.value = null
    resultSet.value = null
  }

  /**
   * Initialize the store with the given CSRF token.
   *
   * @param csrfToken$ CSRF token to use.
   * @param forceReload Whether to force reload.
   */
  const initialize = (csrfToken$: string, forceReload: boolean = false) => {
    // Initialize only once.
    if (!forceReload && storeState.state !== State.Initial) {
      return initializeRes.value
    }

    $reset()

    // Set simple properties.
    csrfToken.value = csrfToken$

    // Mark store as active.
    storeState.state = State.Active

    initializeRes.value = Promise.resolve()
    return initializeRes.value
  }

  /**
   * Fetch the result set via the given result row UUID.
   */
  const fetchResultSetViaRow = async (resultRowUuid: string) => {
    // Prevent loading twice.
    if (resultRowUuid === resultRow.value?.sodar_uuid) {
      return
    }

    const svClient = new SvClient(csrfToken.value)

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      const resultRow$ = await svClient.retrieveSvQueryResultRow(resultRowUuid)
      const resultSetUuid$ = resultRow$.svqueryresultset
      const resultSet$ = await svClient.retrieveSvQueryResultSet(resultSetUuid$)

      if (resultSet$.svquery) {
        // The result set belongs to a query so we retrieve it and get the case UUID
        // from there.
        const query$ = await svClient.retrieveSvQuery(resultSet$.svquery)
        query.value = query$
        caseUuid.value = query$.case
      } else {
        // Otherwise, it really should provide us with a Case UUID.
        if (!resultSet$.case) {
          console.error('expected case UUID in query but had none')
        }
        caseUuid.value = resultSet$.case
      }

      resultRow.value = resultRow$
      resultSet.value = resultSet$
      resultSetUuid.value = resultSetUuid$

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error(err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
    }
  }

  return {
    // data / state
    csrfToken,
    storeState,
    resultRow,
    resultSetUuid,
    resultSet,
    query,
    caseUuid,
    initializeRes,
    // functions
    initialize,
    fetchResultSetViaRow,
  }
})

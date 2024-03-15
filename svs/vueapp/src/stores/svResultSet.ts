/**
 * Store with the result set and result set UUID of an SV query.
 */

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { SvClient } from '@svs/api/strucvarClient'
import { VariantClient } from '@variants/api/variantClient'

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

  /** Table server option page number. */
  const tablePageNo = ref<number | null>(null)
  /** Table server option page size. */
  const tablePageSize = ref<number | null>(null)
  /** Table server option to sort column by. */
  const tableSortBy = ref<any | null>(null)
  /** Table server option sort asc or desc. */
  const tableSortType = ref<string | null>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    resultRow.value = null
    resultSetUuid.value = null
    resultSet.value = null
    query.value = null

    tablePageNo.value = null
    tablePageSize.value = null
    tableSortBy.value = null
    tableSortType.value = null
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

  const loadResultSetViaQuery = async (queryUuid$: string) => {
    // Once query is finished, load results, if still for the same query.
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')
    const responseResultSetList =
      await svClient.listSvQueryResultSet(queryUuid$)
    if (!responseResultSetList.length) {
      console.error('ERROR: no results in response')
    } else {
      // Still fetching the same query; push to query result set.
      resultSet.value = responseResultSetList[0]
      resultSetUuid.value = responseResultSetList[0].sodar_uuid
    }
  }

  const loadResultSetViaCase = async (caseUuid$: any) => {
    // Once query is finished, load results, if still for the same query.
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )
    const case$ = await variantClient.retrieveCase(caseUuid$)
    if (case$.svqueryresultset) {
      resultSet.value = case$.svqueryresultset
      resultSetUuid.value = case$.svqueryresultset.sodar_uuid
    } else {
      console.error('ERROR: no result set in case response')
    }
  }

  /**
   * Fetch the result set via the given result row UUID.
   */
  const fetchResultSetViaRow = async (resultRowUuid: string) => {
    // Prevent loading twice.
    if (resultRowUuid === resultRow.value?.sodar_uuid) {
      return
    }

    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

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
    tablePageNo,
    tablePageSize,
    tableSortBy,
    tableSortType,
    // functions
    initialize,
    fetchResultSetViaRow,
    loadResultSetViaQuery,
    loadResultSetViaCase,
  }
})

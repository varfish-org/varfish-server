/**
 * Store with the result set and result set UUID of an SV query.
 */
import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'

import { SvClient } from '@/svs/api/strucvarClient'
import { State, StoreState } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'
import { VariantClient } from '@/variants/api/variantClient'

/**
 * The view that the result set is loaded for: the query view, the case annotation
 * overview, or the details of a result row.
 */
export type ResultSetSource = 'query' | 'case' | 'row'

export const useSvResultSetStore = defineStore('svResultSet', () => {
  // store dependencies

  /** Context store. */
  const ctxStore = useCtxStore()

  // data passed to `initialize` and store state

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
  /**
   * The view the result set is loaded for.  A result set that arrives for another view is
   * discarded, so that loads that are still running for a view that the user has left do
   * not overwrite the result set.  The query view sets it, as the query store loads its
   * result set; the other loads set it themselves.  Not cleared by `$reset()`, as the query
   * view sets it before initializing the store.
   */
  const resultSetSource = ref<ResultSetSource | null>(null)

  /** Table server option page number. */
  const tablePageNo = ref<number | null>(null)
  /** Table server option page size. */
  const tablePageSize = ref<number | null>(null)
  /** Table server option to sort column by. */
  const tableSortBy = ref<any | null>(null)
  /** Table server option sort asc or desc. */
  const tableSortType = ref<string | null>(null)
  /** Uuid of last visisted row */
  const lastVisited = ref<string | null>(null)

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
    lastVisited.value = null
  }

  /**
   * Initialize the store.
   *
   * @param forceReload Whether to force reload.
   */
  const initialize = (forceReload: boolean = false) => {
    // Initialize only once.
    if (!forceReload && storeState.state !== State.Initial) {
      return initializeRes.value
    }

    $reset()

    // Mark store as active.
    storeState.state = State.Active

    initializeRes.value = Promise.resolve()
    return initializeRes.value
  }

  const loadResultSetViaQuery = async (queryUuid$: string) => {
    // Once query is finished, load results, if still for the same query.
    const svClient = new SvClient(ctxStore.csrfToken)
    const responseResultSetList =
      await svClient.listSvQueryResultSet(queryUuid$)
    if (resultSetSource.value !== 'query') {
      return // the query view has been left
    }
    if (!responseResultSetList.length) {
      console.error('ERROR: no results in response')
    } else {
      // Still fetching the same query; push to query result set.
      resultSet.value = responseResultSetList[0]
      resultSetUuid.value = responseResultSetList[0].sodar_uuid
    }
  }

  const loadResultSetViaCase = async (caseUuid$: any) => {
    resultSetSource.value = 'case'
    // Once query is finished, load results, if still for the same query.
    const variantClient = new VariantClient(ctxStore.csrfToken)
    const case$ = await variantClient.retrieveCase(caseUuid$)
    if (resultSetSource.value !== 'case') {
      return // the case annotation overview has been left
    }
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
    resultSetSource.value = 'row'
    // Prevent loading twice.
    if (resultRowUuid === resultRow.value?.sodar_uuid) {
      return
    }

    const svClient = new SvClient(ctxStore.csrfToken)

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      const resultRow$ = await svClient.retrieveSvQueryResultRow(resultRowUuid)
      const resultSetUuid$ = resultRow$.svqueryresultset
      const resultSet$ = await svClient.retrieveSvQueryResultSet(resultSetUuid$)

      // The result set belongs to a query so we retrieve it and get the case UUID from
      // there.  Otherwise, it really should provide us with a Case UUID.
      const query$ = resultSet$.svquery
        ? await svClient.retrieveSvQuery(resultSet$.svquery)
        : null

      // Only keep the result set if the result row's details have not been left.
      if (resultSetSource.value === 'row') {
        if (query$) {
          query.value = query$
          caseUuid.value = query$.case
        } else {
          if (!resultSet$.case) {
            console.error('expected case UUID in query but had none')
          }
          caseUuid.value = resultSet$.case
        }

        resultRow.value = resultRow$
        resultSet.value = resultSet$
        resultSetUuid.value = resultSetUuid$
      }

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
    storeState,
    resultRow,
    resultSetUuid,
    resultSet,
    query,
    resultSetSource,
    caseUuid,
    initializeRes,
    tablePageNo,
    tablePageSize,
    tableSortBy,
    tableSortType,
    lastVisited,
    // functions
    initialize,
    fetchResultSetViaRow,
    loadResultSetViaQuery,
    loadResultSetViaCase,
  }
})

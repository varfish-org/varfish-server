/**
 * Store with the result set and result set UUID of an variant query.
 */

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { VariantClient } from '@variants/api/variantClient'
import { DisplayColumns } from '@variants/enums'

export const useVariantResultSetStore = defineStore('variantResultSet', () => {
  // no store dependencies

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())
  /** Extra annotation fields available. */
  const extraAnnoFields = ref<any | null>(null)

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
  /** Which details to display, integer value from {@code DisplayDetails}. */
  const displayDetails = ref<number | null>(null)
  /** Which frequency information to display, integer value from {@code DisplayFrequency}. */
  const displayFrequency = ref<number | null>(null)
  /** The constraint to display, integer value from {@code DisplayConstraint}. */
  const displayConstraint = ref<number | null>(null)
  /** The additional columns to display; Integers from {@code DisplayColumns}. */
  const displayColumns = ref<any | null>(null)
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
    displayDetails.value = null
    displayFrequency.value = null
    displayConstraint.value = null
    displayColumns.value = null
    lastVisited.value = null
  }

  /**
   * Initialize the store with the given CSRF token.
   *
   * @param csrfToken$ CSRF token to use.
   * @param forceReload Whether to force reload.
   */
  const initialize = async (
    csrfToken$: string,
    forceReload: boolean = false,
  ) => {
    // Initialize only once.
    if (!forceReload && storeState.state !== State.Initial) {
      return initializeRes.value
    }

    $reset()

    // Load extra annotation fields, if necessary.
    if (!extraAnnoFields.value) {
      const variantClient = new VariantClient(csrfToken$)
      extraAnnoFields.value = await variantClient.fetchExtraAnnoFields()
    }

    // Set simple properties.
    csrfToken.value = csrfToken$

    // Mark store as active.
    storeState.state = State.Active

    initializeRes.value = Promise.resolve()
    return initializeRes.value
  }

  const refreshDisplayColumns = () => {
    const maybeAdd = [
      'SpliceAI-acc-gain',
      'SpliceAI-acc-loss',
      'SpliceAI-don-loss',
      'SpliceAI-don-gain',
      'CADD-PHRED',
    ]
    displayColumns.value = [DisplayColumns.Effect.value]
    extraAnnoFields.value
      .filter((value: any) => maybeAdd.includes(value.label))
      .forEach((value: any) => {
        displayColumns.value.push(`extra_anno${value.field}`)
      })
  }

  const loadResultSetViaQuery = async (queryUuid$: string) => {
    // Once query is finished, load results, if still for the same query.
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )
    const responseResultSetList =
      await variantClient.listQueryResultSet(queryUuid$)
    if (!responseResultSetList.length) {
      console.error('ERROR: no results in response')
    } else {
      // Still fetching the same query; push to query result set.
      resultSet.value = responseResultSetList[0]
      resultSetUuid.value = responseResultSetList[0].sodar_uuid
      refreshDisplayColumns()
    }
  }

  const loadResultSetViaCase = async (caseUuid$: any) => {
    // Once query is finished, load results, if still for the same query.
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )
    const case$ = await variantClient.retrieveCase(caseUuid$)
    if (case$.smallvariantqueryresultset) {
      resultSet.value = case$.smallvariantqueryresultset
      resultSetUuid.value = case$.smallvariantqueryresultset.sodar_uuid
      refreshDisplayColumns()
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

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      const resultRow$ =
        await variantClient.retrieveQueryResultRow(resultRowUuid)
      const resultSetUuid$ = resultRow$.smallvariantqueryresultset
      const resultSet$ =
        await variantClient.retrieveQueryResultSet(resultSetUuid$)

      if (resultSet$.smallvariantquery) {
        // The result set belongs to a query so we retrieve it and get the case UUID
        // from there.
        const query$ = await variantClient.retrieveQuery(
          resultSet$.smallvariantquery,
        )
        query.value = query$
        caseUuid.value = query$.case

        refreshDisplayColumns()
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
    extraAnnoFields,
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
    displayDetails,
    displayFrequency,
    displayConstraint,
    displayColumns,
    lastVisited,
    // functions
    initialize,
    fetchResultSetViaRow,
    loadResultSetViaQuery,
    loadResultSetViaCase,
    $reset,
  }
})

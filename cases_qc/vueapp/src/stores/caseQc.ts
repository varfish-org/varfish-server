import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { CaseQcClient } from '@cases_qc/api/caseQcClient'
import { StoreState, State } from '@varfish/storeUtils'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { type VarfishStats } from '@cases_qc/api/types'

export const useCaseQcStore = defineStore('caseQc', () => {
  // store dependencies

  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** UUID of the project.  */
  const projectUuid = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The current QC statistics. */
  const varfishStats = ref<VarfishStats>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any>>(Promise.resolve(null))

  // functions
  /** Fetch the QC stats details.
   *
   * @param svRecord The SV record to fetch details for.
   */
  const fetchQc = async (caseUuid$: string) => {
    // Prevent fetching twice.
    if (caseUuid$ === caseUuid.value) {
      return
    }

    // Clear old store contents
    varfishStats.value = null

    // Fetch new details
    const caseQcClient = new CaseQcClient(csrfToken.value)
    varfishStats.value = await caseQcClient.retrieveVarfishStats(caseUuid$)

    caseUuid.value = caseUuid$
  }

  /**
   * Initialize the store for the given case.
   *
   * This will fetch all information via the REST API, but only once for each state.
   *
   * This will also initialize the store dependencies.
   *
   * @param csrfToken$ CSRF token to use.
   * @param projectUuid$ UUID of the project.
   * @param caseUuid$ UUID of the case to use.
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    csrfToken$: string,
    projectUuid$: string,
    caseUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseDetailsStore.initialize(
      csrfToken$,
      projectUuid$,
      caseUuid$,
      forceReload,
    )

    // Initialize only once for each case.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$ &&
      caseUuid.value === caseUuid$
    ) {
      return initializeRes.value
    }

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    await fetchQc(caseUuid$)
    // case UUID set in fetchQc

    initializeRes.value = Promise.resolve()

    return initializeRes.value
  }

  return {
    // data / state
    csrfToken,
    projectUuid,
    caseUuid,
    storeState,
    varfishStats,
    initializeRes,
    // functions
    initialize,
    fetchQc,
  }
})

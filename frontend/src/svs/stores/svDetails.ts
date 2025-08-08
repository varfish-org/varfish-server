import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { AnnonarsApiClient } from '@/varfish/api/annonars'
import { State, StoreState } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'

/** `SvRecord` is a type alias for easier future interface definition. */
type SvRecord = any
/** `GeneInfo` is a type alias for easier future interface definition. */
type GeneInfo = any

export const useSvDetailsStore = defineStore('svDetails', () => {
  // store dependencies

  /** Context store. */
  const ctxStore = useCtxStore()
  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()

  // data passed to `initialize` and store state

  /** UUID of the project.  */
  const projectUuid = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The current UUID record. */
  const currentSvRecord = ref<SvRecord>(null)
  /** Infos on the variants of the record. */
  const genesInfos = ref<GeneInfo[] | null>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  // functions
  /** Fetch SV details.
   *
   * @param svRecord The SV record to fetch details for.
   */
  const fetchSvDetails = async (svRecord: SvRecord) => {
    // Prevent fetching twice.
    if (svRecord.sodar_uuid === currentSvRecord.value?.sodar_uuid) {
      return
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      // Clear old store contents
      currentSvRecord.value = null
      genesInfos.value = null

      // Fetch new details
      const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)
      const hgncIds = []
      for (const txEffect of svRecord.payload.tx_effects) {
        if (txEffect.gene.hgnc_id) {
          hgncIds.push(txEffect.gene.hgnc_id)
        }
      }
      if (hgncIds.length) {
        genesInfos.value = await annonarsClient.retrieveGeneInfos(hgncIds)
      }
      currentSvRecord.value = svRecord

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (error) {
      storeState.serverInteractions -= 1
      storeState.state = State.Error
    }
  }

  /**
   * Initialize the store for the given case.
   *
   * This will fetch all information via the REST API, but only once for each state.
   *
   * This will also initialize the store dependencies.
   *
   * @param projectUuid$ UUID of the project.
   * @param caseUuid$ UUID of the case to use.
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    projectUuid$: string,
    caseUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseDetailsStore.initialize(projectUuid$, caseUuid$, forceReload)

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
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$
    // Update store state
    storeState.state = State.Active

    initializeRes.value = Promise.resolve()

    return initializeRes.value
  }

  return {
    // data / state
    projectUuid,
    caseUuid,
    storeState,
    currentSvRecord,
    genesInfos,
    initializeRes,
    // functions
    initialize,
    fetchSvDetails,
  }
})

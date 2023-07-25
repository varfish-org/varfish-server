import annonarsApi from '@varfish/api/annonars'
import { defineStore } from 'pinia'
import { Ref, ref } from 'vue'

/** `SvRecord` is a type alias for easier future interface definition. */
type SvRecord = any
/** `GeneInfo` is a type alias for easier future interface definition. */
type GeneInfo = any
/** `AppContext` is a type alias for easier future interface definition. */
type AppContext = any

/** The possible store states. */
enum StoreState {
  Initial = 'initial',
  Initializing = 'initializing',
  Active = 'active',
  Error = 'error',
}

export const useSvDetailsStore = defineStore('detailsSv', () => {
  // Store state and message for UI
  /** State of the store. */
  const storeState: Ref<StoreState> = ref(StoreState.Initial)
  /** Message to display for store state, e.g., in overlay. */
  const storeStateMessage: Ref<string> = ref('')
  /** How many server interactions are running */
  const serverInteractions: Ref<number> = ref(0)

  // properties from application context
  /** CSRF Token to use (from app context). */
  const csrfToken: Ref<string> = ref(null)

  // state
  /** The current UUID record. */
  const currentSvRecord: Ref<SvRecord> = ref(null)
  /** Infos on the variants of the record. */
  const genesInfos: Ref<Array<GeneInfo>> = ref(null)

  /** Fetch SV details.
   *
   * @param svRecord The SV record to fetch details for.
   */
  const fetchSvDetails = async (svRecord: SvRecord) => {
    // Clear old store contents
    genesInfos.value = null

    // Fetch new details
    currentSvRecord.value = svRecord
    const hgncIds = svRecord.payload.tx_effects.map((item) => item.gene.hgnc_id)
    genesInfos.value = await annonarsApi.retrieveGeneInfos(hgncIds)
  }

  /** Initialize the store from the appContext. */
  const initialize = async (appContext: AppContext) => {
    if (storeState.value !== StoreState.Initial) {
      // only once
      return
    }
    // storeState.value = StoreState.initializing
    // storeStateMessage.value = 'Initializing...'

    storeState.value = StoreState.Active
    storeStateMessage.value = 'Store Active'

    // Initialize from appContext
    csrfToken.value = appContext.csrf_token
  }

  return {
    // data / state
    storeState,
    storeStateMessage,
    serverInteractions,
    csrfToken,
    currentSvRecord,
    genesInfos,
    // functions
    initialize,
    fetchSvDetails,
  }
})

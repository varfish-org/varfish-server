import geneinfoApi from '@variants/api/geneinfo.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

/** Constants with the used store states. */
export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

export const useSvDetailsStore = defineStore('detailsSv', () => {
  // Store state and message for UI
  /** State of the store. */
  const storeState = ref(StoreState.initial)
  /** Message to display for store state, e.g., in overlay. */
  const storeStateMessage = ref('')
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  // properties from application context
  /** CSRF Token to use (from app context). */
  const csrfToken = ref(null)

  // state
  /** The current UUID record. */
  const currentSvRecord = ref(null)
  /** The database used for query. */
  const database = ref(null)
  /** Infos on the variants of the record. */
  const genesInfos = ref(null)

  /** Fetch SV details. */
  const fetchSvDetails = async (svRecord, selectedDatabase) => {
    // Clear old store contents
    genesInfos.value = null

    // Fetch new details
    currentSvRecord.value = svRecord
    database.value = selectedDatabase
    const tmpGenesInfos = []
    const allGeneIds = svRecord.payload.ovl_genes
      .concat(svRecord.payload.tad_genes)
      .map((gene) => {
        return database.value == 'refseq' ? gene.entrez_id : gene.ensembl_id
      })
      .filter((geneId) => !!geneId)
    await Promise.all(
      allGeneIds.map(async (geneId) => {
        const geneInfos = await geneinfoApi.retrieveGeneInfos(
          csrfToken.value,
          database.value,
          geneId
        )
        tmpGenesInfos.push(geneInfos)
      })
    )
    tmpGenesInfos.sort((a, b) => {
      return ('' + a.symbol).localeCompare('' + b.symbol)
    })
    const tmpGenesInfos2 = []
    for (const entry of tmpGenesInfos) {
      if (!entry.symbol || entry.symbol == '') {
        continue // skip unless has symbol
      } else if (
        tmpGenesInfos2.length === 0 ||
        tmpGenesInfos2[tmpGenesInfos2.length - 1].symbol !== entry.symbol
      ) {
        tmpGenesInfos2.push(entry)
      }
    }
    genesInfos.value = tmpGenesInfos2
  }

  /** Initialize the store from the appContext. */
  const initialize = async (appContext) => {
    if (storeState.value !== 'initial') {
      // only once
      return
    }
    // storeState.value = StoreState.initializing
    // storeStateMessage.value = 'Initializing...'

    storeState.value = StoreState.active
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
    database,
    genesInfos,
    // functions
    initialize,
    fetchSvDetails,
  }
})

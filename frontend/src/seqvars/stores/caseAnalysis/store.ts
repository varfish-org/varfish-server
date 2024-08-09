import { acceptHMRUpdate, defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import {
  CaseAnalysis,
  CaseAnalysisSession,
  CasesAnalysisService,
} from '@varfish-org/varfish-api/lib'
import { client } from '@/cases/plugins/heyApi'

/**
 * Store for the case analysis (and case analysis session).
 */
export const useCaseAnalysisStore = defineStore('caseAnalysis', () => {
  /** The current store state. */
  const storeState = reactive<StoreState>(new StoreState())

  /** The UUID of the project for the presets. */
  const projectUuid = ref<string | undefined>(undefined)
  /** The UUID of the current case. */
  const caseUuid = ref<string | undefined>(undefined)

  /** The analyses for the case by UUID. */
  const caseAnalyses = reactive<Map<string, CaseAnalysis>>(new Map())
  /** The analysis sessions for the case by UUID. */
  const caseAnalysisSessions = reactive<Map<string, CaseAnalysisSession>>(
    new Map(),
  )
  /** The currently active analysis. */
  const currentAnalysis = ref<CaseAnalysis | undefined>(undefined)
  /** The currently active analysis session. */
  const currentSession = ref<CaseAnalysisSession | undefined>(undefined)

  /**
   * Initialize the store.
   *
   * @param projectUuid$ The UUID of the project to load the analyses/sessions for.
   * @param caseUuid$ The UUID of the case to load the analyses/sessions for.
   * @param forceReload$ Whether to force a reload of the data.
   */
  const initialize = async (
    projectUuid$: string,
    caseUuid$: string,
    forceReload$: boolean = false,
  ) => {
    // Do not reinitialize if the project is the same unless forced.
    if (
      projectUuid$ === projectUuid.value &&
      caseUuid$ === caseUuid.value &&
      !forceReload$
    ) {
      return
    }

    $reset()
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    storeState.state = State.Fetching
    try {
      storeState.serverInteractions += 1
      // NB: we currently load analyses and sessions sequentially because they
      // run in transactions but not without locks and either might fail.
      await loadCaseAnalyses()
      await loadCaseAnalysisSessions()
    } catch (e) {
      console.error('error', e)
      storeState.state = State.Error
      storeState.message = `Error loading case analysis / sessions: ${e}`
    } finally {
      storeState.serverInteractions -= 1
    }
    storeState.state = State.Active
  }

  /**
   * Load the case analyses for the current case.
   */
  const loadCaseAnalyses = async (): Promise<void> => {
    // Guard against missing initialization.
    if (caseUuid.value === undefined) {
      throw new Error('caseUuid is undefined')
    }

    // Paginate through all case analyses of the case.
    let cursor: string | undefined = undefined
    do {
      const response =
        await CasesAnalysisService.casesAnalysisApiCaseanalysisList({
          client,
          path: { case: caseUuid.value },
          query: { cursor, page_size: 100 },
        })
      if (response.data && response.data.results) {
        for (const caseAnalysis of response.data.results) {
          caseAnalyses.set(caseAnalysis.sodar_uuid, caseAnalysis)
        }

        if (response.data.next) {
          const tmpCursor = new URL(response.data.next).searchParams.get(
            'cursor',
          )
          if (tmpCursor !== null) {
            cursor = tmpCursor
          }
        }
      }
    } while (cursor !== undefined)
  }

  /**
   * Load the case analysis sessions for the current case.
   */
  const loadCaseAnalysisSessions = async (): Promise<void> => {
    // Guard against missing initialization.
    if (caseUuid.value === undefined) {
      throw new Error('caseUuid is undefined')
    }

    // Paginate through all case analyses of the case.
    let cursor: string | undefined = undefined
    do {
      const response =
        await CasesAnalysisService.casesAnalysisApiCaseanalysissessionList({
          client,
          path: { case: caseUuid.value },
          query: { cursor, page_size: 100 },
        })
      if (response.data && response.data.results) {
        for (const caseAnalysisSession of response.data.results) {
          caseAnalysisSessions.set(
            caseAnalysisSession.sodar_uuid,
            caseAnalysisSession,
          )
        }

        if (response.data.next) {
          const tmpCursor = new URL(response.data.next).searchParams.get(
            'cursor',
          )
          if (tmpCursor !== null) {
            cursor = tmpCursor
          }
        }
      }
    } while (cursor !== undefined)

    // Currently, there only ever is one analysis and session.
    currentAnalysis.value = caseAnalyses.values().next().value
    currentSession.value = caseAnalysisSessions.values().next().value
  }

  /**
   * Clear the store.
   *
   * This can be useful against artifacts in the UI.
   */
  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    projectUuid.value = undefined
    caseUuid.value = undefined
    caseAnalyses.clear()
    caseAnalysisSessions.clear()
  }

  return {
    // attributes
    storeState,
    projectUuid,
    caseUuid,
    caseAnalyses,
    caseAnalysisSessions,
    currentAnalysis,
    currentSession,
    // methods
    initialize,
    $reset,
  }
})

// Enable HMR (Hot Module Replacement)
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCaseAnalysisStore, import.meta.hot))
}

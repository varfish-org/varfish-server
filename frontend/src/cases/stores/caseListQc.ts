/** Store for the project-wide quality control.
 *
 * ### Store Dependencies
 *
 * Will use and initialize the following stores.
 *
 * - `caseListStore`
 */
import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'

import { CaseListClient } from '@/cases/api/caseListClient'
import { useCaseListStore } from '@/cases/stores/caseList'
import { State, StoreState } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'

/** Alias definition of CaseListQcValues type; to be defined later. */
type CaseListQcValues = any

export const useCasesQcStore = defineStore('caseListQc', () => {
  // store dependencies

  /** The context store. */
  const ctxStore = useCtxStore()
  /** The caseList store */
  const caseListStore = useCaseListStore()

  // data passed to `initialize` and store state

  /** The project UUID. */
  const projectUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** QC values retrieved from API. */
  const qcValues = ref<CaseListQcValues | null>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  // functions

  /**
   * Initialize the store and fetch the store's QC values.
   *
   * Will also initialize all its store dependencies.
   *
   * Will only reload for the same project if `forceReload`.
   *
   * @param projectUuid$ UUID of the project to load the case list for.
   */
  const initialize = async (
    projectUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseListStore.initialize(projectUuid$, forceReload)

    // Initialize only once for each project.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$
    ) {
      return initializeRes.value
    }

    // Set simple properties.
    projectUuid.value = projectUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const caseListClient = new CaseListClient(ctxStore.csrfToken)

    return caseListClient
      .loadProjectQcValues(caseListStore.project.sodar_uuid)
      .then((res) => {
        qcValues.value = res
        storeState.state = State.Active
        storeState.serverInteractions -= 1
      })
      .catch((err) => {
        console.error('Problem initializing caseListQc store', err)
        storeState.state = State.Error
        storeState.serverInteractions -= 1
      })
  }

  return {
    // data / state
    projectUuid,
    storeState,
    qcValues,
    initializeRes,
    // function
    initialize,
  }
})

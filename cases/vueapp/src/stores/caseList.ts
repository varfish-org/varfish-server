/** The main store of the cases app.
 *
 * Holds the major app state as well as the overall case list.
 */

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { CaseListClient } from '@cases/api/caseListClient'

/** Alias definition of Project type; to be defined later. */
type Project = any
/** Alias definition of UserPerms type; to be defined later. */
type UserPerms = any

/** Case state annotation info. */
export interface CaseStateInfo {
  label: string
  color: string
}

/** Mapping from case state to display info. */
export const CaseStates = new Map<string, CaseStateInfo>([
  ['initial', { label: 'initial', color: 'secondary' }],
  ['active', { label: 'active', color: 'info' }],
  ['closed-unsolved', { label: 'closed as unsolved', color: 'success' }],
  ['closed-uncertain', { label: 'closed as uncertain', color: 'warning' }],
  ['closed-solved', { label: 'closed as solved', color: 'danger' }],
])

export const useCaseListStore = defineStore('caseList', () => {
  // no store dependencies

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** The project UUID. */
  const projectUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The current project. */
  const project = ref<Project | null>(null)
  /** Whether to show inline help. */
  const showInlineHelp = ref<boolean>(false)
  /** The complexity mode to use for presentation. */
  const complexityMode = ref<string>('simple')
  /** The number of cases in the project. */
  const caseCount = ref<number | null>(null)
  /** The optional query string. */
  const caseQueryString = ref<string>('')
  /** The permissions that the user has. */
  const userPerms = ref<UserPerms>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any>>(null)

  // functions

  /**
   * Initialize the store.
   *
   * Will only reload for the same project if `forceReload`.
   *
   * @param csrfToken$ CSRF token to use.
   * @param projectUuid$ UUID of the project to load.
   * @param forceReload Whether to force reload.
   * @returns Promise for when the store is done initializing.
   */
  const initialize = (
    csrfToken$: string,
    projectUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize only once for each project.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$
    ) {
      return initializeRes.value
    }

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const caseListClient = new CaseListClient(csrfToken.value)

    initializeRes.value = caseListClient
      .fetchProject(projectUuid.value)
      .then((res) => {
        project.value = res
        return Promise.all([
          caseListClient
            .listCase(project.value.sodar_uuid, {
              pageNo: 0,
              pageSize: 1,
            })
            .then((res) => {
              caseCount.value = res.count
            }),
          caseListClient.fetchPermissions(projectUuid.value).then((res) => {
            userPerms.value = res
          }),
        ])
          .then(() => {
            storeState.state = State.Active
            storeState.serverInteractions -= 1
          })
          .catch((err) => {
            console.error('Problem initializing cases store', err)
            storeState.state = State.Error
            storeState.serverInteractions -= 1
          })
      })

    return initializeRes.value
  }

  return {
    // state / data
    csrfToken,
    projectUuid,
    storeState,
    project,
    showInlineHelp,
    complexityMode,
    caseCount,
    caseQueryString,
    userPerms,
    initializeRes,
    // functions
    initialize,
  }
})

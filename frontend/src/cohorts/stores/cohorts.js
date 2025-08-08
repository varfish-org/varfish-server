/** The main store of the cohorts app.
 *
 * Holds the major app state.
 */
import difference from 'lodash/difference'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import cohortsApi from '@/cohorts/api/cohorts'
import { uuidv4 } from '@/cohorts/helpers'
import { useCtxStore } from '@/varfish/stores/ctx'

export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

export const useCohortsStore = defineStore('cohorts', () => {
  /** The context store. */
  const ctxStore = useCtxStore()

  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The current project. */
  const project = ref(null)
  /** List of projects and contained cases the user has access to. */
  const projectsCases = ref([])

  /** Whether to show inline help. */
  const showInlineHelp = ref(false)
  /** The complexity mode to use for presentation. */
  const complexityMode = ref('simple')

  /** The permissions that the user has. */
  const userPerms = ref(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /** vue-easy-table state. */
  const tableLoading = ref(false)

  /** vue-easy-table server options. */
  const tableServerOptions = ref({
    page: 1,
    rowsPerPage: 10,
    sortBy: null,
    sortType: 'asc',
  })

  /** vue-easy-table search term. */
  const searchTerm = ref('')

  /** vue-easy-table data. */
  const tableRows = ref([])

  /** Total count of cohorts across pagination. */
  const cohortCount = ref(0)

  /** Initialize the store using the given CSRF token and project UUID. */
  const initialize = async (projectUuid$) => {
    if (storeState.value !== 'initial') {
      // only once
      return initializeRes.value
    }
    project.value = projectUuid$

    storeState.value = StoreState.initializing
    serverInteractions.value += 1

    initializeRes.value = Promise.all([
      cohortsApi
        .fetchPermissions(ctxStore.csrfToken, project.value.sodar_uuid)
        .then((res) => {
          userPerms.value = res
        }),
      cohortsApi
        .listAccessibleProjectsCases(project.value.sodar_uuid)
        .then((res) => {
          projectsCases.value = res
        }),
    ])
      .then(() => {
        serverInteractions.value -= 1
        storeState.value = StoreState.active
      })
      .catch((err) => {
        console.error('Problem initializing cohorts store', err)
        storeState.value = StoreState.error
      })

    return initializeRes.value
  }

  /** Create a cohort. */
  const createCohort = async (payload) => {
    const cases = payload.cases
    let cohort = null
    delete payload.cases
    serverInteractions.value += 1
    try {
      cohort = await cohortsApi.createCohort(
        ctxStore.csrfToken,
        project.value.sodar_uuid,
        payload,
      )
    } finally {
      serverInteractions.value -= 1
    }
    if (cohort) {
      for (const caseUuid of cases) {
        const cohortCase = {
          sodar_uuid: uuidv4(),
          cohort: cohort.sodar_uuid,
          case: caseUuid,
        }
        serverInteractions.value += 1
        try {
          await cohortsApi.createCohortCase(
            ctxStore.csrfToken,
            project.value.sodar_uuid,
            cohortCase,
          )
        } finally {
          serverInteractions.value -= 1
        }
      }
    }
  }

  /** Update a cohort. */
  const updateCohort = async (cohortUuid, payload) => {
    const cases = payload.cases
    let cohort = null
    const currentCasesUuids = {}
    delete payload.cases
    serverInteractions.value += 1
    try {
      cohort = await cohortsApi.updateCohort(
        ctxStore.csrfToken,
        cohortUuid,
        payload,
      )
    } finally {
      serverInteractions.value -= 1
    }
    serverInteractions.value += 1
    try {
      const cohortCases = await cohortsApi.listCohortCase(
        ctxStore.csrfToken,
        cohortUuid,
      )
      for (const cohortCase of cohortCases) {
        currentCasesUuids[cohortCase.case] = cohortCase.sodar_uuid
      }
    } finally {
      serverInteractions.value -= 1
    }
    if (cohort && currentCasesUuids) {
      for (const caseToRemove of difference(
        Object.keys(currentCasesUuids),
        cases,
      )) {
        serverInteractions.value += 1
        try {
          await cohortsApi.destroyCohortCase(
            ctxStore.csrfToken,
            currentCasesUuids[caseToRemove],
          )
        } finally {
          serverInteractions.value -= 1
        }
      }
      for (const caseToAdd of difference(
        cases,
        Object.keys(currentCasesUuids),
      )) {
        const cohortCase = {
          sodar_uuid: uuidv4(),
          cohort: cohort.sodar_uuid,
          case: caseToAdd,
        }
        serverInteractions.value += 1
        try {
          await cohortsApi.createCohortCase(
            ctxStore.csrfToken,
            project.value.sodar_uuid,
            cohortCase,
          )
        } finally {
          serverInteractions.value -= 1
        }
      }
    }
  }

  /** Destroy a cohort. */
  const destroyCohort = async (cohortUuid) => {
    serverInteractions.value += 1
    try {
      await cohortsApi.destroyCohort(ctxStore.csrfToken, cohortUuid)
    } finally {
      serverInteractions.value -= 1
    }
  }

  /** Load cohorts for given project. */
  const loadFromServer = async () => {
    tableLoading.value = true
    serverInteractions.value += 1
    try {
      const response = await cohortsApi.listCohort(
        ctxStore.csrfToken,
        project.value.sodar_uuid,
        {
          pageNo: tableServerOptions.value.page,
          pageSize: tableServerOptions.value.rowsPerPage,
          orderBy: tableServerOptions.value.sortBy,
          orderDir: tableServerOptions.value.sortType,
          queryString: searchTerm.value,
        },
      )
      cohortCount.value = response.count
      tableRows.value = response.results
      tableLoading.value = false
    } finally {
      serverInteractions.value -= 1
    }
  }

  return {
    storeState,
    serverInteractions,
    project,
    projectsCases,
    showInlineHelp,
    complexityMode,
    userPerms,
    tableLoading,
    tableServerOptions,
    searchTerm,
    cohortCount,
    tableRows,
    initializeRes,
    initialize,
    createCohort,
    updateCohort,
    destroyCohort,
    loadFromServer,
  }
})

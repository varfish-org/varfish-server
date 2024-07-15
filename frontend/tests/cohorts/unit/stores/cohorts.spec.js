import { uuidv4 } from '@/cohorts/helpers'
import cohortsApi from '@/cohorts/api/cohorts'
import { useCohortsStore } from '@/cohorts/stores/cohorts'
import { State, StoreState } from '@/varfish/storeUtils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import accessibleProjectsCasesResponse from '../../data/accessibleProjectsCasesResponse.json'
import createCohortCaseResponses from '../../data/createCohortCaseResponses.json'
import createCohortResponse from '../../data/createCohortResponse.json'
import listCohortCaseResponse from '../../data/listCohortCaseResponse.json'
import listCohortResponse from '../../data/listCohortResponse.json'
import updateCohortResponse from '../../data/updateCohortResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@/cohorts/api/cohorts.js')
vi.mock('@/cohorts/helpers.js')

describe('useCohortsStore', () => {
  const csrfToken = 'fake-token'
  const project = accessibleProjectsCasesResponse[0]
  const cohortUuid = 'cohort-fake-uuid'

  let cohortsStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createPinia())
    cohortsStore = useCohortsStore()
    uuidv4.mockReturnValue('cohortcase-fake-uuid')
    uuidv4.mockReturnValueOnce('cohortcase3-fake-uuid')
    uuidv4.mockReturnValueOnce('cohortcase4-fake-uuid')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('initial state', async () => {
    expect(cohortsStore.storeState).toBe(State.Initial)
    expect(cohortsStore.serverInteractions).toBe(0)
    expect(cohortsStore.project).toBe(null)
    expect(cohortsStore.csrfToken).toBe(null)
    expect(cohortsStore.projectsCases).toStrictEqual([])
    expect(cohortsStore.showInlineHelp).toBe(false)
    expect(cohortsStore.complexityMode).toBe('simple')
    expect(cohortsStore.userPerms).toBe(null)
    expect(cohortsStore.initializeRes).toBe(null)
    expect(cohortsStore.tableLoading).toBe(false)
    expect(cohortsStore.tableServerOptions).toStrictEqual({
      page: 1,
      rowsPerPage: 10,
      sortBy: null,
      sortType: 'asc',
    })
    expect(cohortsStore.searchTerm).toBe('')
    expect(cohortsStore.tableRows).toStrictEqual([])
    expect(cohortsStore.cohortCount).toBe(0)
  })

  test('createCohort()', async () => {
    cohortsApi.createCohort.mockResolvedValue(createCohortResponse)
    cohortsApi.createCohortCase.mockResolvedValueOnce(
      createCohortCaseResponses[0],
    )
    cohortsApi.createCohortCase.mockResolvedValueOnce(
      createCohortCaseResponses[1],
    )
    cohortsStore.storeState = StoreState.active
    cohortsStore.csrfToken = csrfToken
    cohortsStore.project = project

    const payload = {
      cases: [
        createCohortCaseResponses[0].case,
        createCohortCaseResponses[1].case,
      ],
    }

    await cohortsStore.createCohort(payload)

    expect(cohortsApi.createCohort).toHaveBeenCalledOnce()
    expect(cohortsApi.createCohort).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      payload,
    )

    expect(cohortsApi.createCohortCase).toHaveBeenCalledTimes(2)
    expect(cohortsApi.createCohortCase).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      {
        cohort: createCohortResponse.sodar_uuid,
        case: createCohortCaseResponses[0].case,
        sodar_uuid: 'cohortcase3-fake-uuid',
      },
    )
    expect(cohortsApi.createCohortCase).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      {
        cohort: createCohortResponse.sodar_uuid,
        case: createCohortCaseResponses[1].case,
        sodar_uuid: 'cohortcase4-fake-uuid',
      },
    )
  })

  test('updateCohort()', async () => {
    cohortsApi.updateCohort.mockResolvedValue(updateCohortResponse)
    cohortsApi.listCohortCase.mockResolvedValue(listCohortCaseResponse)
    cohortsApi.createCohortCase.mockResolvedValue(createCohortCaseResponses)

    cohortsStore.storeState = State.Active
    cohortsStore.csrfToken = csrfToken
    cohortsStore.project = project

    const updateCases = [
      'case1-fake-uuid',
      'case3-fake-uuid',
      'case5-fake-uuid',
    ]

    const payload = {
      cases: updateCases,
    }

    await cohortsStore.updateCohort(cohortUuid, payload)

    expect(cohortsApi.listCohortCase).toHaveBeenCalledOnce()
    expect(cohortsApi.listCohortCase).toHaveBeenCalledWith(
      csrfToken,
      cohortUuid,
    )

    expect(cohortsApi.destroyCohortCase).toHaveBeenCalledOnce()
    expect(cohortsApi.destroyCohortCase).toHaveBeenCalledWith(
      csrfToken,
      'cohortcase2-fake-uuid',
    )

    expect(cohortsApi.createCohortCase).toHaveBeenCalledTimes(2)
    expect(cohortsApi.createCohortCase).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      {
        cohort: cohortUuid,
        case: 'case3-fake-uuid',
        sodar_uuid: 'cohortcase3-fake-uuid',
      },
    )
    expect(cohortsApi.createCohortCase).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      {
        cohort: cohortUuid,
        case: 'case5-fake-uuid',
        sodar_uuid: 'cohortcase4-fake-uuid',
      },
    )
  })

  test('destroyCohort()', async () => {
    cohortsApi.destroyCohort.mockResolvedValue(createCohortResponse)
    cohortsStore.storeState = State.Active
    cohortsStore.csrfToken = csrfToken
    cohortsStore.project = project

    await cohortsStore.destroyCohort(cohortUuid)

    expect(cohortsApi.destroyCohort).toHaveBeenCalledOnce()
    expect(cohortsApi.destroyCohort).toHaveBeenCalledWith(csrfToken, cohortUuid)
  })

  test('loadFromServer()', async () => {
    cohortsApi.listCohort.mockResolvedValue(listCohortResponse)

    cohortsStore.storeState = State.Active
    cohortsStore.csrfToken = csrfToken
    cohortsStore.project = project

    const tableServerOptions = {
      pageNo: cohortsStore.tableServerOptions.page,
      pageSize: cohortsStore.tableServerOptions.rowsPerPage,
      orderBy: cohortsStore.tableServerOptions.sortBy,
      orderDir: cohortsStore.tableServerOptions.sortType,
      queryString: '',
    }

    await cohortsStore.loadFromServer()

    expect(cohortsApi.listCohort).toHaveBeenCalledOnce()
    expect(cohortsApi.listCohort).toHaveBeenCalledWith(
      csrfToken,
      project.sodar_uuid,
      tableServerOptions,
    )
    expect(cohortsStore.cohortCount).toStrictEqual(listCohortResponse.count)
    expect(cohortsStore.tableRows).toStrictEqual(listCohortResponse.results)
    expect(cohortsStore.tableLoading).toBe(false)
  })
})

import cohortsApi from '@cohorts/api/cohorts.js'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import accessibleProjectsCasesResponse from '../../data/accessibleProjectsCasesResponse.json'
import createCohortCaseResponses from '../../data/createCohortCaseResponses.json'
import createCohortResponse from '../../data/createCohortResponse.json'
import listCohortCaseResponse from '../../data/listCohortCaseResponse.json'
import listCohortResponse from '../../data/listCohortResponse.json'
import permissionsResponse from '../../data/permissionsResponse.json'
import updateCohortResponse from '../../data/updateCohortResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-project-uuid'
  const entityUuid = 'fake-entity-uuid'

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('listCohort', async () => {
    fetch.mockResponseOnce(JSON.stringify(listCohortResponse))

    const res = await cohortsApi.listCohort(csrfToken, projectUuid, {})

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohort/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listCohortResponse)
  })

  test('listCohort with parameters', async () => {
    fetch.mockResponseOnce(JSON.stringify(listCohortResponse))

    const pageNo = 2
    const pageSize = 10
    const orderBy = 'date_created'
    const orderDir = 'ascending'
    const queryString = 'Cohort'
    const res = await cohortsApi.listCohort(csrfToken, projectUuid, {
      pageNo: pageNo,
      pageSize: pageSize,
      orderBy: orderBy,
      orderDir: orderDir,
      queryString: queryString,
    })

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohort/list-create/${projectUuid}/?page=${pageNo}&page_size=${pageSize}&order_by=${orderBy}&order_dir=${orderDir}&q=${queryString}`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listCohortResponse)
  })

  // TODO List with search/pagination parameters

  test('createCohort', async () => {
    fetch.mockResponseOnce(JSON.stringify(createCohortResponse))

    const payload = { name: 'New Cohort' }
    const res = await cohortsApi.createCohort(csrfToken, projectUuid, payload)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohort/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(createCohortResponse)
  })

  test('listAccessibleProjectsCases', async () => {
    fetch.mockResponseOnce(JSON.stringify(accessibleProjectsCasesResponse))

    const res = await cohortsApi.listAccessibleProjectsCases(projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/accessible-projects-cases/list/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': null,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(accessibleProjectsCasesResponse)
  })

  test('updateCohort', async () => {
    fetch.mockResponseOnce(JSON.stringify(updateCohortResponse))

    const payload = { name: 'Cohort 2 Updated' }
    const res = await cohortsApi.updateCohort(csrfToken, entityUuid, payload)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohort/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PUT',
      },
    ])
    expect(res).toEqual(updateCohortResponse)
  })

  test('destroyCohort', async () => {
    fetch.mockResponseOnce({})

    const res = await cohortsApi.destroyCohort(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohort/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBeUndefined()
  })

  test('createCohortCase', async () => {
    fetch.mockResponseOnce(JSON.stringify(createCohortCaseResponses[0]))
    const payload = {
      sodar_uuid: 'fake-entity-uuid',
      cohort: 'fake-cohort-uuid',
      case: 'fake-case-uuid',
    }
    const res = await cohortsApi.createCohortCase(
      csrfToken,
      projectUuid,
      payload
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohortcase/create/${projectUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(createCohortCaseResponses[0])
  })

  test('listCohortCase', async () => {
    fetch.mockResponseOnce(JSON.stringify(listCohortCaseResponse))

    const res = await cohortsApi.listCohortCase(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohortcase/list/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listCohortCaseResponse)
  })

  test('destroyCohortCase', async () => {
    fetch.mockResponseOnce({})

    const res = await cohortsApi.destroyCohortCase(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/cohortcase/destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBeUndefined()
  })

  test('fetchPermissions', async () => {
    fetch.mockResponseOnce(JSON.stringify(permissionsResponse))

    const res = await cohortsApi.fetchPermissions(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cohorts/ajax/user-permissions/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(permissionsResponse)
  })
})

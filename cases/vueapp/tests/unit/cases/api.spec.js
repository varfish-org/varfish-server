import casesApi from '@cases/api/cases.js'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import caseListResponse from '../../data/caseListResponse.json'
import loadProjectQcValuesResponse from '../../data/loadProjectQcValuesResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-uuid'

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('apiFetch', async () => {
    fetch.mockResponseOnce(JSON.stringify(caseListResponse))

    const res = await casesApi.listCase(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      '/cases/ajax/case/list/fake-uuid/',
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/vnd.bihealth.varfish+json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(caseListResponse)
  })

  test('loadProjectQcValues', async () => {
    fetch.mockResponseOnce(JSON.stringify(loadProjectQcValuesResponse))

    const res = await casesApi.loadProjectQcValues(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      '/variants/fake-uuid/api-qc/',
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/vnd.bihealth.varfish+json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(loadProjectQcValuesResponse)
  })
})

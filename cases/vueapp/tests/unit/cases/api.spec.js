import casesApi from '@cases/api/cases.js'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import caseListResponse from '../../data/caseListResponse.json'
import fetchCaseAlignmentStatsResponse from '../../data/fetchCaseAlignmentStatsResponse.json'
import fetchCaseRelatednessResponse from '../../data/fetchCaseRelatednessResponse.json'
import fetchCaseVariantStatsResponse from '../../data/fetchCaseVariantStatsResponse.json'
import loadProjectQcValuesResponse from '../../data/loadProjectQcValuesResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-project-uuid'
  const caseUuid = 'fake-case-uuid'

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('listCase with parameters', async () => {
    fetch.mockResponseOnce(JSON.stringify(caseListResponse))

    const res = await casesApi.listCase(csrfToken, projectUuid, {
      pageNo: 0,
      pageSize: 10,
      queryString: 'thequery',
    })

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      '/cases/ajax/case/list/fake-project-uuid/?page=1&page_size=10&q=thequery',
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(caseListResponse)
  })

  test('listCase with empty', async () => {
    fetch.mockResponseOnce(JSON.stringify(caseListResponse))

    const res = await casesApi.listCase(csrfToken, projectUuid, {})

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      '/cases/ajax/case/list/fake-project-uuid/',
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
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
      '/variants/ajax/project/qc/fake-project-uuid/',
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(loadProjectQcValuesResponse)
  })

  test('fetchCaseAlignmentStats', async () => {
    fetch.mockResponseOnce(JSON.stringify(fetchCaseAlignmentStatsResponse))

    const res = await casesApi.fetchCaseAlignmentStats(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/case-alignment-stats/list/${caseUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(fetchCaseAlignmentStatsResponse)
  })

  test('fetchCaseVariantStats', async () => {
    fetch.mockResponseOnce(JSON.stringify(fetchCaseVariantStatsResponse))

    const res = await casesApi.fetchCaseVariantStats(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/case-variant-stats/list/${caseUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(fetchCaseVariantStatsResponse)
  })

  test('fetchCaseRelatedness', async () => {
    fetch.mockResponseOnce(JSON.stringify(fetchCaseRelatednessResponse))

    const res = await casesApi.fetchCaseRelatedness(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/case-relatedness/list/${caseUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(fetchCaseRelatednessResponse)
  })

  test('fetchPermissions', async () => {
    fetch.mockResponseOnce(JSON.stringify(['views.view_data']))

    const res = await casesApi.fetchPermissions(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/user-permissions/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(['views.view_data'])
  })
})

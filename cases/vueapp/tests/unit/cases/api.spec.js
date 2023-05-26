import casesApi from '@cases/api/cases.js'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import caseListResponse from '../../data/caseListResponse.json'
import createCaseCommentResponse from '../../data/createCaseCommentResponse.json'
import fetchAnnotationReleaseInfosResponse from '../../data/fetchAnnotationReleaseInfosResponse.json'
import fetchCaseAlignmentStatsResponse from '../../data/fetchCaseAlignmentStatsResponse.json'
import fetchCaseGeneAnnotationResponse from '../../data/fetchCaseGeneAnnotationResponse.json'
import fetchCaseRelatednessResponse from '../../data/fetchCaseRelatednessResponse.json'
import fetchCaseVariantStatsResponse from '../../data/fetchCaseVariantStatsResponse.json'
import fetchSvAnnotationReleaseInfosResponse from '../../data/fetchSvAnnotationReleaseInfosResponse.json'
import listCaseCommentResponse from '../../data/listCaseCommentResponse.json'
import listCasePhenotypeTermsResponse from '../../data/listCasePhenotypeTermsResponse.json'
import loadProjectQcValuesResponse from '../../data/loadProjectQcValuesResponse.json'
import retrieveCaseResponse from '../../data/retrieveCaseResponse.json'
import updateCaseCommentResponse from '../../data/updateCaseCommentResponse.json'
import updateCasePayload from '../../data/updateCasePayload.json'
import updateCasePhenotypeTermsResponse from '../../data/updateCasePhenotypeTermsResponse.json'
import updateCaseResponse from '../../data/updateCaseResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-project-uuid'
  const caseUuid = 'fake-case-uuid'
  const caseCommentUuid = 'fake-case-comment-uuid'
  const casePhenotypeTermsUuid = 'fake-case-phenotype-terms-uuid'

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

  test('retrieveCase', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveCaseResponse))

    const res = await casesApi.retrieveCase(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case/retrieve-update/${caseUuid}/`,
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
    expect(res).toEqual(retrieveCaseResponse)
  })

  test('updateCase', async () => {
    fetch.mockResponseOnce(JSON.stringify(updateCaseResponse))

    const res = await casesApi.updateCase(
      csrfToken,
      caseUuid,
      updateCasePayload
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case/retrieve-update/${caseUuid}/`,
      {
        body: JSON.stringify(updateCasePayload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(updateCaseResponse)
  })

  test('fetchVarAnnos', async () => {
    const res = await casesApi.fetchVarAnnos(csrfToken, projectUuid)

    expect(res).toEqual([])
  })

  test('fetchVarComments', async () => {
    const res = await casesApi.fetchVarComments(csrfToken, projectUuid)

    expect(res).toEqual([])
  })

  test('fetchVarAcmgRatings', async () => {
    const res = await casesApi.fetchVarAcmgRatings(csrfToken, projectUuid)

    expect(res).toEqual([])
  })

  test('fetchSvAnnos', async () => {
    const res = await casesApi.fetchSvAnnos(csrfToken, projectUuid)

    expect(res).toEqual([])
  })

  test('fetchSvComments', async () => {
    const res = await casesApi.fetchSvComments(csrfToken, projectUuid)

    expect(res).toEqual([])
  })

  test('listCaseComment empty', async () => {
    fetch.mockResponseOnce(JSON.stringify([]))

    const res = await casesApi.listCaseComment(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
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
    expect(res).toEqual([])
  })

  test('listCaseComment non-empty', async () => {
    fetch.mockResponseOnce(JSON.stringify(listCaseCommentResponse))

    const res = await casesApi.listCaseComment(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
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
    expect(res).toEqual(listCaseCommentResponse)
  })

  test('createCaseComment', async () => {
    fetch.mockResponseOnce(JSON.stringify(createCaseCommentResponse))

    const payload = { comment: 'This is a case comment' }
    const res = await casesApi.createCaseComment(csrfToken, caseUuid, payload)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(createCaseCommentResponse)
  })

  test('retrieveCaseComment', async () => {
    // Intentionally using the response from createCaseComment as the response for this
    fetch.mockResponseOnce(JSON.stringify(createCaseCommentResponse))

    const res = await casesApi.retrieveCaseComment(csrfToken, caseCommentUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
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
    expect(res).toEqual(createCaseCommentResponse)
  })

  test('updateCaseComment', async () => {
    fetch.mockResponseOnce(JSON.stringify(updateCaseCommentResponse))

    const payload = { comment: 'This is an updated case comment' }
    const res = await casesApi.updateCaseComment(
      csrfToken,
      caseCommentUuid,
      payload
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(updateCaseCommentResponse)
  })

  test('destroyCaseComment', async () => {
    const res = await casesApi.destroyCaseComment(csrfToken, caseCommentUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBeUndefined()
  })

  test('listCasePhenotypeTerms', async () => {
    fetch.mockResponseOnce(JSON.stringify(listCasePhenotypeTermsResponse))

    const res = await casesApi.listCasePhenotypeTerms(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
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
    expect(res).toEqual(listCasePhenotypeTermsResponse)
  })

  test('createCasePhenotypeTerms', async () => {
    // TODO
    fetch.mockResponseOnce(JSON.stringify({}))

    const payload = {}
    const res = await casesApi.createCasePhenotypeTerms(
      csrfToken,
      caseUuid,
      payload
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
      {
        body: JSON.stringify({}),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual({})
  })

  test('retrieveCasePhenotypeTerms', async () => {
    fetch.mockResponseOnce(JSON.stringify(updateCasePhenotypeTermsResponse))

    const res = await casesApi.retrieveCasePhenotypeTerms(
      csrfToken,
      casePhenotypeTermsUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
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
    expect(res).toEqual(updateCasePhenotypeTermsResponse)
  })

  test('updateCasePhenotypeTerms', async () => {
    fetch.mockResponseOnce(JSON.stringify(updateCasePhenotypeTermsResponse))

    const payload = { terms: ['HP:0001129'] }
    const res = await casesApi.updateCasePhenotypeTerms(
      csrfToken,
      casePhenotypeTermsUuid,
      payload
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      {
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(updateCasePhenotypeTermsResponse)
  })

  test('destroyCasePhenotypeTerms', async () => {
    const res = await casesApi.destroyCasePhenotypeTerms(
      csrfToken,
      casePhenotypeTermsUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': 'fake-token',
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBeUndefined()
  })

  test('fetchAnnotationReleaseInfos', async () => {
    fetch.mockResponseOnce(JSON.stringify(fetchAnnotationReleaseInfosResponse))

    const res = await casesApi.fetchAnnotationReleaseInfos(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/annotation-release-info/list/${caseUuid}/`,
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
    expect(res).toEqual(fetchAnnotationReleaseInfosResponse)
  })

  test('fetchSvAnnotationReleaseInfos', async () => {
    fetch.mockResponseOnce(
      JSON.stringify(fetchSvAnnotationReleaseInfosResponse)
    )

    const res = await casesApi.fetchSvAnnotationReleaseInfos(
      csrfToken,
      caseUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/sv-annotation-release-info/list/${caseUuid}/`,
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
    expect(res).toEqual(fetchSvAnnotationReleaseInfosResponse)
  })

  test('fetchCaseGeneAnnotation', async () => {
    fetch.mockResponseOnce(JSON.stringify(fetchCaseGeneAnnotationResponse))

    const res = await casesApi.fetchCaseGeneAnnotation(csrfToken, caseUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/cases/api/case-gene-annotation/list/${caseUuid}/`,
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
    expect(res).toEqual(fetchCaseGeneAnnotationResponse)
  })
})

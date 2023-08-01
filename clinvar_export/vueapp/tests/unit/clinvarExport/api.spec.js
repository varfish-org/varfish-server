import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { rawAppContext } from '../fixtures'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const appContext = {
    baseUrl: rawAppContext.base_url,
    csrfToken: rawAppContext.csrf_token,
  }

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  const expectedXmlArgs = (mimeType) => {
    return Object.freeze({
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: mimeType,
        'X-CSRFToken': appContext.csrfToken,
      },
    })
  }

  const expectedJsonGetArgs = Object.freeze({
    method: 'GET',
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': appContext.csrfToken,
    },
    body: null,
  })

  const expectedJsonCreateArgs = Object.freeze({
    ...expectedJsonGetArgs,
    method: 'POST',
    body: JSON.stringify({ fake: 'payload' }),
  })

  const expectedJsonUpdateArgs = Object.freeze({
    ...expectedJsonCreateArgs,
    method: 'PATCH',
  })
  const expectedJsonDeleteArgs = Object.freeze({
    ...expectedJsonGetArgs,
    method: 'DELETE',
  })

  test('getSubmissionSetXml', async () => {
    fetch.mockResponseOnce('<fake-xml />')

    const res = await clinvarExportApi.getSubmissionSetXml(
      appContext,
      'uuid-arg'
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/clinvar-xml/uuid-arg/`,
      expectedXmlArgs('text/xml'),
    ])
    expect(await res.text()).toEqual('<fake-xml />')
  })

  test('getSubmissionSetValid', async () => {
    fetch.mockResponseOnce(JSON.stringify({ valid: true }))

    const res = await clinvarExportApi.getSubmissionSetValid(
      appContext,
      'uuid-arg'
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/clinvar-validate/uuid-arg/`,
      expectedXmlArgs('application/json'),
    ])
    expect(await res.json()).toEqual({ valid: true })
  })

  test.each([
    ['getOrganisations', clinvarExportApi.getOrganisations, 'organisation'],
    ['getFamilies', clinvarExportApi.getFamilies, 'family'],
    ['getSubmitters', clinvarExportApi.getSubmitters, 'submitter'],
    [
      'getAssertionMethods',
      clinvarExportApi.getAssertionMethods,
      'assertion_method',
    ],
    ['getSubmissionSets', clinvarExportApi.getSubmissionSets, 'submission_set'],
    ['getSubmissions', clinvarExportApi.getSubmissions, 'submission'],
    [
      'getSubmissionIndividuals',
      clinvarExportApi.getSubmissionIndividuals,
      'submission_individual',
    ],
    ['getIndividuals', clinvarExportApi.getIndividuals, 'individual'],
    ['getSubmittingOrgs', clinvarExportApi.getSubmittingOrgs, 'submitting_org'],
  ])('get via API %p', async (_label, func, entity) => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const res = await func(appContext, 'uuid-arg')

    expect(fetch.mock.calls.length).toEqual(1)
    const entityNoUnder = entity.replace('_', '')
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/${entityNoUnder}/`,
      expectedJsonGetArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })

  test.each([
    [
      'createSubmissionSet',
      clinvarExportApi.createSubmissionSet,
      'submission_set',
    ],
    ['createSubmission', clinvarExportApi.createSubmission, 'submission'],
    [
      'createSubmissionIndividual',
      clinvarExportApi.createSubmissionIndividual,
      'submission_individual',
    ],
    [
      'createSubmittingOrg',
      clinvarExportApi.createSubmittingOrg,
      'submitting_org',
    ],
  ])('create via API %p', async (_label, func, entity) => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const payload = { fake: 'payload' }
    const res = await func(payload, appContext)

    expect(fetch.mock.calls.length).toEqual(1)
    const entityNoUnder = entity.replace('_', '')
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/${entityNoUnder}/`,
      expectedJsonCreateArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })

  test.each([
    [
      'updateSubmissionSet',
      clinvarExportApi.updateSubmissionSet,
      'submission_set',
    ],
    ['updateSubmission', clinvarExportApi.updateSubmission, 'submission'],
    [
      'updateSubmissionIndividual',
      clinvarExportApi.updateSubmissionIndividual,
      'submission_individual',
    ],
    [
      'updateSubmittingOrg',
      clinvarExportApi.updateSubmittingOrg,
      'submitting_org',
    ],
  ])('update via API %p', async (_label, func, entity) => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const payload = { fake: 'payload' }
    const res = await func(payload, appContext)

    expect(fetch.mock.calls.length).toEqual(1)
    const entityNoUnder = entity.replace('_', '')
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/${entityNoUnder}/`,
      expectedJsonUpdateArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })

  test.each([
    [
      'deleteSubmissionSet',
      clinvarExportApi.deleteSubmissionSet,
      'submission_set',
    ],
    ['deleteSubmission', clinvarExportApi.deleteSubmission, 'submission'],
    [
      'deleteSubmissionIndividual',
      clinvarExportApi.deleteSubmissionIndividual,
      'submission_individual',
    ],
    [
      'deleteSubmittingOrg',
      clinvarExportApi.deleteSubmittingOrg,
      'submitting_org',
    ],
  ])('delete via API %p', async (_label, func, entity) => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const payload = { fake: 'payload' }
    const res = await func(payload, appContext)

    expect(fetch.mock.calls.length).toEqual(1)
    const entityNoUnder = entity.replace('_', '')
    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/${entityNoUnder}/`,
      expectedJsonDeleteArgs,
    ])
    expect(res).toBeUndefined()
  })

  test('getUserAnnotations', async () => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const res = await clinvarExportApi.getUserAnnotations(
      appContext,
      'family-uuid'
    )

    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/user-annotations/family-uuid`,
      expectedJsonGetArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })

  test('genericTermQuery', async () => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const res = await clinvarExportApi.genericTermQuery(
      appContext,
      'name',
      'label',
      'term-id'
    )

    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/query-name/?query=term-id`,
      expectedJsonGetArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })

  test.each([
    ['queryOmim', 'omim', clinvarExportApi.queryOmim],
    ['queryHpo', 'hpo', clinvarExportApi.queryHpo],
  ])('query: %p', async (_label, name, func) => {
    fetch.mockResponseOnce(JSON.stringify({ fake: 'result' }))

    const res = await func(appContext, 'term-id')

    expect(fetch.mock.calls[0]).toEqual([
      `${appContext.baseUrl}/query-${name}/?query=term-id`,
      expectedJsonGetArgs,
    ])
    expect(res).toEqual({ fake: 'result' })
  })
})

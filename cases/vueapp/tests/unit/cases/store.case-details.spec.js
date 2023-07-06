import casesApi from '@cases/api/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details.js'
import { StoreState, useCasesStore } from '@cases/stores/cases.js'
import flushPromises from 'flush-promises'
import { createPinia, setActivePinia } from 'pinia'
import {
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

import caseListResponse from '../../data/caseListResponse.json'
import fetchAnnotationReleaseInfosResponse from '../../data/fetchAnnotationReleaseInfosResponse.json'
import fetchCaseAlignmentStatsResponse from '../../data/fetchCaseAlignmentStatsResponse.json'
import fetchCaseGeneAnnotationResponse from '../../data/fetchCaseGeneAnnotationResponse.json'
import fetchCaseRelatednessResponse from '../../data/fetchCaseRelatednessResponse.json'
import fetchCaseVariantStatsResponse from '../../data/fetchCaseVariantStatsResponse.json'
import fetchSvAnnotationReleaseInfosResponse from '../../data/fetchSvAnnotationReleaseInfosResponse.json'
import listCaseCommentResponse from '../../data/listCaseCommentResponse.json'
import listCasePhenotypeTermsResponse from '../../data/listCasePhenotypeTermsResponse.json'
import caseRetrieveResponse from '../../data/retrieveCaseResponse.json'

// Mock out the cases API
vi.mock('@cases/api/cases.js')

export function copy(obj) {
  return JSON.parse(JSON.stringify(obj))
}

describe('case-details store', () => {
  const caseUuid = 'fake-uuid'
  const csrfToken = 'fake-token'
  const appContext = {
    csrf_token: csrfToken,
    project: {
      sodar_uuid: 'fake-uuid',
      title: 'fake-title',
    },
  }
  let caseDetailsStore
  let casesStore

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    caseDetailsStore = useCaseDetailsStore()
    casesStore = useCasesStore()
    casesApi.listCase.mockResolvedValue(caseListResponse)
    const allPerms = [
      'cases.view_data',
      'cases.add_case',
      'cases.update_case',
      'cases.sync_remote',
    ]
    casesApi.fetchPermissions.mockResolvedValue(copy(allPerms))

    // Initialize the case store, required for case-details store
    casesStore.initialize(appContext)

    // Prepare API mocks
    casesApi.retrieveCase.mockResolvedValue(copy(caseRetrieveResponse))
    casesApi.listCaseComment.mockResolvedValue(copy(listCaseCommentResponse))
    casesApi.fetchVarAnnos.mockResolvedValue([])
    casesApi.fetchSvAnnos.mockResolvedValue([])
    casesApi.fetchCaseGeneAnnotation.mockResolvedValue(
      copy(fetchCaseGeneAnnotationResponse)
    )
    casesApi.fetchCaseVariantStats.mockResolvedValue(
      copy(fetchCaseVariantStatsResponse)
    )
    casesApi.fetchCaseRelatedness.mockResolvedValue(
      copy(fetchCaseRelatednessResponse)
    )
    casesApi.listCasePhenotypeTerms.mockResolvedValue(
      copy(listCasePhenotypeTermsResponse)
    )
    casesApi.fetchAnnotationReleaseInfos.mockResolvedValue(
      copy(fetchAnnotationReleaseInfosResponse)
    )
    casesApi.fetchSvAnnotationReleaseInfos.mockResolvedValue(
      copy(fetchSvAnnotationReleaseInfosResponse)
    )
    casesApi.fetchCaseAlignmentStats.mockResolvedValue(
      copy(fetchCaseAlignmentStatsResponse)
    )
    casesApi.fetchPermissions.mockResolvedValue(copy(allPerms))
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('empty after construction', () => {
    expect(caseDetailsStore.caseObj).toEqual(null)
    expect(caseDetailsStore.caseComments).toEqual(null)
    expect(caseDetailsStore.geneAnnotations).toEqual(null)
    expect(caseDetailsStore.varAnnos).toEqual(null)
    expect(caseDetailsStore.varAnnoList).toEqual([])
    expect(caseDetailsStore.varComments).toEqual(null)
    expect(caseDetailsStore.varCommentList).toEqual([])
    expect(caseDetailsStore.acmgRatings).toEqual(null)
    expect(caseDetailsStore.acmgRatingList).toEqual([])
    expect(caseDetailsStore.svAnnos).toEqual(null)
    expect(caseDetailsStore.svAnnoList).toEqual([])
    expect(caseDetailsStore.svComments).toEqual(null)
    expect(caseDetailsStore.svCommentList).toEqual([])
  })

  test('initialize', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    expect(casesApi.retrieveCase).toHaveBeenCalledWith(csrfToken, caseUuid)
    expect(casesApi.listCaseComment).toHaveBeenCalledWith(csrfToken, caseUuid)
    expect(casesApi.fetchCaseGeneAnnotation).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.fetchCaseVariantStats).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.fetchCaseRelatedness).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.listCasePhenotypeTerms).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.fetchAnnotationReleaseInfos).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.fetchSvAnnotationReleaseInfos).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )
    expect(casesApi.fetchCaseAlignmentStats).toHaveBeenCalledWith(
      csrfToken,
      caseUuid
    )

    expect(caseDetailsStore.storeState).toEqual(StoreState.active)
    expect(casesStore.serverInteractions).toEqual(0)
    // expect(caseDetailsStore.caseUuid).toEqual('fake-uuid')
    expect(caseDetailsStore.caseObj).toEqual(caseRetrieveResponse)
    expect(caseDetailsStore.caseComments).toEqual(listCaseCommentResponse)
    expect(caseDetailsStore.geneAnnotations).toEqual(
      fetchCaseGeneAnnotationResponse
    )
    expect(caseDetailsStore.varAnnos).toEqual([])
    // expect(caseDetailsStore.varAnnoList).toEqual()
    expect(caseDetailsStore.varComments).toEqual(null)
    expect(caseDetailsStore.varCommentList).toEqual([])
    expect(caseDetailsStore.acmgRatings).toEqual(null)
    expect(caseDetailsStore.acmgRatingList).toEqual([])
    expect(caseDetailsStore.svAnnos).toEqual([])
    // expect(caseDetailsStore.svAnnoList).toEqual()
    expect(caseDetailsStore.svComments).toEqual(null)
    expect(caseDetailsStore.svCommentList).toEqual([])
    expect(caseDetailsStore.caseAlignmentStats).toEqual(
      fetchCaseAlignmentStatsResponse[0]
    )
    // expect(caseDetailsStore.caseVariantStats).toEqual(fetchCaseVariantStatsResponse[0])
    expect(caseDetailsStore.caseRelatedness).toEqual(
      fetchCaseRelatednessResponse
    )
    expect(caseDetailsStore.casePhenotypeTerms).toEqual(
      listCasePhenotypeTermsResponse
    )
    expect(caseDetailsStore.caseAnnotationReleaseInfos).toEqual(
      fetchAnnotationReleaseInfosResponse
    )
    expect(caseDetailsStore.caseSvAnnotationReleaseInfos).toEqual(
      fetchSvAnnotationReleaseInfosResponse
    )
  })

  test('already initialized', async () => {
    caseDetailsStore.storeState = StoreState.active
    caseDetailsStore.caseObj = caseRetrieveResponse
    caseDetailsStore.caseObj.sodar_uuid = caseUuid
    await caseDetailsStore.initialize(caseUuid)

    flushPromises()

    expect(casesApi.retrieveCase).not.toHaveBeenCalled()
    expect(casesApi.listCaseComment).not.toHaveBeenCalled()
    expect(casesApi.fetchCaseGeneAnnotation).not.toHaveBeenCalled()
    expect(casesApi.fetchCaseVariantStats).not.toHaveBeenCalled()
    expect(casesApi.fetchCaseRelatedness).not.toHaveBeenCalled()
    expect(casesApi.listCasePhenotypeTerms).not.toHaveBeenCalled()
    expect(casesApi.fetchAnnotationReleaseInfos).not.toHaveBeenCalled()
    expect(casesApi.fetchSvAnnotationReleaseInfos).not.toHaveBeenCalled()
    expect(casesApi.fetchCaseAlignmentStats).not.toHaveBeenCalled()
  })

  test('updateCase', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    casesApi.updateCase.mockResolvedValue(caseRetrieveResponse)

    await caseDetailsStore.updateCase({ payload: 'fake-payload' })
    flushPromises()

    expect(casesApi.updateCase).toHaveBeenCalledWith(csrfToken, caseUuid, {
      payload: 'fake-payload',
    })
  })

  test('getCaseComment empty', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const result = caseDetailsStore.getCaseComment('fake-comment-uuid')

    expect(result).toEqual(null)
  })

  test('getCaseComment', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const result = caseDetailsStore.getCaseComment(
      listCaseCommentResponse[0].sodar_uuid
    )

    expect(result).toEqual(listCaseCommentResponse[0])
  })

  test('createCaseComment', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    expect(caseDetailsStore.caseComments.length).toEqual(2)

    const newCaseComment = {
      sodar_uuid: 'fake-comment-uuid',
      date_created: '2023-05-12T08:09:41.958458Z',
      date_modified: '2023-05-12T08:09:41.958471Z',
      case: '45847808-31a1-4f98-945f-675195708160',
      user: 'user',
      comment: 'This is a new comment',
    }

    casesApi.createCaseComment.mockResolvedValue(newCaseComment)

    await caseDetailsStore.createCaseComment({ payload: 'fake-payload' })
    flushPromises()

    expect(casesApi.createCaseComment).toHaveBeenCalledWith(
      csrfToken,
      caseUuid,
      { payload: 'fake-payload' }
    )
    expect(caseDetailsStore.caseComments.length).toEqual(3)
    expect(caseDetailsStore.caseComments[2]).toEqual(newCaseComment)
  })

  test('updateCaseComment', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const updatedCaseComment = copy(listCaseCommentResponse[0])
    updatedCaseComment.comment = 'fake-comment'

    casesApi.updateCaseComment.mockResolvedValue(updatedCaseComment)

    await caseDetailsStore.updateCaseComment(updatedCaseComment.sodar_uuid, {
      payload: 'fake-payload',
    })
    flushPromises()

    expect(casesApi.updateCaseComment).toHaveBeenCalledWith(
      csrfToken,
      updatedCaseComment.sodar_uuid,
      { payload: 'fake-payload' }
    )
    expect(caseDetailsStore.caseComments[0]).toEqual(updatedCaseComment)
  })

  test('destroyCaseComment', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    expect(caseDetailsStore.caseComments.length).toEqual(2)

    casesApi.destroyCaseComment.mockResolvedValue()

    await caseDetailsStore.destroyCaseComment(
      listCaseCommentResponse[0].sodar_uuid
    )
    flushPromises()

    expect(casesApi.destroyCaseComment).toBeCalledWith(
      csrfToken,
      listCaseCommentResponse[0].sodar_uuid
    )
    expect(caseDetailsStore.caseComments.length).toEqual(1)
  })

  test('getCasePhenotypeTerms', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const response = await caseDetailsStore.getCasePhenotypeTerms(
      listCasePhenotypeTermsResponse[1].sodar_uuid
    )

    expect(response).toEqual(listCasePhenotypeTermsResponse[1])
  })

  test('updateCasePhenotypeTerms', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const updatedCasePhenotypeTerms = copy(listCasePhenotypeTermsResponse[0])
    updatedCasePhenotypeTerms.terms.push('HP:0000001')

    casesApi.updateCasePhenotypeTerms.mockResolvedValue(
      updatedCasePhenotypeTerms
    )

    await caseDetailsStore.updateCasePhenotypeTerms(
      listCasePhenotypeTermsResponse[0].sodar_uuid,
      { payload: 'fake-payload' }
    )
    flushPromises()

    expect(casesApi.updateCasePhenotypeTerms).toBeCalledWith(
      csrfToken,
      listCasePhenotypeTermsResponse[0].sodar_uuid,
      { payload: 'fake-payload' }
    )
    expect(caseDetailsStore.casePhenotypeTerms[0]).toEqual(
      updatedCasePhenotypeTerms
    )
  })

  test('createCasePhenotypeTerms', async () => {
    await caseDetailsStore.initialize(caseUuid)
    flushPromises()

    const newCasePhenotypeTerms = {
      sodar_uuid: 'fake-pheno-uuid',
      date_created: '2023-05-10T11:18:09.901786Z',
      date_modified: '2023-05-10T11:51:39.315253Z',
      case: '45847808-31a1-4f98-945f-675195708160',
      individual: 'Case_1_sibling-N1-DNA1-WGS1',
      terms: ['HP:1111111'],
    }

    casesApi.createCasePhenotypeTerms.mockResolvedValue(newCasePhenotypeTerms)

    await caseDetailsStore.createCasePhenotypeTerms(caseUuid, {
      payload: 'fake-payload',
    })
    flushPromises()

    expect(casesApi.createCasePhenotypeTerms).toBeCalledWith(
      csrfToken,
      caseUuid,
      { payload: 'fake-payload' }
    )
    expect(caseDetailsStore.casePhenotypeTerms.length).toEqual(4)
    expect(caseDetailsStore.casePhenotypeTerms[3]).toEqual(
      newCasePhenotypeTerms
    )
  })
})

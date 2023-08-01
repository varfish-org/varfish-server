import { useCaseDetailsStore } from '@cases/stores/case-details'
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

describe('case-details store', () => {
  let caseDetailsStore

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    caseDetailsStore = useCaseDetailsStore()
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

  // test('initialize', async () => {
  // })
})

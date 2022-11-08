import CaseDetailCardTerms from '@cases/components/CaseDetailCardTerms.vue'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('CaseDetailCardTerms.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  test('test with empty data', async () => {
    fetch.mockResponse(JSON.stringify([]))
    const wrapper = makeWrapper(CaseDetailCardTerms)

    expect(wrapper.html()).matches(/No inviduals in case/)
    expect(wrapper.html()).not.matches(/<strong.*?>NA12878<\/strong>/)
  })

  test('test with case detail store data', async () => {
    fetch.mockResponse(JSON.stringify([]))
    const wrapper = makeWrapper(CaseDetailCardTerms, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No inviduals in case/)
    expect(wrapper.html()).matches(/<strong.*?>NA12878<\/strong>/)
  })
})

import CaseDetailCardTerms from '@cases/components/CaseDetailCardTerms.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

describe('CaseDetailCardTerms.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardTerms)

    expect(wrapper.html()).matches(/No inviduals in case/)
    expect(wrapper.html()).not.matches(/<strong>NA12878<\/strong>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardTerms, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No inviduals in case/)
    expect(wrapper.html()).matches(/<strong>NA12878<\/strong>/)
  })
})

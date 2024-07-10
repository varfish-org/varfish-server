import CaseDetailCardAlignmentQc from '@/cases/components/CaseDetail/CardAlignmentQc.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetail/CardAlignmentQc.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardAlignmentQc)

    expect(wrapper.html()).matches(/No coverage information provided/)
    expect(wrapper.html()).not.matches(/<th.*>NA12878<\/th>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardAlignmentQc, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No coverage information provided/)
    expect(wrapper.html()).matches(/<th.*>NA12878<\/th>/)
  })
})

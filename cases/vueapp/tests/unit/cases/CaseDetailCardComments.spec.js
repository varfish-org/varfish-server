import CaseDetailCardComments from '@cases/components/CaseDetailCardComments.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

describe('CaseDetailCardComments.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardComments)

    expect(wrapper.html()).matches(/No case comments \(yet\)/)
    expect(wrapper.html()).not.matches(/<strong>root<\/strong>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardComments, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No case comments \(yet\)/)
    expect(wrapper.html()).matches(/<strong>root<\/strong>/)
  })
})

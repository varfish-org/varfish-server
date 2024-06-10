import CaseDetailCardCase from '@cases/components/CaseDetail/CardCase.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardCase.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardCase)

    expect(wrapper.html()).matches(/No notes taken \(yet\)/)
    expect(wrapper.html()).not.matches(/Here are some notes/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardCase, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No notes taken \(yet\)/)
    expect(wrapper.html()).matches(/Here are some notes/)
  })
})

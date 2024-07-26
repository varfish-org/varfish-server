import CaseDetailCardSvInfo from '@/cases/components/CaseDetail/CardSvInfo.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardSvInfo.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardSvInfo)

    expect(wrapper.html()).matches(/No SV annotation info./)
    expect(wrapper.html()).not.matches(/<td.*>GRCh37<\/td>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardSvInfo, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No SV annotation info./)
    expect(wrapper.html()).matches(/<td.*>GRCh37<\/td>/)
  })
})

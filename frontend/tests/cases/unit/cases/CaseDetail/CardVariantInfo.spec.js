import { beforeAll, describe, expect, test, vi } from 'vitest'

import CaseDetailCardVariantInfo from '@/cases/components/CaseDetail/CardVariantInfo.vue'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardVariantInfo.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardVariantInfo)

    expect(wrapper.html()).matches(/No \(small\) variant annotation info./)
    expect(wrapper.html()).not.matches(/<td.*>GRCh37<\/td>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardVariantInfo, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No \(small\) variant annotation info./)
    expect(wrapper.html()).matches(/<td.*>GRCh37<\/td>/)
  })
})

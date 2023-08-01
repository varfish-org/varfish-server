import CaseDetailCardVariantQc from '@cases/components/CaseDetail/CardVariantQc.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardVariantQc.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardVariantQc)

    expect(wrapper.html()).matches(/No variant QC info provided/)
    expect(wrapper.html()).not.matches(/<td class="font-weight-bold">/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardVariantQc, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No variant QC info provided./)
    expect(wrapper.html()).matches(/<td class="font-weight-bold">/)
  })
})

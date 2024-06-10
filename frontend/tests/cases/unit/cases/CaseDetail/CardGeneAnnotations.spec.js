import CaseDetailCardGeneAnnotations from '@/cases/components/CaseDetail/CardGeneAnnotations.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardGeneAnnotations.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardGeneAnnotations)

    expect(wrapper.html()).matches(/No gene annotations \(yet\)./)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardGeneAnnotations, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No gene annotations \(yet\)./)
  })
})

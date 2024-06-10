import CaseDetailCardPedigree from '@cases/components/CaseDetail/CardPedigree.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailCardPedigree.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailCardPedigree)

    expect(wrapper.html()).matches(/No individuals in case./)
    expect(wrapper.html()).not.matches(/NA12878/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(CaseDetailCardPedigree, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).not.matches(/No individuals in case./)
    expect(wrapper.html()).matches(/NA12878/)
  })
})

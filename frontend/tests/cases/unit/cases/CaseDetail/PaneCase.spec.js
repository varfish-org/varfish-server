import { beforeAll, describe, expect, test, vi } from 'vitest'

import CaseDetailPaneCase from '@/cases/components/CaseDetail/PaneCase.vue'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import caseListStoreData from '../../../data/caseListStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailPaneCase.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailPaneCase)

    expect(wrapper.findAll('case-detail-card-case-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-pedigree-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-variants-info-stub').length).toBe(
      1,
    )
    expect(wrapper.findAll('case-detail-card-sv-info-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-case-comments-stub').length).toBe(
      1,
    )
    expect(wrapper.findAll('case-detail-card-terms-stub').length).toBe(1)
    expect(
      wrapper.findAll('case-detail-card-case-annotations-stub').length,
    ).toBe(1)
    expect(wrapper.findAll('case-detail-card-alignment-qc-stub').length).toBe(1)
    expect(
      wrapper.findAll('case-detail-card-gene-annotations-stub').length,
    ).toBe(1)
  })

  test('test with case detail store data', async () => {
    const initialState = {
      cases: caseListStoreData,
      caseDetails: caseDetailsStoreData,
    }
    const wrapper = makeWrapper(CaseDetailPaneCase, initialState)

    expect(wrapper.findAll('case-detail-card-case-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-pedigree-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-variants-info-stub').length).toBe(
      1,
    )
    expect(wrapper.findAll('case-detail-card-sv-info-stub').length).toBe(1)
    expect(wrapper.findAll('case-detail-card-case-comments-stub').length).toBe(
      1,
    )
    expect(wrapper.findAll('case-detail-card-terms-stub').length).toBe(1)
    expect(
      wrapper.findAll('case-detail-card-case-annotations-stub').length,
    ).toBe(1)
    expect(wrapper.findAll('case-detail-card-alignment-qc-stub').length).toBe(1)
    expect(
      wrapper.findAll('case-detail-card-gene-annotations-stub').length,
    ).toBe(1)
  })
})

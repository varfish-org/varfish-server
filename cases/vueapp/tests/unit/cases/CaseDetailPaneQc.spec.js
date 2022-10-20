import CaseDetailPaneQc from '@cases/components/CaseDetailPaneQc.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import casesStoreData from '../../data/casesStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

describe('CaseDetailPaneQc.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailPaneQc)

    expect(wrapper.findAll('qc-plot-relatedness-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-depth-het-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-chr-x-ratio-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-var-type-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-var-effect-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-indel-size-stub').length).toBe(1)
    expect(wrapper.findAll('qc-table-var-stats-stub').length).toBe(1)
  })

  test('test with case detail store data', async () => {
    const initialState = {
      cases: casesStoreData,
      caseDetails: caseDetailsStoreData,
    }
    const wrapper = makeWrapper(CaseDetailPaneQc, initialState)

    expect(wrapper.findAll('qc-plot-relatedness-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-depth-het-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-chr-x-ratio-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-var-type-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-var-effect-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-indel-size-stub').length).toBe(1)
    expect(wrapper.findAll('qc-table-var-stats-stub').length).toBe(1)
  })
})

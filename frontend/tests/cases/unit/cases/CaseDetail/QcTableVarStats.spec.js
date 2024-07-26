import QcTableVarStats from '@/cases/components/CaseDetail/QcTableVarStats.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('QcTableVarStats.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper(QcTableVarStats)

    expect(wrapper.findAll('table').length).toBe(1)
    expect(wrapper.html()).toMatch(/No variant statistics to display./)
  })

  // TODO Fix me
  test('test with data data', async () => {
    // console.log(caseDetailsStoreData.caseVariantStats)
    const varStats = Object.entries(caseDetailsStoreData.caseVariantStats).map(
      ([name, stats]) => {
        return {
          sample_name: name,
          ...stats,
        }
      },
    )

    const wrapper = makeWrapper(QcTableVarStats, caseDetailsStoreData, {
      varStats: varStats,
    })

    expect(wrapper.findAll('table').length).toBe(1)
    expect(wrapper.html()).toMatch(/<td.*>NA12878<\/td>/)
  })
})

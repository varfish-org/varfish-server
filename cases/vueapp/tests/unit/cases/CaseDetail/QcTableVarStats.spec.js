import QcTableVarStats from '@cases/components/CaseDetail/QcTableVarStats.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'

const makeWrapper = (varStats) => {
  return mount(QcTableVarStats, {
    props: {
      varStats: varStats,
    },
  })
}

describe('QcTableVarStats.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper(null)

    expect(wrapper.findAll('table').length).toBe(1)
    expect(wrapper.html()).toMatch(/No variant statistics to display./)
  })

  test('test with data data', async () => {
    const varStats = Object.entries(caseDetailsStoreData.caseVariantStats).map(
      ([name, stats]) => {
        return {
          sample_name: name,
          ...stats,
        }
      },
    )
    const wrapper = makeWrapper(varStats)

    expect(wrapper.findAll('table').length).toBe(1)
    expect(wrapper.html()).toMatch(/<td>NA12878<\/td>/)
  })
})

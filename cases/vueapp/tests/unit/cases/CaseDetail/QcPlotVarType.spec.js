import QcPlotVarType from '@cases/components/CaseDetail/QcPlotVarType.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'

const makeWrapper = (variantStats = {}) => {
  return mount(QcPlotVarType, {
    props: {
      renderer: 'svg',
      variantStats,
    },
  })
}

describe('QcPlotVarType.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper(null)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /Histograms with variant type counts for each sample/
    )
  })

  test('test with some data', async () => {
    const caseVariantStats = caseDetailsStoreData.caseVariantStats
    const wrapper = makeWrapper({
      NA12878: caseVariantStats['NA12878-N1-DNA1-WES1'],
      NA12891: caseVariantStats['NA12891-N1-DNA1-WES1'],
      NA12892: caseVariantStats['NA12892-N1-DNA1-WES1'],
    })

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /Histograms with variant type counts for each sample/
    )
  })
})

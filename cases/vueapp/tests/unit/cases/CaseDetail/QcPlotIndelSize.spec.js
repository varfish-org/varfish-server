import QcPlotIndelSize from '@cases/components/CaseDetail/QcPlotIndelSize.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (props = {}) => {
  return mount(QcPlotIndelSize, {
    props: {
      renderer: 'svg',
      ...props,
    },
  })
}

describe('QcPlotIndelSize.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper()

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /Histograms with indel sizes for each sample/
    )
  })

  test('test with some data', async () => {
    const props = {
      variantStats: {
        NA12878: {
          ontarget_indel_sizes: {
            '-11': 10,
            1: 10,
            2: 20,
            11: 10,
          },
        },
      },
    }
    const wrapper = makeWrapper(props)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /Histograms with indel sizes for each sample/
    )
  })
})

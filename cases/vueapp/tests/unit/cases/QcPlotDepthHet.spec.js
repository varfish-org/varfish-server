import QcPlotDepthHet from '@cases/components/QcPlotDepthHet.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (props = {}) => {
  return mount(QcPlotDepthHet, {
    props: {
      renderer: 'svg',
      ...props,
    },
  })
}

describe('QcPlotDepthHet.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper()

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      / Plot of heterozygous genotype ratio to depth of coverage /
    )
  })

  const propsFragment = {
    hetRatioQuantiles: [
      0.04383295417758679, 0.1344037831317821, 0.22497461208597744,
      0.23320129400756537, 0.2414279759291533,
    ],
    dpQuantiles: [-1, 1, 3, 3, 3],
    dpHetData: [
      { x: 3, y: 0.2414279759291533, sample: 'NA12878' },
      { x: 3, y: 0.22497461208597744, sample: 'NA12891' },
      { x: -1, y: 0.04383295417758679, sample: 'NA12892' },
    ],
  }

  test('test with some data and no outliers', async () => {
    const wrapper = makeWrapper(propsFragment)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      / Plot of heterozygous genotype ratio to depth of coverage /
    )
  })

  test('test with some data and some outliers', async () => {
    const localFragments = {
      ...propsFragment,
      dpQuantiles: [10, 20, 30, 40, 50],
      dpHetData: [
        { x: 10000, y: 0.2414279759291533, sample: 'NA12878' },
        { x: 30, y: 0.22497461208597744, sample: 'NA12891' },
        { x: 30, y: 1000, sample: 'NA12892' },
      ],
    }
    const wrapper = makeWrapper(localFragments)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      / Plot of heterozygous genotype ratio to depth of coverage /
    )
  })
})

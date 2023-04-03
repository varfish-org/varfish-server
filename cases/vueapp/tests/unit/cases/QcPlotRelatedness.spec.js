import QcPlotRelatedness from '@cases/components/QcPlotRelatedness.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (relData = []) => {
  return mount(QcPlotRelatedness, {
    props: {
      renderer: 'svg',
      relData,
    },
  })
}

describe('QcPlotRelatedness.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper(null)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(/Plot of relatedness coefficient vs. IBS0/)
  })

  test('test with some data', async () => {
    const relData = [
      {
        ibs0: 2,
        rel: 1.0262426847746502,
        sample0: 'NA12891',
        sample1: 'NA12878',
        sibSib: false,
        parentChild: true,
      },
      {
        ibs0: 5,
        rel: 0.9774101961748356,
        sample0: 'NA12892',
        sample1: 'NA12878',
        sibSib: false,
        parentChild: true,
      },
      {
        ibs0: 390,
        rel: 0.05419055817300081,
        sample0: 'NA12892',
        sample1: 'NA12891',
        sibSib: false,
        parentChild: false,
      },
    ]
    const wrapper = makeWrapper(relData)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(/Plot of relatedness coefficient vs. IBS0/)
  })
})

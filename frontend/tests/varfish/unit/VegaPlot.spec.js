import VegaPlot from '@varfish/components/VegaPlot.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

describe('VegaPlot.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  const dataValues1 = [{ x: 0, y: 0 }]
  // const dataValues2 = [
  //         { x: 0, y: 0 },
  //         { x: 1, y: 1 },
  //       ]
  const props = {
    renderer: 'svg',
    description: 'Some description',
    dataValues: dataValues1,
    encoding: {
      x: {
        field: 'x',
        type: 'quantitative',
      },
      1: {
        field: 'y',
        type: 'quantitative',
      },
    },
    mark: {
      type: 'line',
    },
  }

  test('render with initial data', async () => {
    const wrapper = mount(VegaPlot, {
      props,
    })

    await wrapper.vm.getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(/for a linear scale with values from 0 to 0/)
  })

  test('render with no initial data data', async () => {
    const wrapper = mount(VegaPlot, {
      props: {
        ...props,
        dataValues: null,
      },
    })

    await wrapper.vm.getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /for a linear scale with values from NaN to NaN/,
    )
  })

  test('inject data', async () => {
    const wrapper = mount(VegaPlot, {
      props: {
        ...props,
        dataValues: null,
      },
    })

    await wrapper.vm.getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(
      /for a linear scale with values from NaN to NaN/,
    )

    // TOOD: for some reason the watch() in VegaPlot causes the test to hang.
    // wrapper.setProps({dataValues: dataValues2})
    //
    // expect(wrapper.html()).toMatch(/for a linear scale with values from 0 to 0/)
  })
})

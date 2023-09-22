import FragmentLengthHistogramPlot from '@cases_qc/components/FragmentLengthHistogramPlot.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

describe('FragmentLengthHistogramPlot.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })
  test('render without message', () => {
    const wrapper = mount(FragmentLengthHistogramPlot)

    expect(wrapper.findAll('.spinner-border').length).toBe(1)
  })

  test('render with message', () => {
    const wrapper = mount(FragmentLengthHistogramPlot, {
      props: {
        message: 'Hello World!',
      },
    })

    expect(wrapper.findAll('.spinner-border').length).toBe(1)
    expect(wrapper.findAll('.text-muted')[0].html()).toMatch(/Hello World!/)
  })
})

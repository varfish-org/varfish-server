import QcPlotChrXRatio from '@cases/components/QcPlotChrXRatio.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (props = {}) => {
  return mount(QcPlotChrXRatio, {
    props: {
      renderer: 'svg',
      ...props,
    },
  })
}

describe('QcPlotChrXRatio.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data', async () => {
    const wrapper = makeWrapper()

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(/Plot of het. call ratio on chrX/)
  })

  test('test with some data', async () => {
    const props = {
      pedigree: [
        {
          sex: 2,
          father: 'NA12891-N1-DNA1-WES1',
          mother: 'NA12892-N1-DNA1-WES1',
          name: 'NA12878-N1-DNA1-WES1',
          affected: 2,
          has_gt_entries: true,
        },
        {
          sex: 1,
          father: '0',
          mother: '0',
          name: 'NA12891-N1-DNA1-WES1',
          affected: 1,
          has_gt_entries: true,
        },
        {
          sex: 0,
          father: '0',
          mother: '0',
          name: 'NA12892-N1-DNA1-WES1',
          affected: 1,
          has_gt_entries: true,
        },
      ],
      sexErrors: {
        'NA12878-N1-DNA1-WES1': ['some example error'],
        'NA12892-N1-DNA1-WES1': ['sex set to 0/unknown'],
      },
      chrXHetHomRatio: {
        'NA12878-N1-DNA1-WES1': 2.0914893617021275,
        'NA12891-N1-DNA1-WES1': 0.29952830188679247,
        'NA12892-N1-DNA1-WES1': 1.6457023060796645,
      },
    }
    const wrapper = makeWrapper(props)

    await wrapper.vm.getVegaPlot().getVegaEmbedPromise()

    expect(wrapper.findAll('svg').length).toBe(2)
    expect(wrapper.html()).toMatch(/Plot of het. call ratio on chrX/)
  })
})

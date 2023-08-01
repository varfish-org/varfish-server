import CaseListPaneQc from '@cases/components/CaseList/PaneQc.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, test, vi } from 'vitest'

import casesQcStoreData from '../../../data/casesQcStoreData.json'

const makeWrapper = (casesQcState = {}) => {
  return mount(CaseListPaneQc, {
    shallow: true,
    props: {
      renderer: 'svg',
    },
    global: {
      plugins: [
        createTestingPinia({
          initialState: { casesQc: casesQcState },
          createSpy: vi.fn,
        }),
      ],
    },
  })
}

describe('CaseListPaneQc.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with null data in store', () => {
    const wrapper = makeWrapper({})

    expect(wrapper.findAll('qc-table-var-stats-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-relatedness-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-depth-het-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-chr-x-ratio-stub').length).toBe(1)
  })

  test('test with qc data in store', () => {
    const wrapper = makeWrapper(casesQcStoreData)

    expect(wrapper.findAll('qc-table-var-stats-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-relatedness-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-depth-het-stub').length).toBe(1)
    expect(wrapper.findAll('qc-plot-chr-x-ratio-stub').length).toBe(1)
  })
})

describe('CaseListPaneQc.vue downloads', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  test('test download per sample metric clicked', () => {
    const wrapper = makeWrapper(casesQcStoreData)

    const mockElement = vi.fn()
    mockElement.setAttribute = vi.fn()
    mockElement.style = {}
    mockElement.click = vi.fn()
    vi.spyOn(document, 'createElement').mockImplementation(vi.fn())
    document.createElement.mockReturnValueOnce(mockElement)
    vi.spyOn(document.body, 'appendChild').mockImplementation(vi.fn())
    vi.spyOn(document.body, 'removeChild').mockImplementation(vi.fn())

    expect(wrapper.findAll('.download-per-sample').length).toBe(1)
    wrapper.findAll('.download-per-sample')[0].wrapperElement.click()

    expect(document.createElement).toHaveBeenCalled(1)
    expect(document.createElement).toHaveBeenNthCalledWith(1, 'a')
    expect(mockElement.setAttribute).toHaveBeenCalled(2)
    expect(mockElement.setAttribute).toHaveBeenNthCalledWith(
      1,
      'href',
      expect.stringMatching(/^data:application\/octet-stream;base64,/),
    )
    expect(mockElement.setAttribute).toHaveBeenNthCalledWith(
      2,
      'download',
      'per-sample-metrics.tsv',
    )
    expect(mockElement.click).toHaveBeenCalled(1)
    expect(document.body.appendChild).toHaveBeenCalled(1)
    expect(document.body.appendChild).toHaveBeenNthCalledWith(1, mockElement)
    expect(document.body.removeChild).toHaveBeenCalled(1)
    expect(document.body.removeChild).toHaveBeenNthCalledWith(1, mockElement)
  })

  test('test download relatedness clicked', () => {
    const wrapper = makeWrapper(casesQcStoreData)

    const mockElement = vi.fn()
    mockElement.setAttribute = vi.fn()
    mockElement.style = {}
    mockElement.click = vi.fn()
    vi.spyOn(document, 'createElement').mockImplementation(vi.fn())
    document.createElement.mockReturnValueOnce(mockElement)
    vi.spyOn(document.body, 'appendChild').mockImplementation(vi.fn())
    vi.spyOn(document.body, 'removeChild').mockImplementation(vi.fn())

    expect(wrapper.findAll('.download-relatedness').length).toBe(1)
    wrapper.findAll('.download-relatedness')[0].wrapperElement.click()

    expect(document.createElement).toHaveBeenCalled(1)
    expect(document.createElement).toHaveBeenNthCalledWith(1, 'a')
    expect(mockElement.setAttribute).toHaveBeenCalled(2)
    expect(mockElement.setAttribute).toHaveBeenNthCalledWith(
      1,
      'href',
      expect.stringMatching(/^data:application\/octet-stream;base64,/),
    )
    expect(mockElement.setAttribute).toHaveBeenNthCalledWith(
      2,
      'download',
      'relatedness.tsv',
    )
    expect(mockElement.click).toHaveBeenCalled(1)
    expect(document.body.appendChild).toHaveBeenCalled(1)
    expect(document.body.appendChild).toHaveBeenNthCalledWith(1, mockElement)
    expect(document.body.removeChild).toHaveBeenCalled(1)
    expect(document.body.removeChild).toHaveBeenNthCalledWith(1, mockElement)
  })
})

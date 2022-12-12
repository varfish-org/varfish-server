import FilterFormGenesRegionsPane from '@variants/components/FilterFormGenesRegionsPane.vue'
import { mount } from '@vue/test-utils'
import debounce from 'lodash.debounce'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'
import { reactive } from 'vue'

import lookupGeneResponse from '../../data/lookup-gene-response.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()
vi.mock('lodash.debounce')

describe('FilterFormGenesRegionsPane.vue', () => {
  beforeEach(() => {
    // replace debouncing by identity for tests
    debounce.mockImplementation((func) => func)
    fetch.resetMocks()
    fetchMock.doMock()
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  test('genes region', async () => {
    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: false,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: [],
          gene_allowlist: [],
          genomic_region: ['chr1', 'chrX:1,000,000-2,000,000'],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('genomic_region')

    expect(
      wrapper.get('#genomic-region-section').attributes('style')
    ).toBeUndefined()
    expect(wrapper.get('#gene-allowlist-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(wrapper.get('#gene-blocklist-section').attributes('style')).toBe(
      'display: none;'
    )
  })

  test('genes region with invalid regions', async () => {
    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: false,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: ['TGDS'],
          gene_allowlist: ['TGDS'],
          genomic_region: ['chr1', 'chrX:1,000,000-2,000,000', 'invalid'],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('genomic_region')

    expect(wrapper.get('textarea').element.value).toEqual(
      'chr1 chrX:1,000,000-2,000,000 invalid'
    )
  })

  test('genes allow list with help', async () => {
    fetch.mockResponses([
      JSON.stringify(lookupGeneResponse[0]),
      JSON.stringify(lookupGeneResponse[1]),
    ])

    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: true,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: [],
          gene_allowlist: ['TGDS', 'TTN'],
          genomic_region: [],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('gene_allowlist')

    expect(wrapper.get('#genomic-region-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(
      wrapper.get('#gene-allowlist-section').attributes('style')
    ).toBeUndefined()
    expect(wrapper.get('#gene-blocklist-section').attributes('style')).toBe(
      'display: none;'
    )

    expect(fetch.mock.calls.length).toEqual(2)
    expect(fetch.mock.calls[0]).toEqual([
      `/geneinfo/api/lookup-gene/?query=TGDS`,
      {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': undefined,
      },
    ])

    expect(fetch.mock.calls[1]).toEqual([
      `/geneinfo/api/lookup-gene/?query=TTN`,
      {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': undefined,
      },
    ])
  })

  test('genes allow list 404', async () => {
    fetch.mockResponseOnce(JSON.stringify(lookupGeneResponse[2]), {
      status: 404,
    })

    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: true,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: [],
          gene_allowlist: ['NONEXISTENT'],
          genomic_region: [],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('gene_allowlist')

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/geneinfo/api/lookup-gene/?query=NONEXISTENT`,
      {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': undefined,
      },
    ])
  })

  test('genes region block list and help', async () => {
    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: true,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: ['TGDS', 'TTN'],
          gene_allowlist: [],
          genomic_region: [],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('gene_blocklist')

    expect(wrapper.get('#genomic-region-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(wrapper.get('#gene-allowlist-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(
      wrapper.get('#gene-blocklist-section').attributes('style')
    ).toBeUndefined()
    expect(wrapper.get('code').exists()).toBe(true)
  })

  test('genes  list and help', async () => {
    const wrapper = mount(FilterFormGenesRegionsPane, {
      props: {
        showFiltrationInlineHelp: true,
        filtrationComplexityMode: 'dev',
        querySettings: reactive({
          gene_blocklist: ['TGDS', 'TTN'],
          gene_allowlist: [],
          genomic_region: [],
        }),
      },
    })

    const selector = wrapper.get('#gene-regions-list-type')

    await selector.setValue('gene_blocklist')

    expect(wrapper.get('#genomic-region-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(wrapper.get('#gene-allowlist-section').attributes('style')).toBe(
      'display: none;'
    )
    expect(
      wrapper.get('#gene-blocklist-section').attributes('style')
    ).toBeUndefined()
    expect(wrapper.get('code').exists()).toBe(true)
  })
})

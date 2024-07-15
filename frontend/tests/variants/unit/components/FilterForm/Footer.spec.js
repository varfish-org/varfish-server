import { createTestingPinia } from '@pinia/testing'
import FilterFormFooter from '@/variants/components/FilterForm/Footer.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import variantQueryStore from '../../../data/filter-query-store.json'

const piniaTestStore = createTestingPinia({
  initialState: {
    filterQuery: variantQueryStore,
  },
  createSpy: vi.fn,
})

describe('FilterFormFooter.vue', () => {
  test('footer database refseq', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.get('#id_database_selector_refseq').element.checked).toBe(
      true,
    )
    expect(wrapper.get('#id_database_selector_ensembl').element.checked).toBe(
      false,
    )
  })

  test('footer database ensembl', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'initial',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.get('#id_database_selector_refseq').element.checked).toBe(
      false,
    )
    expect(wrapper.get('#id_database_selector_ensembl').element.checked).toBe(
      true,
    )
  })

  test('footer database switch ensembl to refseq', async () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'initial',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const radioRefseq = wrapper.get('#id_database_selector_refseq')
    // let radioEnsembl = wrapper.get('#id_database_selector_ensembl')

    await radioRefseq.setValue()

    expect(radioRefseq.element.checked).toBe(true)
    // expect(radioEnsembl.element.checked).toBe(false)  // BUG in happy-dom?: radio-based flipping not working TODO
    // Test also for what is emitted
    expect(wrapper.emitted()['update:database'][0][0]).toBe('refseq')
  })

  test('footer database switch refseq to ensembl', async () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    // const radioRefseq = wrapper.get('#id_database_selector_refseq')
    const radioEnsembl = wrapper.get('#id_database_selector_ensembl')

    await radioEnsembl.setValue()

    // expect(radioRefseq.element.checked).toBe(false)  // BUG in happy-dom?: radio-based flipping not working TODO
    expect(radioEnsembl.element.checked).toBe(true)
    // Test also for what is emitted
    expect(wrapper.emitted()['update:database'][0][0]).toBe('ensembl')
  })

  test('footer state running', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'running',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.spin').exists()).toBe(true)
  })

  test('footer state finished', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'finished',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.spin').exists()).toBe(false)
  })

  test('footer state loading-results', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'loading-results',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })
    expect(wrapper.find('.spin').exists()).toBe(true)
  })

  test('footer state results-loaded', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'results-loaded',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.spin').exists()).toBe(false)
  })

  test('footer state job-cancelled', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'job-cancelled',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.spin').exists()).toBe(false)
  })

  test('footer state error', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'error',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.spin').exists()).toBe(false)
  })

  test('footer button click submit', async () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'initial',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    await wrapper.get('#submitFilter').trigger('click')

    expect(wrapper.emitted().submitCancelButtonClick).toBeTruthy()
  })

  test('footer filtration complexity mode dev', async () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'ensembl',
        queryState: 'initial',
        filtrationComplexityMode: 'dev',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('code').exists()).toBe(true)
  })
})

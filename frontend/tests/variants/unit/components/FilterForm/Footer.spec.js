import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import FilterFormFooter from '@/variants/components/FilterForm/Footer.vue'

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

  test('hasAnyChanges prop shows change indicator button', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.change-indicator').exists()).toBe(true)
    expect(wrapper.find('[data-target="#changesModal"]').exists()).toBe(true)
  })

  test('hasAnyChanges prop false hides change indicator', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: false,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.change-indicator').exists()).toBe(false)
    expect(wrapper.find('[data-target="#changesModal"]').exists()).toBe(false)
  })

  test('changes modal structure exists', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('#changesModal').exists()).toBe(true)
    expect(wrapper.find('#changesModalLabel').text()).toBe('Changed Settings')
    expect(wrapper.find('[data-dismiss="modal"]').exists()).toBe(true)
  })

  test('getChanges computed returns empty array when no settings exist', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: null,
          lastSubmittedQuerySettings: null,
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes).toEqual([])
  })

  test('getChanges computed detects string value changes', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'ensembl',
            recessive_mode: 'compound-recessive',
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
            recessive_mode: 'compound-recessive',
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(1)
    expect(changes[0].field).toBe('database')
    expect(changes[0].previous).toBe('refseq')
    expect(changes[0].current).toBe('ensembl')
  })

  test('getChanges computed detects boolean value changes', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            require_in_clinvar: true,
          },
          lastSubmittedQuerySettings: {
            require_in_clinvar: false,
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(1)
    expect(changes[0].field).toBe('require_in_clinvar')
    expect(changes[0].previous).toBe('false')
    expect(changes[0].current).toBe('true')
  })

  test('getChanges computed detects null/undefined changes', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            gnomad_exomes_frequency: null,
            gnomad_genomes_frequency: 0.01,
          },
          lastSubmittedQuerySettings: {
            gnomad_exomes_frequency: 0.002,
            gnomad_genomes_frequency: null,
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(2)
    const gnomadExomesFreqChange = changes.find(
      (c) => c.field === 'gnomad_exomes_frequency',
    )
    expect(gnomadExomesFreqChange.previous).toBe('0.002')
    expect(gnomadExomesFreqChange.current).toBe('null')
    const gnomadGenomesFreqChange = changes.find(
      (c) => c.field === 'gnomad_genomes_frequency',
    )
    expect(gnomadGenomesFreqChange.previous).toBe('null')
    expect(gnomadGenomesFreqChange.current).toBe('0.01')
  })

  test('getChanges computed detects object changes', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            genotype: { 'NA12878-N1-DNA1-WES1': 'het' },
          },
          lastSubmittedQuerySettings: {
            genotype: { 'NA12878-N1-DNA1-WES1': 'hom' },
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(1)
    expect(changes[0].field).toBe('genotype')
    expect(changes[0].previous).toContain('NA12878-N1-DNA1-WES1')
    expect(changes[0].previous).toContain('hom')
    expect(changes[0].current).toContain('het')
  })

  test('getChanges computed detects multiple changes', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'ensembl',
            var_type_snv: true,
            gnomad_exomes_frequency: 0.01,
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
            var_type_snv: false,
            gnomad_exomes_frequency: 0.002,
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(3)
    expect(changes.map((c) => c.field)).toContain('database')
    expect(changes.map((c) => c.field)).toContain('var_type_snv')
    expect(changes.map((c) => c.field)).toContain('gnomad_exomes_frequency')
  })

  test('getChanges computed returns empty array when settings are identical', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'refseq',
            var_type_mnv: true,
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
            var_type_mnv: true,
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: false,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const changes = wrapper.vm.getChanges
    expect(changes.length).toBe(0)
  })

  test('restorePreviousSettings restores lastSubmittedQuerySettings', async () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'ensembl',
            var_type_indel: false,
            gnomad_genomes_frequency: 0.01,
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
            var_type_indel: true,
            gnomad_genomes_frequency: 0.002,
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const variantQueryStore = wrapper.vm.variantQueryStore

    wrapper.vm.restorePreviousSettings()

    expect(variantQueryStore.querySettings.database).toBe('refseq')
    expect(variantQueryStore.querySettings.var_type_indel).toBe(true)
    expect(variantQueryStore.querySettings.gnomad_genomes_frequency).toBe(0.002)
  })

  test('modal displays no changes message when changes array is empty', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'refseq',
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: false,
      },
      global: {
        plugins: [testPinia],
      },
    })

    expect(wrapper.find('.alert-info').exists()).toBe(true)
    expect(wrapper.find('.alert-info').text()).toContain('No changes detected')
  })

  test('modal displays changes table when changes exist', () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'ensembl',
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    expect(wrapper.find('.table').exists()).toBe(true)
    expect(wrapper.findAll('tbody tr').length).toBe(1)
  })

  test('restore button exists in modal footer', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const restoreButton = wrapper.find('.modal-footer .btn-info')
    expect(restoreButton.exists()).toBe(true)
    expect(restoreButton.text()).toContain('Restore Previous')
  })

  test('restore button triggers restorePreviousSettings', async () => {
    const testPinia = createTestingPinia({
      initialState: {
        variantQuery: {
          querySettings: {
            database: 'ensembl',
          },
          lastSubmittedQuerySettings: {
            database: 'refseq',
          },
        },
      },
      createSpy: vi.fn,
    })

    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [testPinia],
      },
    })

    const restoreButton = wrapper.find('.modal-footer .btn-info')
    await restoreButton.trigger('click')

    const variantQueryStore = wrapper.vm.variantQueryStore
    expect(variantQueryStore.querySettings.database).toBe('refseq')
  })

  test('change indicator tooltip exists', () => {
    const wrapper = shallowMount(FilterFormFooter, {
      props: {
        database: 'refseq',
        queryState: 'initial',
        hasAnyChanges: true,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.find('.tooltip-text').exists()).toBe(true)
    expect(wrapper.find('.tooltip-text').text()).toContain(
      'Settings modified after query submitted',
    )
  })
})

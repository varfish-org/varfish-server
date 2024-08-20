import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import FilterFormPrioritizationPane from '@/variants/components/FilterForm/PrioritizationPane.vue'

describe('FilterFormPrioritizationPane.vue', () => {
  test('prioritization prefilled', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        prioEnabled: true,
        prioAlgorithm: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        pathoEnabled: true,
        pathoScore: 'cadd',
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const pathoScore = wrapper.get('#patho-score')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(pathoEnabled.element.checked).toBe(true)
    expect(pathoScore.element.value).toBe('cadd')
    expect(prioEnabled.element.checked).toBe(true)
    expect(prioAlgorithm.element.value).toBe('hiphive-human')
  })

  test('prioritization prefilled change values', async () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        pathoEnabled: true,
        pathoScore: 'cadd',
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')

    await pathoEnabled.setValue(false)
    await prioEnabled.setValue(false)
    await prioAlgorithm.setValue('phenix')

    expect(pathoEnabled.element.checked).toBe(false)
    expect(prioEnabled.element.checked).toBe(false)
    expect(prioAlgorithm.element.value).toBe('phenix')
  })

  test('prioritization prefilled with help', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: true,
        exomiserEnabled: true,
        caddEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        pathoEnabled: true,
        pathoScore: 'cadd',
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(2)
  })

  test('prioritization prefilled with warning', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        pathoEnabled: true,
        pathoScore: 'cadd',
      },
    })

    expect(wrapper.findAll('.alert-warning').length).toBe(1)
  })

  test('prioritization empty', () => {
    shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: false,
        caddEnabled: false,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: [],
        pathoEnabled: false,
      },
    })

    // TODO [TEST_STUB]
  })
})

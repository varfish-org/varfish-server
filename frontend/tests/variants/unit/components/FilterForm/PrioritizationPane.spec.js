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
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorithm: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        gmEnabled: true,
        pediaEnabled: true,
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const pathoScore = wrapper.get('#patho-score')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')
    const gmEnabled = wrapper.get('#gm-enabled')
    const pediaEnabled = wrapper.get('#pedia-enabled')

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(pathoEnabled.element.checked).toBe(true)
    expect(pathoScore.element.value).toBe('cadd')
    expect(prioEnabled.element.checked).toBe(true)
    expect(prioAlgorithm.element.value).toBe('hiphive-human')
    expect(gmEnabled.element.checked).toBe(true)
    expect(pediaEnabled.element.checked).toBe(true)
  })

  test('prioritization prefilled change values', async () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        gmEnabled: true,
        pediaEnabled: true,
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')
    const gmEnabled = wrapper.get('#gm-enabled')
    const pediaEnabled = wrapper.get('#pedia-enabled')

    await pathoEnabled.setValue(false)
    await prioEnabled.setValue(false)
    await prioAlgorithm.setValue('phenix')
    await gmEnabled.setValue(false)
    await pediaEnabled.setValue(false)

    expect(pathoEnabled.element.checked).toBe(false)
    expect(prioEnabled.element.checked).toBe(false)
    expect(prioAlgorithm.element.value).toBe('phenix')
    expect(gmEnabled.element.checked).toBe(false)
    expect(pediaEnabled.element.checked).toBe(false)
  })

  test('prioritization prefilled enable pedia value', async () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: '',
        pathoEnabled: false,
        pathoScore: 'cadd',
        gmEnabled: false,
        pediaEnabled: false,
      },
    })

    const pediaEnabled = wrapper.get('#pedia-enabled')

    pediaEnabled.element.checked = true
    await pediaEnabled.trigger('click')
    await pediaEnabled.trigger('change')
    await pediaEnabled.setChecked()

    expect(pediaEnabled.element.checked).toBe(true)
  })

  test('prioritization prefilled with help', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: true,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        gmEnabled: true,
        pediaEnabled: true,
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(3)
  })

  test('prioritization prefilled with photo file path', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: true,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: 'C://fake-path',
        pathoEnabled: true,
        pathoScore: 'cadd',
        gmEnabled: true,
        pediaEnabled: true,
      },
    })

    expect(wrapper.props('photoFile')).toBe('C://fake-path')
  })

  test('prioritization prefilled with warning', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioGm: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        gmEnabled: true,
        pediaEnabled: true,
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
        cadaEnabled: false,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: [],
        prioGm: '',
        photoFile: '',
        pathoEnabled: false,
        gmEnabled: false,
        pediaEnabled: false,
      },
    })

    // TODO [TEST_STUB]
  })
})

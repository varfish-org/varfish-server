import FilterFormPrioritizationPane from '@variants/components/FilterForm/PrioritizationPane.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('FilterFormPrioritizationPane.vue', () => {
  test('prioritization prefilled', () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorithm: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioFace: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        faceEnabled: true,
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const pathoScore = wrapper.get('#patho-score')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')
    const faceEnabled = wrapper.get('#face-enabled')

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(pathoEnabled.element.checked).toBe(true)
    expect(pathoScore.element.value).toBe('cadd')
    expect(prioEnabled.element.checked).toBe(true)
    expect(prioAlgorithm.element.value).toBe('hiphive-human')
    expect(faceEnabled.element.checked).toBe(true)
  })

  test('prioritization prefilled change values', async () => {
    const wrapper = shallowMount(FilterFormPrioritizationPane, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: false,
        exomiserEnabled: true,
        caddEnabled: true,
        cadaEnabled: true,
        prioEnabled: true,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: ['HP:0000245'],
        prioFace: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        faceEnabled: true,
      },
    })

    const pathoEnabled = wrapper.get('#patho-enabled')
    const prioEnabled = wrapper.get('#prio-enabled')
    const prioAlgorithm = wrapper.get('#prio-algorithm')
    const faceEnabled = wrapper.get('#face-enabled')

    await pathoEnabled.setValue(false)
    await prioEnabled.setValue(false)
    await prioAlgorithm.setValue('phenix')
    await faceEnabled.setValue(false)

    expect(pathoEnabled.element.checked).toBe(false)
    expect(prioEnabled.element.checked).toBe(false)
    expect(prioAlgorithm.element.value).toBe('phenix')
    expect(faceEnabled.element.checked).toBe(false)
  })

  test('prioritization prefilled with help', () => {
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
        prioFace: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        faceEnabled: true,
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(2)
  })

  test('prioritization prefilled with warning', () => {
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
        prioFace: '',
        photoFile: '',
        pathoEnabled: true,
        pathoScore: 'cadd',
        faceEnabled: true,
      },
    })

    expect(wrapper.findAll('.alert-warning').length).toBe(1)
  })

  test('prioritization empty', () => {
    shallowMount(FilterFormPrioritizationPane, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: false,
        exomiserEnabled: false,
        caddEnabled: false,
        cadaEnabled: false,
        prioEnabled: false,
        prioAlgorith: 'hiphive-human',
        prioHpoTerms: [],
        prioFace: '',
        photoFile: '',
        pathoEnabled: false,
        faceEnabled: false,
      },
    })

    // TODO [TEST_STUB]
  })
})

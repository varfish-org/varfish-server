import FilterFormFrequencyPane from '@variants/components/FilterForm/FrequencyPane.vue'
import { shallowMount } from '@vue/test-utils'
import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import singletonCaseData from '../../../data/case-singleton.json'
import querySettingsSingleton from '../../../data/query-settings-singleton.json'

describe('FilterFormFrequencyPane.vue', () => {
  test('frequency with GRCh38', () => {
    const wrapper = mount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: true,
        case: { ...singletonCaseData, release: 'GRCh38' },
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')
    const rows = wrapper.findAll('tr')

    expect(wrapper.find('#warning-text-grch38').exists()).toBeTruthy()
    expect(rows.length).toBe(9)
    expect(inputs.length).toBe(40)

    // Bug in vue-testUtils? This should technically work but seems to be a bug in vue test utils.
    // expect(rows[1].isVisible()).toBe(false)
    // expect(rows[2].isVisible()).toBe(false)
    expect(rows[1].attributes('style')).toBe('display: none;')
    expect(rows[2].attributes('style')).toBe('display: none;')
  })

  test('frequency defaults with help', () => {
    const wrapper = mount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: true,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    expect(wrapper.find('#warning-text-grch38').exists()).toBeFalsy()
    expect(inputs.length).toBe(40)
    expect(wrapper.findAll('.alert-secondary').length).toBe(1)

    // Check defaults of checkboxes
    expect(inputs[0].element.checked).toBeTruthy()
    expect(inputs[5].element.checked).toBeTruthy()
    expect(inputs[10].element.checked).toBeTruthy()
    expect(inputs[15].element.checked).toBeTruthy()
    expect(inputs[20].element.checked).toBeTruthy()
    expect(inputs[25].element.checked).toBeTruthy()
    expect(inputs[30].element.checked).toBeTruthy()
    expect(inputs[35].element.checked).toBeFalsy()

    // Check homozygous count
    expect(inputs[1].element.value).toBe('0')
    expect(inputs[6].element.value).toBe('0')
    expect(inputs[11].element.value).toBe('0')
    expect(inputs[16].element.value).toBe('0')
    expect(inputs[21].element.value).toBe('')
    expect(inputs[26].element.value).toBe('10')
    expect(inputs[31].element.value).toBe('200')
    expect(inputs[36].element.value).toBe('')

    // Check heterozygous count
    expect(inputs[2].element.value).toBe('4')
    expect(inputs[7].element.value).toBe('10')
    expect(inputs[12].element.value).toBe('20')
    expect(inputs[17].element.value).toBe('4')
    expect(inputs[22].element.value).toBe('')
    expect(inputs[27].element.disabled).toBeTruthy()
    expect(inputs[32].element.value).toBe('')
    expect(inputs[37].element.disabled).toBeTruthy()

    // Check hemizygous count
    expect(inputs[3].element.value).toBe('')
    expect(inputs[8].element.value).toBe('')
    expect(inputs[13].element.value).toBe('')
    expect(inputs[18].element.value).toBe('')
    expect(inputs[23].element.value).toBe('')
    expect(inputs[28].element.disabled).toBeTruthy()
    expect(inputs[33].element.disabled).toBeTruthy()
    expect(inputs[38].element.disabled).toBeTruthy()

    // Check frequency
    expect(inputs[4].element.value).toBe('0.002')
    expect(inputs[9].element.value).toBe('0.002')
    expect(inputs[14].element.value).toBe('0.002')
    expect(inputs[19].element.value).toBe('0.002')
    expect(inputs[24].element.value).toBe('20')
    expect(inputs[29].element.value).toBe('0.01')
    expect(inputs[34].element.value).toBe('0.01')
    expect(inputs[39].element.value).toBe('')
  })

  test('frequency change checkboxes', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    // Change defaults of checkboxes
    await inputs[0].setValue(false)
    await inputs[5].setValue(false)
    await inputs[10].setValue(false)
    await inputs[15].setValue(false)
    await inputs[20].setValue(false)
    await inputs[25].setValue(false)
    await inputs[30].setValue(false)
    await inputs[35].setValue()

    expect(inputs[0].element.checked).toBeFalsy()
    expect(inputs[5].element.checked).toBeFalsy()
    expect(inputs[10].element.checked).toBeFalsy()
    expect(inputs[15].element.checked).toBeFalsy()
    expect(inputs[20].element.checked).toBeFalsy()
    expect(inputs[25].element.checked).toBeFalsy()
    expect(inputs[30].element.checked).toBeFalsy()
    expect(inputs[35].element.checked).toBeTruthy()
  })

  test('frequency change homozygous count', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    await inputs[1].setValue(123)
    await inputs[6].setValue(123)
    await inputs[11].setValue(123)
    await inputs[16].setValue(123)
    await inputs[21].setValue(123)
    await inputs[26].setValue(123)
    await inputs[31].setValue(123)
    await inputs[36].setValue(123)

    expect(inputs[1].element.value).toBe('123')
    expect(inputs[6].element.value).toBe('123')
    expect(inputs[11].element.value).toBe('123')
    expect(inputs[16].element.value).toBe('123')
    expect(inputs[21].element.value).toBe('123')
    expect(inputs[26].element.value).toBe('123')
    expect(inputs[31].element.value).toBe('123')
    expect(inputs[36].element.value).toBe('123')
  })

  test('frequency change heterozygous count', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    await inputs[2].setValue(123)
    await inputs[7].setValue(123)
    await inputs[12].setValue(123)
    await inputs[17].setValue(123)
    await inputs[22].setValue(123)
    await inputs[32].setValue(123)

    expect(inputs[2].element.value).toBe('123')
    expect(inputs[7].element.value).toBe('123')
    expect(inputs[12].element.value).toBe('123')
    expect(inputs[17].element.value).toBe('123')
    expect(inputs[22].element.value).toBe('123')
    expect(inputs[32].element.value).toBe('123')
  })

  test('frequency change hemizygous count', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    await inputs[3].setValue(123)
    await inputs[8].setValue(123)
    await inputs[13].setValue(123)
    await inputs[18].setValue(123)
    await inputs[23].setValue(123)

    expect(inputs[3].element.value).toBe('123')
    expect(inputs[8].element.value).toBe('123')
    expect(inputs[13].element.value).toBe('123')
    expect(inputs[18].element.value).toBe('123')
    expect(inputs[23].element.value).toBe('123')
  })

  test('frequency change frequency', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    const inputs = wrapper.findAll('input')

    await inputs[4].setValue(123)
    await inputs[9].setValue(123)
    await inputs[14].setValue(123)
    await inputs[19].setValue(123)
    await inputs[24].setValue(123)
    await inputs[29].setValue(123)
    await inputs[34].setValue(123)
    await inputs[39].setValue(123)

    expect(inputs[4].element.value).toBe('123')
    expect(inputs[9].element.value).toBe('123')
    expect(inputs[14].element.value).toBe('123')
    expect(inputs[19].element.value).toBe('123')
    expect(inputs[24].element.value).toBe('123')
    expect(inputs[29].element.value).toBe('123')
    expect(inputs[34].element.value).toBe('123')
    expect(inputs[39].element.value).toBe('123')
  })

  test('frequency dev mode', async () => {
    const wrapper = shallowMount(FilterFormFrequencyPane, {
      props: {
        showFiltrationInlineHelp: false,
        filtrationComplexityMode: 'dev',
        case: singletonCaseData,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.get('code').text()).toMatch(/\{"thousand.+/)
  })
})

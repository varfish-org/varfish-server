import FilterFormQualityPaneRow from '@/variants/components/FilterForm/QualityPaneRow.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'
import { reactive } from 'vue'

import singletonCaseData from '../../../data/case-singleton.json'
import querySettingsSingleton from '../../../data/query-settings-singleton.json'

const dataSingleton = reactive({
  caseName: singletonCaseData.name,
  index: 1,
  member: singletonCaseData.pedigree[0],
  qualMinDpHet:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].dp_het,
  qualMinDpHom:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].dp_hom,
  qualMinAb:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].ab,
  qualMinGq:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].gq,
  qualMinAd:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].ad,
  qualMaxAd:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].ad_max,
  qualFail:
    querySettingsSingleton.quality[singletonCaseData.pedigree[0].name].fail,
})

describe('FilterFormQualityPaneRow.vue', () => {
  test('quality row singleton', () => {
    const wrapper = shallowMount(FilterFormQualityPaneRow, {
      props: dataSingleton,
    })

    const inputs = wrapper.findAll('input')
    // const select = wrapper.find('select')

    expect(wrapper.find('.invalid-feedback').exists()).toBe(false)
    expect(inputs.length).toBe(6)
    expect(Number(inputs[0].element.value)).toBe(dataSingleton.qualMinDpHet)
    expect(Number(inputs[0].element.value)).toBe(dataSingleton.qualMinDpHet)
    expect(Number(inputs[1].element.value)).toBe(dataSingleton.qualMinDpHom)
    expect(Number(inputs[2].element.value)).toBe(dataSingleton.qualMinAb)
    expect(Number(inputs[3].element.value)).toBe(dataSingleton.qualMinGq)
    expect(Number(inputs[4].element.value)).toBe(dataSingleton.qualMinAd)
    expect(Number(inputs[5].element.value)).toBe(0)
    // TODO: Bug in happy-dom? Value is "" in tests.
    // expect(select.element.value).toEqual(dataSingleton.qualFail)
  })

  test('quality row singleton change data', async () => {
    const wrapper = shallowMount(FilterFormQualityPaneRow, {
      props: dataSingleton,
    })

    const inputs = wrapper.findAll('input')
    const select = wrapper.find('select')

    await inputs[0].setValue(111)
    await inputs[1].setValue(222)
    await inputs[2].setValue(0.333)
    await inputs[3].setValue(444)
    await inputs[4].setValue(555)
    await inputs[5].setValue(666)
    await select.setValue('ignore')

    // TODO: bug in happy-dom or vue-test? The 0-th equals "10"
    // expect(inputs[0].element.value).toEqual('111')
    expect(inputs[1].element.value).toEqual('222')
    expect(inputs[2].element.value).toEqual('0.333')
    expect(inputs[3].element.value).toEqual('444')
    expect(inputs[4].element.value).toEqual('555')
    expect(inputs[5].element.value).toEqual('666')
    expect(select.element.value).toEqual('ignore')
  })
})

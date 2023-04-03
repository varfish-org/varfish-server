import FilterFormQualityPane from '@variants/components/FilterFormQualityPane.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'
import { reactive } from 'vue'

import singletonCaseData from '../../data/case-singleton.json'
import trioCaseData from '../../data/case-trio.json'
import querySettingsSingleton from '../../data/query-settings-singleton.json'
import querySettingsTrio from '../../data/query-settings-trio.json'

describe('FilterFormQualityPane.vue', () => {
  test('quality singleton with help', () => {
    const wrapper = shallowMount(FilterFormQualityPane, {
      props: {
        filtrationComplexityMode: 'simple',
        showFiltrationInlineHelp: true,
        caseObj: singletonCaseData,
        querySettings: reactive(querySettingsSingleton),
      },
    })
    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
    expect(wrapper.findAll('filter-form-quality-pane-row-stub').length).toBe(1)
  })

  test('quality trio', () => {
    const wrapper = shallowMount(FilterFormQualityPane, {
      props: {
        filtrationComplexityMode: 'simple',
        showFiltrationInlineHelp: false,
        caseObj: trioCaseData,
        querySettings: reactive(querySettingsTrio),
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)
    expect(wrapper.findAll('filter-form-quality-pane-row-stub').length).toBe(3)
  })
})

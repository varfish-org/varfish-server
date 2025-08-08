import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'
import { reactive } from 'vue'

import FilterFormGenotypePane from '@/variants/components/FilterForm/GenotypePane.vue'

import singletonCaseData from '../../../data/case-singleton.json'
import trioCaseData from '../../../data/case-trio.json'
import querySettingsSingleton from '../../../data/query-settings-singleton.json'
import querySettingsTrio from '../../../data/query-settings-trio.json'

describe('FilterFormGenotypePane.vue', () => {
  test('genotype trio', async () => {
    const wrapper = shallowMount(FilterFormGenotypePane, {
      props: {
        showFiltrationInlineHelp: false,
        case: trioCaseData,
        querySettings: reactive(querySettingsTrio),
        useOptgroup: false,
      },
    })

    const selects = wrapper.findAll('select')

    expect(selects.length).toBe(3)

    // TODO [TEST_STUB]
    await selects[0].setValue('hom')
  })

  test('genotype trio with help', () => {
    const wrapper = shallowMount(FilterFormGenotypePane, {
      props: {
        showFiltrationInlineHelp: true,
        case: trioCaseData,
        querySettings: reactive(querySettingsTrio),
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
  })

  test('genotype singleton', async () => {
    const wrapper = shallowMount(FilterFormGenotypePane, {
      props: {
        showFiltrationInlineHelp: false,
        case: singletonCaseData,
        querySettings: reactive(querySettingsSingleton),
      },
    })

    const selects = wrapper.findAll('select')

    expect(selects.length).toBe(1)
  })
})

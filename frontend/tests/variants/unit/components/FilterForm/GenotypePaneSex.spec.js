import FilterFormGenotypePaneSex from '@variants/components/FilterForm/GenotypePaneSex.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('FilterFormGenotypePaneSex.vue', () => {
  test('genotype sex male', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneSex, {
      props: {
        sex: 1,
      },
    })

    expect(wrapper.find('#sex-male-icon').exists()).toBe(true)
  })

  test('genotype sex female', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneSex, {
      props: {
        sex: 2,
      },
    })

    expect(wrapper.find('#sex-female-icon').exists()).toBe(true)
  })

  test('genotype sex unknown', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneSex, {
      props: {
        sex: 0,
      },
    })

    expect(wrapper.find('#sex-unknown-icon').exists()).toBe(true)
  })
})

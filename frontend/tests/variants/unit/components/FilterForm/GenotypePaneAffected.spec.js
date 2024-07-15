import FilterFormGenotypePaneAffected from '@/variants/components/FilterForm/GenotypePaneAffected.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('FilterFormGenotypePaneAffected.vue', () => {
  test('genotype affected', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneAffected, {
      props: {
        affected: 2,
      },
    })

    expect(wrapper.find('#affected-icon').exists()).toBe(true)
  })

  test('genotype unaffected', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneAffected, {
      props: {
        affected: 1,
      },
    })

    expect(wrapper.find('#unaffected-icon').exists()).toBe(true)
  })

  test('genotype unknown', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneAffected, {
      props: {
        affected: 0,
      },
    })

    expect(wrapper.find('#unknown-icon').exists()).toBe(true)
  })
})

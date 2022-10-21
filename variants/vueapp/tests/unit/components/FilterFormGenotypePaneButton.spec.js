import FilterFormGenotypePaneButton from '@variants/components/FilterFormGenotypePaneButton.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('FilterFormGenotypePaneButton.vue', () => {
  test('genotype button', () => {
    const wrapper = shallowMount(FilterFormGenotypePaneButton, {})

    expect(wrapper.find('button').exists()).toBe(true)
  })

  // TODO [TEST_STUB]
})

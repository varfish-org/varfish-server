import VariantDetailsVariantValidator from '@variants/components/VariantDetails/VariantValidator.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import { reactive } from 'vue'

import variantValidatorResultsData from '../../../data/variant-validator.json'
import trioVariantsData from '../../../data/variants-trio.json'

global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(variantValidatorResultsData),
  })
)

describe('VariantDetailsVariantValidator.vue', () => {
  test('initial', () => {
    const wrapper = shallowMount(VariantDetailsVariantValidator, {
      props: {
        smallVariant: trioVariantsData[0],
        variantValidatorState: 0,
        variantValidatorResults: null,
      },
    })

    expect(wrapper.find('.alert-secondary').exists()).toBe(true)
  })

  test('running', () => {
    const wrapper = shallowMount(VariantDetailsVariantValidator, {
      props: {
        smallVariant: trioVariantsData[0],
        variantValidatorState: 1,
        variantValidatorResults: null,
      },
    })

    expect(wrapper.find('.alert-info').exists()).toBe(true)
    expect(wrapper.find('fa-solid-circle-notch-stub').exists()).toBe(true)
    expect(wrapper.find('fa-solid-circle-notch-stub').classes('spin')).toBe(
      true
    )
  })

  test('done', () => {
    const wrapper = shallowMount(VariantDetailsVariantValidator, {
      props: {
        smallVariant: trioVariantsData[0],
        variantValidatorState: 2,
        variantValidatorResults: variantValidatorResultsData,
      },
    })

    expect(wrapper.find('.alert-warning').exists()).toBe(true)
    expect(wrapper.findAll('.nav-item').length).toBe(8)
  })

  test('submit', async () => {
    const props = reactive({
      smallVariant: trioVariantsData[0],
      variantValidatorState: 0,
      variantValidatorResults: null,
    })
    const wrapper = shallowMount(VariantDetailsVariantValidator, {
      props: props,
    })

    await wrapper.get('button').trigger('click')
    // TODO [TEST_STUB]
    // expect(props.variantValidatorState).toBe(1)
  })
})

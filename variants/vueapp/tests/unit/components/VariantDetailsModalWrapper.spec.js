import VariantDetailsModalWrapper from '@variants/components/VariantDetailsModalWrapper.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import trioVariantsData from '../../data/variants-trio.json'

describe('VariantDetailsModalWrapper.vue', () => {
  test('data loading', () => {
    const wrapper = shallowMount(VariantDetailsModalWrapper, {
      props: {
        smallVariant: { ...trioVariantsData[0] },
        fetched: false,
      },
    })

    expect(wrapper.find('fa-solid-circle-notch-stub').exists()).toBe(true)
  })

  test('data loading no variant', () => {
    const wrapper = shallowMount(VariantDetailsModalWrapper, {
      props: {
        smallVariant: null,
        fetched: false,
      },
    })

    expect(wrapper.find('fa-solid-circle-notch-stub').exists()).toBe(true)
  })

  test('calling modal', () => {
    shallowMount(VariantDetailsModalWrapper, {
      props: {
        smallVariant: null,
        fetched: false,
      },
    })

    // TODO [TEST_STUB] jquery not available
    // wrapper.vm.showModal()
  })
})

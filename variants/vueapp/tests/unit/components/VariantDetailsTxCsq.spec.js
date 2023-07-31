import VariantDetailsTxCsq from '@variants/components/VariantDetailsTxCsq.vue'

import brca1Txcsq from '@variantsTest/data/var-brca1-missense-benign-txcsq.json'

import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('VariantDetailsTxCsq.vue', () => {
  test('transcripts all levels', () => {
    const wrapper = shallowMount(VariantDetailsTxCsq, {
      props: {
        txCsq: brca1Txcsq,
      },
    })

    expect(wrapper.findAll('tr').length).toBe(6)
  })

  test('transcripts disabled/empty', () => {
    const wrapper = shallowMount(VariantDetailsTxCsq, {
      props: {
        effectDetails: null,
      },
    })

    expect(wrapper.findAll('tr').length).toBe(1)
  })
})

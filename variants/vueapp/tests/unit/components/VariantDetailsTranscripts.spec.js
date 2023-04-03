import VariantDetailsTranscripts from '@variants/components/VariantDetailsTranscripts.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('VariantDetailsTranscripts.vue', () => {
  test('transcripts all levels', () => {
    const wrapper = shallowMount(VariantDetailsTranscripts, {
      props: {
        effectDetails: [
          {
            transcriptId: 'NM_002222.5',
            variantEffects: ['missense_variant'],
            hgvsNucleotides: 'c.6835C>T',
            hgvsProtein: 'p.(R2279W)',
          },
          {
            transcriptId: 'XM_005265109.1',
            variantEffects: ['stop_lost'],
            hgvsNucleotides: 'c.6955C>T',
            hgvsProtein: 'p.(R2319W)',
          },
          {
            transcriptId: 'XM_005265110.1',
            variantEffects: ['synonymous_variant'],
            hgvsNucleotides: 'c.6956C>T',
            hgvsProtein: 'p.(R2310W)',
          },
        ],
      },
    })

    expect(wrapper.findAll('.badge-warning').length).toBe(1)
    expect(wrapper.findAll('.badge-danger').length).toBe(1)
    expect(wrapper.findAll('.badge-secondary').length).toBe(1)
    expect(wrapper.findAll('tr').length).toBe(4)
  })

  test('transcripts disabled/empty', () => {
    const wrapper = shallowMount(VariantDetailsTranscripts, {
      props: {
        effectDetails: null,
      },
    })

    expect(wrapper.find('p').exists()).toBe(true)
    expect(wrapper.find('table').exists()).toBe(false)
  })
})

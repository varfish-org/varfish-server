import HpoTermInput from '@variants/components/HpoTermInput.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('HpoTermInput.vue', () => {
  test('hpo term input with help', () => {
    const wrapper = shallowMount(HpoTermInput, {
      props: {
        csrfToken: 'fake token',
        showFiltrationInlineHelp: true,
        hpoTerms: ['HP:0000245', 'HP:0000418'],
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
  })
})

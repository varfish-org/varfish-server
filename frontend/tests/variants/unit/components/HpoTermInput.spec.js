import HpoTermInput from '@/variants/components/HpoTermInput.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, beforeEach } from 'vitest'
import { setupUrlConfigForTesting } from '@bihealth/reev-frontend-lib/lib/urlConfig'

describe('HpoTermInput.vue', () => {
  beforeEach(() => {
    setupUrlConfigForTesting()
  })

  test('hpo term input with help', () => {
    const wrapper = shallowMount(HpoTermInput, {
      props: {
        showFiltrationInlineHelp: true,
        hpoTerms: ['HP:0000118'],
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
  })
})

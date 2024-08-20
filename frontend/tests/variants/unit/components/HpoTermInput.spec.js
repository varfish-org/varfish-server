import { setupUrlConfigForTesting } from '@bihealth/reev-frontend-lib/lib/urlConfig'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, test } from 'vitest'

import HpoTermInput from '@/variants/components/HpoTermInput.vue'

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

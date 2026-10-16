import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { nextTick } from 'vue'

import FilterForm from '@/variants/components/FilterForm.vue'

import singletonCaseData from '../../data/case-singleton.json'
import querySettingsSingleton from '../../data/query-settings-singleton.json'

// DevPane imports vue-clipboard3, whose CJS build cannot be loaded by vitest.
vi.mock('@/varfish/components/FilterForm/DevPane.vue', () => ({
  default: {},
}))

const mountFilterForm = (querySettings) =>
  mount(FilterForm, {
    global: {
      plugins: [
        createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            variantQuery: { querySettings },
            caseDetails: { caseObj: singletonCaseData },
          },
        }),
      ],
      stubs: {
        FilterFormQuickPresets: true,
        FilterFormGenotypePane: true,
        FilterFormPriotizationPane: true,
        FilterFormEffectPane: true,
        FilterFormQualityPane: true,
        FilterFormGenesRegionsPane: {
          template: '<div />',
          methods: { isValid: () => true },
        },
        FilterFormFlagsPane: true,
        FilterFormClinvarPane: true,
        Overlay: true,
      },
    },
  })

describe('FilterForm.vue', () => {
  beforeEach(() => {
    // FrequencyPane fetches the in-house database statistics on mount.
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true, json: async () => ({ count: 0 }) }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('filter button is enabled for valid frequencies', async () => {
    const wrapper = mountFilterForm({ ...querySettingsSingleton })
    await nextTick()

    expect(wrapper.get('#submitFilter').element.disabled).toBe(false)
  })

  test('filter button is disabled for a frequency above 0.05', async () => {
    const wrapper = mountFilterForm({
      ...querySettingsSingleton,
      gnomad_exomes_frequency: 0.1,
    })
    await nextTick()

    expect(wrapper.get('#submitFilter').element.disabled).toBe(true)
    expect(wrapper.text()).toContain(
      'You must fix the errors before you can filter.',
    )
  })
})

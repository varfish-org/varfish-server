import casesApi from '@cases/api/cases'
import CaseListPaneCases from '@cases/components/CaseList/PaneCases.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterAll, beforeAll, describe, expect, test, vi } from 'vitest'

import caseListResponse from '../../../data/caseListResponse.json'
import casesState from '../../../data/casesStoreData.json'
import { waitAG, waitRAF } from '../../../helpers'

// Mock out the cases API
vi.mock('@cases/api/cases.js')

const makeWrapper = () => {
  return mount(CaseListPaneCases, {
    global: {
      plugins: [
        createTestingPinia({
          initialState: { cases: casesState },
          createSpy: vi.fn,
        }),
      ],
    },
    shallow: true,
  })
}

describe('CaseListPaneCases.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Set reproducible time
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2020, 3, 1))
  })

  afterAll(() => {
    vi.useRealTimers()
  })

  test('test rendering', async () => {
    casesApi.listCase.mockResolvedValue(caseListResponse)

    const wrapper = makeWrapper()
    await waitAG(wrapper)
    await waitRAF()

    expect(wrapper.findAll('data-table-stub').length).toBe(1)
  })
})

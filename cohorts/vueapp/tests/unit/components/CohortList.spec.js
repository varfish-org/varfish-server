import CohortList from '@cohorts/components/CohortList.vue'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'

import cohortsState from '../../data/cohortsStoreData.json'
import listCohortResponse from '../../data/listCohortResponse.json'

describe('CohortList.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    // Mock out jquery dollar function for showing modals.
    const valResult = vi.fn()
    valResult.change = vi.fn()
    const mockJQueryResult = vi.fn()
    mockJQueryResult.prop = vi.fn()
    mockJQueryResult.val = vi.fn()
    mockJQueryResult.val.mockReturnValue(valResult)
    mockJQueryResult.change = vi.fn()
    const mockJQuery = vi.fn(function () {
      return this
    })
    mockJQuery.mockReturnValue(mockJQueryResult)
    global.$ = mockJQuery
  })

  test('check initialization', async () => {
    const wrapper = shallowMount(CohortList, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              cohorts: {
                storeState: cohortsState.storeState,
                cohortCount: listCohortResponse.count,
                tableRows: listCohortResponse.results,
                project: cohortsState.project,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
    })

    expect(wrapper.html()).matches(/<cohort-list-header-stub>/)
    expect(wrapper.html()).matches(/<cohort-list-table-stub>/)
    expect(wrapper.html()).matches(/<modal-cohort-editor-stub/)
    expect(wrapper.html()).matches(/<toast-stub/)
    expect(wrapper.html()).not.matches(/<overlay-stub>/)
  })

  test('check overlay', async () => {
    const wrapper = shallowMount(CohortList, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              cohorts: {
                storeState: cohortsState.storeState,
                cohortCount: listCohortResponse.count,
                tableRows: listCohortResponse.results,
                serverInteractions: 1,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
    })

    expect(wrapper.html()).matches(/<overlay-stub>/)
  })
})

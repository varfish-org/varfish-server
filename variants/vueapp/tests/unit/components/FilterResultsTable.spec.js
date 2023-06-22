import { createTestingPinia } from '@pinia/testing'
import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
import { StoreState } from '@variants/stores/filterQuery'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import trioCaseData from '../../data/case-trio.json'
import trioVariantsData from '../../data/variants-trio.json'

describe('FilterResultsTable.vue', () => {
  test('results record count', () => {
    const wrapper = shallowMount(FilterResultsTable, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              variantDetails: {},
              filterQuery: {
                storeState: StoreState.initial,
                queryResults: trioVariantsData,
                queryResultsCount: trioVariantsData.length,
              },
              variantFlags: {
                storeState: StoreState.initial,
              },
              variantComments: {
                storeState: StoreState.initial,
              },
              variantAcmgRating: {
                storeState: StoreState.initial,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
      props: {
        case: trioCaseData,
        displayDetails: 0,
        displayFrequency: 2,
        displayConstraint: 3,
        displayColumns: [4],
        extraAnnoFields: [],
      },
    })

    expect(wrapper.get('#results-button').text()).toBe('3')
  })

  test('results no case', () => {
    const wrapper = shallowMount(FilterResultsTable, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              variantDetails: {},
              filterQuery: {
                storeState: StoreState.initial,
                queryResults: [],
                queryResultsCount: 0,
              },
              variantFlags: {
                storeState: StoreState.initial,
              },
              variantComments: {
                storeState: StoreState.initial,
              },
              variantAcmgRating: {
                storeState: StoreState.initial,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
      props: {
        case: null,
        displayDetails: 0,
        displayFrequency: 2,
        displayConstraint: 3,
        displayColumns: [4],
        extraAnnoFields: [],
      },
    })

    expect(wrapper.get('#results-button').text()).toBe('0')
  })
})

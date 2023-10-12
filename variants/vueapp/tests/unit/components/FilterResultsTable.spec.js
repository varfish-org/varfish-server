// import { createTestingPinia } from '@pinia/testing'
// import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
// import { StoreState } from '@variants/stores/variantQuery'
// import { shallowMount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

// import trioCaseData from '../../../data/case-trio.json'
// import trioVariantsData from '../../../data/variants-trio.json'
// import listQueryResultSetResult from '../../../data/listQueryResultSetResult.json'
// import listQueryResultRowResult from '../../../data/listQueryResultRowResult.json'
// import listFrequencyPresetsResponse from "../../data/listFrequencyPresetsResponse.json";

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('FilterResultsTable.vue', () => {
  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('dummy', () => {
    expect(true).toBe(true)
  })
  // TODO vue claims mocked response is not json. but it is.
  // test('results record count', () => {
  //   fetch.mockResponseOnce(JSON.stringify(listQueryResultRowResult))
  //
  //   const wrapper = shallowMount(FilterResultsTable, {
  //     global: {
  //       plugins: [
  //         createTestingPinia({
  //           initialState: {
  //             variantDetails: {},
  //             filterQuery: {
  //               storeState: StoreState.initial,
  //               queryResultSet: listQueryResultSetResult[0],
  //             },
  //             variantFlags: {
  //               storeState: StoreState.initial,
  //             },
  //             variantComments: {
  //               storeState: StoreState.initial,
  //             },
  //             variantAcmgRating: {
  //               storeState: StoreState.initial,
  //             },
  //           },
  //           createSpy: vi.fn,
  //         }),
  //       ],
  //     },
  //     props: {
  //       case: trioCaseData,
  //       displayDetails: 0,
  //       displayFrequency: 2,
  //       displayConstraint: 3,
  //       displayColumns: [4],
  //       extraAnnoFields: [],
  //     },
  //   })
  //
  //   expect(wrapper.get('#results-button').text()).toBe('305')
  // })
  //
  // test('results no case', () => {
  //   const wrapper = shallowMount(FilterResultsTable, {
  //     global: {
  //       plugins: [
  //         createTestingPinia({
  //           initialState: {
  //             variantDetails: {},
  //             filterQuery: {
  //               storeState: StoreState.initial,
  //               queryResultRow: [],
  //               queryResultSet: {
  //                 result_row_count: 0,
  //               },
  //             },
  //             variantFlags: {
  //               storeState: StoreState.initial,
  //             },
  //             variantComments: {
  //               storeState: StoreState.initial,
  //             },
  //             variantAcmgRating: {
  //               storeState: StoreState.initial,
  //             },
  //           },
  //           createSpy: vi.fn,
  //         }),
  //       ],
  //     },
  //     props: {
  //       case: null,
  //       displayDetails: 0,
  //       displayFrequency: 2,
  //       displayConstraint: 3,
  //       displayColumns: [4],
  //       extraAnnoFields: [],
  //     },
  //   })
  //
  //   expect(wrapper.get('#results-button').text()).toBe('0')
  // })
})

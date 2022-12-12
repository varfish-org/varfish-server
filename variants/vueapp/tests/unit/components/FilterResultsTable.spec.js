import FilterResultsTable from '@variants/components/FilterResultsTable.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import trioCaseData from '../../data/case-trio.json'
import trioVariantsData from '../../data/variants-trio.json'

describe('FilterResultsTable.vue', () => {
  test('results record count', () => {
    const wrapper = shallowMount(FilterResultsTable, {
      props: {
        case: trioCaseData,
        queryResults: trioVariantsData,
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
      props: {
        case: null,
        queryResults: [],
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

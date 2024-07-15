import CohortListHeader from '@/cohorts/components/CohortList/Header.vue'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import cohortsState from '../../../data/cohortsStoreData.json'
import listCohortResponse from '../../../data/listCohortResponse.json'

describe('CohortListH/eader.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('check initialization', async () => {
    const wrapper = shallowMount(CohortListHeader, {
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

    const createCohortButton = wrapper.get('.btn-primary')
    await createCohortButton.trigger('click')

    expect(wrapper.emitted()).toHaveProperty('createCohortClick')

    expect(wrapper.html()).matches(/Listing Cohorts for Project/)
    expect(wrapper.html()).contains(cohortsState.project.title)
  })
})

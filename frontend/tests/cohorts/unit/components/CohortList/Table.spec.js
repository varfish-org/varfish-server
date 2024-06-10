import CohortListTable from '@cohorts/components/CohortList/Table.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount, shallowMount } from '@vue/test-utils'
import cloneDeep from 'lodash/cloneDeep'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'

import accessibleProjectsCasesResponse from '../../../data/accessibleProjectsCasesResponse.json'
import cohortsState from '../../../data/cohortsStoreData.json'
import listCohortResponse from '../../../data/listCohortResponse.json'

describe('CohortListTable.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    // Mock out jquery dollar function for showing modals.
    const mockJQueryResult = vi.fn()
    mockJQueryResult.toast = vi.fn()
    mockJQueryResult.modal = vi.fn()
    mockJQueryResult.on = vi.fn()

    const mockJQuery = vi.fn()
    mockJQuery.mockReturnValue(mockJQueryResult)
    global.$ = mockJQuery
  })

  test('check initialize', async () => {
    const wrapper = shallowMount(CohortListTable, {
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

    expect(wrapper.html()).matches(/<data-table-stub/)
    expect(wrapper.html()).matches(/<modal-cohort-editor-stub/)
    expect(wrapper.html()).matches(/<modal-confirm-stub/)
    expect(wrapper.html()).matches(/<toast-stub/)

    expect(wrapper.get('h4').text()).toBe(
      'Cohort List ' + listCohortResponse.count,
    )
  })

  test('check table with button clicks', async () => {
    const wrapper = mount(CohortListTable, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              cohorts: {
                project: cohortsState.project,
                storeState: cohortsState.storeState,
                cohortCount: listCohortResponse.count,
                tableRows: listCohortResponse.results,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
    })

    vi.spyOn(wrapper.vm, 'handleDeleteCohortClicked')
    vi.spyOn(wrapper.vm, 'handleUpdateCohortClicked')

    const editButtons = wrapper.findAll('button.btn-sm.btn-primary')
    const deleteButtons = wrapper.findAll('button.btn-sm.btn-danger')

    expect(wrapper.findAll('tr').length).toBe(listCohortResponse.count + 1)
    expect(editButtons.length).toBe(2)
    expect(deleteButtons.length).toBe(2)

    editButtons[0].trigger('click')
    editButtons[1].trigger('click')

    deleteButtons[0].trigger('click')
    deleteButtons[1].trigger('click')

    expect(wrapper.vm.handleDeleteCohortClicked).toHaveBeenCalledTimes(2)
    expect(wrapper.vm.handleUpdateCohortClicked).toHaveBeenCalledTimes(2)

    expect(
      wrapper.vm.getMemberCount(accessibleProjectsCasesResponse[0].case_set),
    ).toBe(4)
    expect(
      wrapper.vm.getMemberCount(accessibleProjectsCasesResponse[1].case_set),
    ).toBe(3)

    expect(
      wrapper.vm.casesHaveSameRelease(
        accessibleProjectsCasesResponse[0].case_set,
      ),
    ).toBe(true)
    expect(
      wrapper.vm.casesHaveSameRelease(
        accessibleProjectsCasesResponse[1].case_set,
      ),
    ).toBe(true)
  })

  test('check table with different releases in cases', async () => {
    const listCohortResponseCopy = cloneDeep(listCohortResponse)
    listCohortResponseCopy.results[0].cases[0].release = 'GRCh38'

    const wrapper = mount(CohortListTable, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              cohorts: {
                project: cohortsState.project,
                storeState: cohortsState.storeState,
                cohortCount: listCohortResponseCopy.count,
                tableRows: listCohortResponseCopy.results,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
    })

    const filterLink = wrapper.findAll('a.btn-sm.btn-primary')
    const editButtons = wrapper.findAll('button.btn-sm.btn-primary')
    const deleteButtons = wrapper.findAll('button.btn-sm.btn-danger')

    expect(
      wrapper.vm.casesHaveSameRelease(listCohortResponseCopy.results[0].cases),
    ).toBe(false)
    expect(
      wrapper.vm.casesHaveSameRelease(listCohortResponseCopy.results[1].cases),
    ).toBe(true)

    expect(filterLink[0].classes()).toContain('disabled')
    expect(editButtons[0].element.disabled).toBe(false)
    expect(deleteButtons[0].element.disabled).toBe(false)

    expect(filterLink[1].classes()).not.toContain('disabled')
    expect(editButtons[1].element.disabled).toBe(false)
    expect(deleteButtons[1].element.disabled).toBe(false)
  })

  test('check table with inaccessible cases', async () => {
    const listCohortResponseCopy = cloneDeep(listCohortResponse)
    listCohortResponseCopy.results[0].inaccessible_cases = 1

    const wrapper = mount(CohortListTable, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              cohorts: {
                project: cohortsState.project,
                storeState: cohortsState.storeState,
                cohortCount: listCohortResponseCopy.count,
                tableRows: listCohortResponseCopy.results,
              },
            },
            createSpy: vi.fn,
          }),
        ],
      },
    })

    const filterLink = wrapper.findAll('a.btn-sm.btn-primary')
    const editButtons = wrapper.findAll('button.btn-sm.btn-primary')
    const deleteButtons = wrapper.findAll('button.btn-sm.btn-danger')

    expect(filterLink[0].classes()).not.toContain('disabled')
    expect(editButtons[0].element.disabled).toBe(true)
    expect(deleteButtons[0].element.disabled).toBe(true)

    expect(filterLink[1].classes()).not.toContain('disabled')
    expect(editButtons[1].element.disabled).toBe(false)
    expect(deleteButtons[1].element.disabled).toBe(false)
  })
})

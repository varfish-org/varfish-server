import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import ModalCohortEditor from '@/cohorts/components/ModalCohortEditor.vue'

import accessibleProjectsCasesResponse from '../../data/accessibleProjectsCasesResponse.json'
import cohortsState from '../../data/cohortsStoreData.json'
import listCohortResponse from '../../data/listCohortResponse.json'

describe('ModalCohortEditor.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('initialize', () => {
    const wrapper = shallowMount(ModalCohortEditor, {
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

    expect(wrapper.html()).match(/<modal-base-stub/)
  })

  test('buildProjectCasesSelected() with selected cases', () => {
    const wrapper = shallowMount(ModalCohortEditor, {
      props: {
        title: 'Create Cohort',
        modelValue: {
          name: '',
          cases: ['case1-fake-uuid', 'case5-fake-uuid', 'case2-fake-uuid'],
        },
        projectsCases: accessibleProjectsCasesResponse,
      },
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

    wrapper.vm.buildProjectCasesSelected()
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[0].sodar_uuid
      ].indeterminate,
    ).toBe(false)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[0].sodar_uuid
      ].checked,
    ).toBe(true)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[1].sodar_uuid
      ].indeterminate,
    ).toBe(true)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[1].sodar_uuid
      ].checked,
    ).toBe(false)

    expect(wrapper.vm.getSelectedMembersCount).toBe(5)

    expect(wrapper.vm.getSelectedCasesCount).toBe(3)

    expect(
      wrapper.vm.getSelectedProjectMembersCount(
        accessibleProjectsCasesResponse[0].case_set,
      ),
    ).toBe(4)
    expect(
      wrapper.vm.getSelectedProjectCasesCount(
        accessibleProjectsCasesResponse[0].case_set,
      ),
    ).toBe(2)
    expect(
      wrapper.vm.getSelectedProjectMembersCount(
        accessibleProjectsCasesResponse[1].case_set,
      ),
    ).toBe(1)
    expect(
      wrapper.vm.getSelectedProjectCasesCount(
        accessibleProjectsCasesResponse[1].case_set,
      ),
    ).toBe(1)
  })

  test('buildProjectCasesSelected() without selected cases', () => {
    const wrapper = shallowMount(ModalCohortEditor, {
      props: {
        title: 'Create Cohort',
        modelValue: {
          name: '',
          cases: [],
        },
        projectsCases: accessibleProjectsCasesResponse,
      },
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

    wrapper.vm.buildProjectCasesSelected()
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[0].sodar_uuid
      ].indeterminate,
    ).toBe(false)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[0].sodar_uuid
      ].checked,
    ).toBe(false)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[1].sodar_uuid
      ].indeterminate,
    ).toBe(false)
    expect(
      wrapper.vm.projectsCasesSelected[
        accessibleProjectsCasesResponse[1].sodar_uuid
      ].checked,
    ).toBe(false)

    expect(wrapper.vm.getSelectedMembersCount).toBe(0)

    expect(wrapper.vm.getSelectedCasesCount).toBe(0)

    expect(
      wrapper.vm.getSelectedProjectMembersCount(
        accessibleProjectsCasesResponse[0].case_set,
      ),
    ).toBe(0)
    expect(
      wrapper.vm.getSelectedProjectCasesCount(
        accessibleProjectsCasesResponse[0].case_set,
      ),
    ).toBe(0)
    expect(
      wrapper.vm.getSelectedProjectMembersCount(
        accessibleProjectsCasesResponse[1].case_set,
      ),
    ).toBe(0)
    expect(
      wrapper.vm.getSelectedProjectCasesCount(
        accessibleProjectsCasesResponse[1].case_set,
      ),
    ).toBe(0)
  })

  test('computeProgressBar()', () => {
    const wrapper = shallowMount(ModalCohortEditor, {
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

    expect(wrapper.vm.computeProgressBar(0, 10)).toBe(0)
    expect(wrapper.vm.computeProgressBar(5, 10)).toBe(50)
    expect(wrapper.vm.computeProgressBar(10, 10)).toBe(100)
    expect(wrapper.vm.computeProgressBar(2, 0)).toBe(0)
  })
})

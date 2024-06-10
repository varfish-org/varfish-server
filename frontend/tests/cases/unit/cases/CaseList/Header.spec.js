import CaseListHeader from '@cases/components/CaseList/Header.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (caseListState = {}) => {
  return mount(CaseListHeader, {
    shallow: true,
    global: {
      plugins: [
        createTestingPinia({
          initialState: { caseList: caseListState },
          createSpy: vi.fn,
        }),
      ],
    },
  })
}

describe('CaseListHeader.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  const caseListStore = {
    project: { sodar_uuid: 'fake-uuid', title: 'Project Title' },
  }

  test('render without help text', () => {
    const wrapper = makeWrapper({ showInlineHelp: false, ...caseListStore })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)
  })

  test('render with help text', () => {
    const wrapper = makeWrapper({ showInlineHelp: true, ...caseListStore })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
    expect(wrapper.findAll('.alert-secondary')[0].html()).toMatch(
      /This is the case list/,
    )
  })
})

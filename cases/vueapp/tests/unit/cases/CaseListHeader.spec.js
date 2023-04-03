import CaseListHeader from '@cases/components/CaseListHeader.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (casesState = {}) => {
  return mount(CaseListHeader, {
    shallow: true,
    global: {
      plugins: [
        createTestingPinia({
          initialState: { cases: casesState },
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

  const casesStore = {
    project: { sodar_uuid: 'fake-uuid', title: 'Project Title' },
  }

  test('render without help text', () => {
    const wrapper = makeWrapper({ showInlineHelp: false, ...casesStore })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)
  })

  test('render with help text', () => {
    const wrapper = makeWrapper({ showInlineHelp: true, ...casesStore })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
    expect(wrapper.findAll('.alert-secondary')[0].html()).toMatch(
      /This is the case list/
    )
  })
})

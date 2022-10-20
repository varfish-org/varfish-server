import CaseListContent from '@cases/components/CaseListContent.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (casesState = {}) => {
  return mount(CaseListContent, {
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

describe('CaseListContent.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  const casesStore = {
    project: { sodar_uuid: 'fake-uuid', title: 'Project Title' },
  }

  test('render cases tab', async () => {
    const wrapper = makeWrapper(casesStore)

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(wrapper.findAll('.nav-link').length).toBe(2)
    await wrapper.findAll('.nav-link')[0].trigger('click')

    expect(wrapper.html()).toMatch(/case-list-pane-cases-stub/)
    expect(wrapper.html()).not.toMatch(/case-list-pane-qc/)
  })

  test('render qc tab', async () => {
    const wrapper = makeWrapper(casesStore)

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(wrapper.findAll('.nav-link').length).toBe(2)
    await wrapper.findAll('.nav-link')[1].trigger('click')

    expect(wrapper.html()).not.toMatch(/case-list-pane-cases-stub/)
    expect(wrapper.html()).toMatch(/case-list-pane-qc/)
  })
})

import CaseListContent from '@cases/components/CaseList/Content.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'
import { createRouterMock, injectRouterMock } from 'vue-router-mock'

const makeWrapper = (casesState = {}, props = {}) => {
  return mount(CaseListContent, {
    shallow: true,
    props,
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

  const caseListStoreData = {
    project: { sodar_uuid: 'fake-uuid', title: 'Project Title' },
  }

  const router = createRouterMock({
    spy: {
      create: (fn) => vi.fn(fn),
      reset: (spy) => spy.mockReset(),
    },
  })

  beforeEach(() => {
    // Inject the mock router
    injectRouterMock(router)
  })

  test('render cases tab', async () => {
    const wrapper = makeWrapper(caseListStoreData, { currentTab: 'case-list' })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(wrapper.findAll('.nav-link').length).toBe(3)
    await wrapper.findAll('.nav-link')[0].trigger('click')

    expect(wrapper.html()).toMatch(/case-list-pane-cases-stub/)
    expect(wrapper.html()).not.toMatch(/case-list-pane-qc/)
    expect(wrapper.html()).not.toMatch(/query-presets-stub/)
  })

  test('render qc tab', async () => {
    const wrapper = makeWrapper(caseListStoreData, {
      currentTab: 'case-list-qc',
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(wrapper.findAll('.nav-link').length).toBe(3)
    await wrapper.findAll('.nav-link')[1].trigger('click')

    expect(wrapper.html()).not.toMatch(/case-list-pane-cases-stub/)
    expect(wrapper.html()).toMatch(/case-list-pane-qc/)
    expect(wrapper.html()).not.toMatch(/query-presets-stub/)
  })

  test('render filter tab', async () => {
    const wrapper = makeWrapper(caseListStoreData, {
      currentTab: 'case-list-query-presets',
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(0)

    expect(wrapper.findAll('.nav-link').length).toBe(3)
    await wrapper.findAll('.nav-link')[2].trigger('click')

    expect(wrapper.html()).not.toMatch(/case-list-pane-cases-stub/)
    expect(wrapper.html()).not.toMatch(/case-list-pane-qc/)
    expect(wrapper.html()).toMatch(/query-presets-stub/)
  })
})

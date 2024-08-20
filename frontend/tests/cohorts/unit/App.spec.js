import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'

import App from '@/cohorts/App.vue'

import cohortsState from '../data/cohortsStoreData.json'
import { quoteattr } from '../helpers'

const makeWrapper = (appContext) => {
  appContext = appContext || {
    csrf_token: 'fake-token',
    project: {
      sodar_uuid: 'fake-uuid',
      title: 'fake-title',
    },
  }
  const appContextStr = quoteattr(JSON.stringify(appContext))

  document.body.innerHTML = `
    <div>
      <div id="sodar-ss-app-context" app-context="${appContextStr}" />
      <div id="app"></div>
    </div>
  `

  return shallowMount(App, {
    attachTo: document.getElementById('app'),
    global: {
      plugins: [
        createTestingPinia({
          initialState: { cohorts: cohortsState },
          createSpy: vi.fn,
        }),
      ],
    },
  })
}

// Mock out the cases API
vi.mock('@/cohorts/api/cohorts.js')

describe('CohortList.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    // Mock out jquery dollar function for showing modals.
    const valResult = vi.fn()
    valResult.change = vi.fn()
    const mockJQueryResult = vi.fn()
    mockJQueryResult.prop = vi.fn()
    mockJQueryResult.val = vi.fn()
    mockJQueryResult.val.mockReturnValue(valResult)
    mockJQueryResult.change = vi.fn()
    const mockJQuery = vi.fn(function () {
      return this
    })
    mockJQuery.mockReturnValue(mockJQueryResult)
    global.$ = mockJQuery
  })

  test('check initialization', async () => {
    const wrapper = makeWrapper(App)

    expect(wrapper.html()).toBe('<router-view></router-view>')
  })
})

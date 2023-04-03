import casesApi from '@cases/api/cases.js'
import CaseList from '@cases/components/CaseList.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterEach, beforeAll, beforeEach, describe, test, vi } from 'vitest'

import caseListResponse from '../../data/caseListResponse.json'
import casesState from '../../data/casesStoreData.json'
import { quoteattr } from '../../helpers.js'

// Mock out the cases API
vi.mock('@cases/api/cases.js')

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

  return mount(CaseList, {
    attachTo: document.getElementById('app'),
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

describe('CaseList.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })
  beforeEach(() => {
    // Mock out jquery dollar function for showing modals
    const mockJQueryResult = vi.fn()
    mockJQueryResult.prop = vi.fn()
    mockJQueryResult.val = vi.fn()
    mockJQueryResult.change = vi.fn()
    const mockJQuery = vi.fn(function () {
      return this
    })
    mockJQuery.mockReturnValue(mockJQueryResult)
    global.$ = mockJQuery
  })

  afterEach(() => {
    global.$.mockRestore()
  })

  test('smoke test', async () => {
    casesApi.listCase.mockResolvedValue(caseListResponse)
    const _wrapper = makeWrapper()
  })
})

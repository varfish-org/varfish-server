import ClinvarExportApp from '@clinvarexport/components/ClinvarExportApp.vue'
import {
  AppState,
  useClinvarExportStore,
} from '@clinvarexport/stores/clinvar-export'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import {
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

import { rawAppContext } from '../fixtures'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState, extraArgs) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  if (!extraArgs) {
    extraArgs = {}
  }
  return shallowMount(ClinvarExportApp, {
    global: {
      plugins: [
        createTestingPinia({
          initialState: { clinvarExport: clinvarExportState },
          createSpy: vi.fn,
        }),
      ],
    },
    ...extraArgs,
  })
}
// Mock out the clinvarExport API
vi.mock('@clinvarexport/api/clinvarExport')

describe('ClinvarExportApp.vue', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  let appDiv
  let contextDiv
  beforeEach(() => {
    // Setup context and app divs
    appDiv = document.createElement('div')
    appDiv.id = 'app'
    document.body.appendChild(appDiv)
    contextDiv = document.createElement('div')
    contextDiv.id = 'sodar-ss-app-context'
    contextDiv.setAttribute('app-context', JSON.stringify(rawAppContext))
    document.body.append(contextDiv)
  })

  afterEach(() => {
    vi.clearAllMocks()
    // Cleanup context and app divs
    contextDiv.remove()
    appDiv.remove()
  })

  test('check initialization', async () => {
    const appDiv = document.createElement('div')
    appDiv.id = 'app'
    document.body.appendChild(appDiv)
    const contextDiv = document.createElement('div')
    contextDiv.id = 'sodar-ss-app-context'
    contextDiv.setAttribute('app-context', JSON.stringify(rawAppContext))
    document.body.append(contextDiv)

    makeWrapper({}, { attachTo: document.getElementById('app') })
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper

    expect(store.initialize).toHaveBeenCalledTimes(1)
    expect(store.initialize).toHaveBeenNthCalledWith(1, {
      baseUrl: rawAppContext.base_url,
      csrfToken: rawAppContext.csrf_token,
    })

    contextDiv.remove()
    appDiv.remove()
  })

  test('showOverlay', async () => {
    const wrapper = makeWrapper(
      {},
      { attachTo: document.getElementById('app') }
    )
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    const clinvarExportApp = wrapper.vm

    // when initializing
    store.appState = AppState.initializing
    expect(clinvarExportApp.showOverlay).toBe(true)
    store.appState = AppState.list
    expect(clinvarExportApp.showOverlay).toBe(false)
    // when communicating with server
    store.serverInteraction = true
    expect(clinvarExportApp.showOverlay).toBe(true)
    store.serverInteraction = false
    expect(clinvarExportApp.showOverlay).toBe(false)
  })
})

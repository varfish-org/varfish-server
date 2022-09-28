import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import ClinvarExportApp from '@/components/ClinvarExportApp.vue'
import { AppState } from '@/store/modules/clinvarExport.js'

import { copy } from '../../testUtils.js'
import { clinvarExportEmptyState, rawAppContext } from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('ClinvarExportApp.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  let appDiv
  let contextDiv
  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      initialize: jest.fn(),
    }
    const clinvarExport = {
      namespaced: true,
      actions,
      state: () => copy(clinvarExportEmptyState),
    }
    store = new Vuex.Store({
      modules: {
        clinvarExport,
      },
    })
    // setup context and app divs
    appDiv = document.createElement('div')
    appDiv.id = 'app'
    document.body.appendChild(appDiv)
    contextDiv = document.createElement('div')
    contextDiv.id = 'sodar-ss-app-context'
    contextDiv.setAttribute('app-context', JSON.stringify(rawAppContext))
    document.body.append(contextDiv)
  })

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
    // cleanup context and app divs
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

    shallowMount(ClinvarExportApp, {
      store,
      localVue,
      attachTo: document.getElementById('app'),
    })

    expect(actions.initialize).toHaveBeenCalledTimes(1)
    expect(actions.initialize).toHaveBeenNthCalledWith(1, expect.anything(), {
      appContext: {
        baseUrl: rawAppContext.base_url,
        csrfToken: rawAppContext.csrf_token,
      },
    })

    contextDiv.remove()
    appDiv.remove()
  })

  test('showOverlay', async () => {
    const wrapper = shallowMount(ClinvarExportApp, {
      store,
      localVue,
      attachTo: document.getElementById('app'),
    })
    const clinvarExportApp = wrapper.vm.$root.$children[0]

    // when initializing
    store.state.clinvarExport.appState = AppState.initializing
    expect(clinvarExportApp.showOverlay).toBe(true)
    store.state.clinvarExport.appState = AppState.list
    expect(clinvarExportApp.showOverlay).toBe(false)
    // when communicating with server
    store.state.clinvarExport.serverInteraction = true
    expect(clinvarExportApp.showOverlay).toBe(true)
    store.state.clinvarExport.serverInteraction = false
    expect(clinvarExportApp.showOverlay).toBe(false)
  })
})

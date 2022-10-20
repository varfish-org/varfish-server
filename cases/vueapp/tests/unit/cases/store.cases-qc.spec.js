import casesApi from '@cases/api/cases.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCasesQcStore } from '@cases/stores/cases-qc.js'
import flushPromises from 'flush-promises'
import { createPinia, setActivePinia } from 'pinia'
import {
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

import loadProjectQcValuesResponse from '../../data/loadProjectQcValuesResponse.json'

// Mock out the cases API
vi.mock('@cases/api/cases.js')

describe('cases-qc store', () => {
  const appContext = {
    csrfToken: 'fake-token',
    project: {
      sodar_uuid: 'fake-uuid',
      title: 'fake-title',
    },
  }

  let casesQcStore

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    const casesStore = useCasesStore()
    casesStore.appContext = appContext
    casesStore.project = appContext.project
    casesQcStore = useCasesQcStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('empty after construction', () => {
    expect(casesQcStore.qcValues).toEqual(null)
  })

  test('initialize', async () => {
    casesApi.loadProjectQcValues.mockResolvedValue(loadProjectQcValuesResponse)

    await casesQcStore.initialize()

    flushPromises()

    expect(casesApi.loadProjectQcValues).toHaveBeenCalled(1)
    expect(casesApi.loadProjectQcValues).toHaveBeenNthCalledWith(
      1,
      appContext.csrfToken,
      appContext.project.sodar_uuid
    )

    expect(casesQcStore.qcValues).toEqual(loadProjectQcValuesResponse)
  })
})

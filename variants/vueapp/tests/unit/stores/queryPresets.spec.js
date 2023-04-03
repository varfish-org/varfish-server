import { copy } from '@varfish/helpers.js'
import queryPresetsApi from '@variants/api/queryPresets.js'
import {
  Category,
  StoreState,
  useQueryPresetsStore,
} from '@variants/stores/queryPresets.js'
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
import createFetchMock from 'vitest-fetch-mock'

import listPresetSetResponse from '../../data/listPresetSetResponse.json'
import retrieveChromosomePresetsResponse from '../../data/retrieveChromosomePresetsResponse.json'
import retrieveFlagsEtcPresetsResponse from '../../data/retrieveFlagsEtcPresetsResponse.json'
import retrieveFrequencyPresetsResponse from '../../data/retrieveFrequencyPresetsResponse.json'
import retrieveImpactPresetsResponse from '../../data/retrieveImpactPresetsResponse.json'
import retrievePresetSetResponse from '../../data/retrievePresetSetResponse.json'
import retrieveQualityPresetsResponse from '../../data/retrieveQualityPresetsResponse.json'
import retrieveQuickPresetsResponse from '../../data/retrieveQuickPresetsResponse.json'

const retrieveData = {
  quickpresets: retrieveQuickPresetsResponse,
  frequencypresets: retrieveFrequencyPresetsResponse,
  impactpresets: retrieveImpactPresetsResponse,
  chromosomepresets: retrieveChromosomePresetsResponse,
  qualitypresets: retrieveQualityPresetsResponse,
  flagsetcpresets: retrieveFlagsEtcPresetsResponse,
}

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@variants/api/queryPresets.js')

describe('useQueryPresetsStore', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-project-uuid'
  const presetSetUuid = 'fake-presetset-uuid'
  const presetsUuid = 'fake-presets-uuid'
  const label = 'some label'

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  let queryPresetsStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createPinia())
    queryPresetsStore = useQueryPresetsStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('initial state', async () => {
    expect(queryPresetsStore.csrfToken).toBe(null)
    expect(queryPresetsStore.projectUuid).toBe(null)
    expect(queryPresetsStore.storeState).toBe(StoreState.initial)
    expect(queryPresetsStore.storeStateMessage).toBe('Initializing...')
    expect(queryPresetsStore.serverInteractions).toBe(0)
    expect(queryPresetsStore.presetSets).toEqual({})
    expect(queryPresetsStore.initializeRes).toBe(null)
  })

  test('initialize() on initial state', async () => {
    queryPresetsApi.listPresetSet.mockResolvedValue(listPresetSetResponse)

    await queryPresetsStore.initialize(csrfToken, projectUuid)

    expect(queryPresetsApi.listPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.listPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      projectUuid
    )
    expect(queryPresetsStore.serverInteractions).toEqual(0)
  })

  test('initialize() on error from API', async () => {
    queryPresetsApi.listPresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })

    await expect(
      queryPresetsStore.initialize(csrfToken, projectUuid)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.listPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.listPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      projectUuid
    )
    expect(queryPresetsStore.storeState).toEqual(StoreState.error)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
  })

  test('initialize() on non-initial state', async () => {
    queryPresetsApi.listPresetSet.mockResolvedValue(listPresetSetResponse)

    queryPresetsStore.storeState = StoreState.action
    queryPresetsStore.initializeRes = Promise.resolve(listPresetSetResponse)

    const result = await queryPresetsStore.initialize(csrfToken, projectUuid)

    expect(result).toBe(listPresetSetResponse)
    expect(queryPresetsApi.listPresetSet).not.toHaveBeenCalled()
    expect(queryPresetsStore.serverInteractions).toEqual(0)
  })

  test('cloneFactoryPresetSet() with working API call', async () => {
    queryPresetsApi.cloneFactoryPresetSet.mockResolvedValue(
      retrievePresetSetResponse
    )
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(0)

    const result = await queryPresetsStore.cloneFactoryPresetSet(label)
    expect(result).toEqual(retrievePresetSetResponse)

    expect(queryPresetsApi.cloneFactoryPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.cloneFactoryPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      { project: projectUuid, label }
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
    expect(Object.keys(queryPresetsStore.presetSets)).toEqual([
      retrievePresetSetResponse.sodar_uuid,
    ])
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Cloning factory defaults...'
    )
  })

  test('cloneFactoryPresetSet() with exception', async () => {
    queryPresetsApi.cloneFactoryPresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid
    expect(queryPresetsStore.serverInteractions).toEqual(0)

    await expect(
      queryPresetsStore.cloneFactoryPresetSet(label)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.cloneFactoryPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.cloneFactoryPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      { project: projectUuid, label }
    )
    expect(queryPresetsStore.storeState).toEqual(StoreState.active)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Cloning factory defaults...'
    )
  })

  test('cloneOtherPresetSet() with working API call', async () => {
    queryPresetsApi.cloneOtherPresetSet.mockResolvedValue(
      retrievePresetSetResponse
    )
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(0)

    const result = await queryPresetsStore.cloneOtherPresetSet(
      presetSetUuid,
      label
    )
    expect(result).toEqual(retrievePresetSetResponse)

    expect(queryPresetsApi.cloneOtherPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.cloneOtherPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid,
      { project: projectUuid, label }
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
    expect(Object.keys(queryPresetsStore.presetSets)).toEqual([
      retrievePresetSetResponse.sodar_uuid,
    ])
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual('Cloning preset set...')
  })

  test('cloneOtherPresetSet() with exception', async () => {
    queryPresetsApi.cloneOtherPresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid
    expect(queryPresetsStore.serverInteractions).toEqual(0)

    await expect(
      queryPresetsStore.cloneOtherPresetSet(presetSetUuid, label)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.cloneOtherPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.cloneOtherPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid,
      { project: projectUuid, label }
    )
    expect(queryPresetsStore.storeState).toEqual(StoreState.active)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual('Cloning preset set...')
  })

  test('revertPresetSet() with working API call', async () => {
    queryPresetsApi.retrievePresetSet.mockResolvedValue(
      retrievePresetSetResponse
    )
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(0)

    const result = await queryPresetsStore.revertPresetSet(presetSetUuid)
    expect(result).toEqual(retrievePresetSetResponse)

    expect(queryPresetsApi.retrievePresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.retrievePresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
    expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Loading preset set from server...'
    )
  })

  test('revertPresetSet() with exception', async () => {
    queryPresetsApi.retrievePresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(queryPresetsStore.serverInteractions).toEqual(0)

    await expect(
      queryPresetsStore.revertPresetSet(presetSetUuid)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.retrievePresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.retrievePresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid
    )
    expect(queryPresetsStore.storeState).toEqual(StoreState.active)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Loading preset set from server...'
    )
  })

  test('updatePresetSet() with working API call', async () => {
    queryPresetsApi.updatePresetSet.mockResolvedValue(retrievePresetSetResponse)
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(0)

    const result = await queryPresetsStore.updatePresetSet(presetSetUuid, label)
    expect(result).toEqual(retrievePresetSetResponse)

    expect(queryPresetsApi.updatePresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.updatePresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid,
      { label }
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
    expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Updating preset set...'
    )
  })

  test('updatePresetSet() with exception', async () => {
    queryPresetsApi.updatePresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid

    expect(queryPresetsStore.serverInteractions).toEqual(0)

    await expect(
      queryPresetsStore.updatePresetSet(presetSetUuid, label)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.updatePresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.updatePresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid,
      { label }
    )
    expect(queryPresetsStore.storeState).toEqual(StoreState.active)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Updating preset set...'
    )
  })

  test('destroyPresetSet() with working API call', async () => {
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid
    queryPresetsStore.presetSets[presetSetUuid] = copy(
      retrievePresetSetResponse
    )

    await queryPresetsStore.destroyPresetSet(presetSetUuid)

    expect(queryPresetsApi.destroyPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.destroyPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(0)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Deleting preset set...'
    )
  })

  test('destroyPresetSet() with exception', async () => {
    queryPresetsApi.destroyPresetSet = vi.fn(async () => {
      throw new Error('fake error')
    })
    queryPresetsStore.storeState = StoreState.active
    queryPresetsStore.csrfToken = csrfToken
    queryPresetsStore.projectUuid = projectUuid
    queryPresetsStore.presetSets = {}
    queryPresetsStore.presetSets[presetSetUuid] = copy(
      retrievePresetSetResponse
    )

    expect(queryPresetsStore.serverInteractions).toEqual(0)

    await expect(
      queryPresetsStore.destroyPresetSet(presetSetUuid)
    ).rejects.toThrow('fake error')

    expect(queryPresetsApi.destroyPresetSet).toHaveBeenCalled(1)
    expect(queryPresetsApi.destroyPresetSet).toHaveBeenNthCalledWith(
      1,
      csrfToken,
      presetSetUuid
    )

    expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
    expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
    expect(queryPresetsStore.storeState).toEqual(StoreState.active)
    expect(queryPresetsStore.serverInteractions).toEqual(0)
    expect(queryPresetsStore.storeStateMessage).toEqual(
      'Deleting preset set...'
    )
  })

  test.each(Object.keys(Category).map((name) => [name]))(
    'createPresets() cat=%s with working API call',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `create${cat.name}`
      const payload = {
        ...retrieveData[category],
        sodar_uuid: presetsUuid,
      }

      queryPresetsApi[apiFunc] = vi.fn(async () => payload)
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )

      await queryPresetsStore.createPresets(category, presetSetUuid, payload)

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetSetUuid,
        payload
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(2)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`][1]
      ).toEqual(payload)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Creating ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'createPresets() cat=%s with exception',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `create${cat.name}`
      const payload = retrieveData[category]

      queryPresetsApi[apiFunc] = vi.fn(async () => {
        throw new Error('fake error')
      })
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets = {}
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )

      expect(queryPresetsStore.serverInteractions).toEqual(0)

      await expect(
        queryPresetsStore.createPresets(category, presetSetUuid, payload)
      ).rejects.toThrow('fake error')

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetSetUuid,
        payload
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
      expect(queryPresetsStore.storeState).toEqual(StoreState.active)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Creating ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'clonePresets() cat=%s with working API call',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `cloneOther${cat.name}`
      const payload = {
        ...retrieveData[category],
      }

      queryPresetsApi[apiFunc] = vi.fn(async () => payload)
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(1)

      await queryPresetsStore.clonePresets(
        category,
        presetSetUuid,
        presetsUuid,
        label
      )

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid,
        { label, presetset: presetSetUuid }
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(2)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`][1]
      ).toEqual(payload)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Cloning ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'clonePresets() cat=%s with exception',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `cloneOther${cat.name}`

      queryPresetsApi[apiFunc] = vi.fn(async () => {
        throw new Error('fake error')
      })
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets = {}
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      const presetsUuid =
        retrievePresetSetResponse[`${category}_set`][0].sodar_uuid

      expect(queryPresetsStore.serverInteractions).toEqual(0)

      await expect(
        queryPresetsStore.clonePresets(
          category,
          presetSetUuid,
          presetsUuid,
          label
        )
      ).rejects.toThrow('fake error')

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid,
        { label, presetset: presetSetUuid }
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
      expect(queryPresetsStore.storeState).toEqual(StoreState.active)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Cloning ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'revertPresets() cat=%s with working API call',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `retrieve${cat.name}`
      const payload = {
        ...copy(retrieveData[category]),
        sodar_uuid: presetsUuid,
      }

      queryPresetsApi[apiFunc] = vi.fn(async () => payload)
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      queryPresetsStore.presetSets[presetSetUuid][
        `${category}_set`
      ][0].sodar_uuid = presetsUuid
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`][0]
      ).toEqual(payload)

      await queryPresetsStore.revertPresets(
        category,
        presetSetUuid,
        presetsUuid
      )

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`][0]
      ).toEqual(payload)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Reverting ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'revertPresets() cat=%s with exception',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `retrieve${cat.name}`

      queryPresetsApi[apiFunc] = vi.fn(async () => {
        throw new Error('fake error')
      })
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets = {}
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      const presetsUuid =
        retrievePresetSetResponse[`${category}_set`][0].sodar_uuid

      expect(queryPresetsStore.serverInteractions).toEqual(0)

      await expect(
        queryPresetsStore.revertPresets(category, presetSetUuid, presetsUuid)
      ).rejects.toThrow('fake error')

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
      expect(queryPresetsStore.storeState).toEqual(StoreState.active)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Reverting ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'updatePresets() cat=%s with working API call',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `update${cat.name}`
      const payload = {
        ...retrieveData[category],
        sodar_uuid: presetsUuid,
      }

      queryPresetsApi[apiFunc] = vi.fn(async () => payload)
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      queryPresetsStore.presetSets[presetSetUuid][`${category}_set`][0] = {
        ...payload,
        label: 'overwrite me',
      }

      await queryPresetsStore.updatePresets(
        category,
        presetSetUuid,
        presetsUuid,
        payload
      )

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid,
        payload
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`][0]
      ).toEqual(payload)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Updating ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'updatePresets() cat=%s with exception',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `update${cat.name}`
      const payload = retrieveData[category]

      queryPresetsApi[apiFunc] = vi.fn(async () => {
        throw new Error('fake error')
      })
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets = {}
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      queryPresetsStore.presetSets[presetSetUuid][`${category}_set`][0] = {
        ...payload,
        label: 'overwrite me',
      }

      expect(queryPresetsStore.serverInteractions).toEqual(0)

      await expect(
        queryPresetsStore.updatePresets(
          category,
          presetSetUuid,
          presetsUuid,
          payload
        )
      ).rejects.toThrow('fake error')

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid,
        payload
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
      expect(queryPresetsStore.storeState).toEqual(StoreState.active)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Updating ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'destroyPresets() cat=%s with working API call',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `destroy${cat.name}`
      const payload = {
        ...retrieveData[category],
        sodar_uuid: presetsUuid,
      }

      queryPresetsApi[apiFunc] = vi.fn(async () => {})
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      queryPresetsStore.presetSets[presetSetUuid][`${category}_set`][0] =
        payload

      await queryPresetsStore.destroyPresets(
        category,
        presetSetUuid,
        presetsUuid
      )

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(
        Object.values(queryPresetsStore.presetSets)[0][`${category}_set`].length
      ).toBe(0)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Deleting ${cat.title}...`
      )
    }
  )

  test.each(Object.keys(Category).map((name) => [name]))(
    'destroyPresets() cat=%s with exception',
    async (category) => {
      const cat = Category[category]
      const apiFunc = `destroy${cat.name}`
      const payload = retrieveData[category]

      queryPresetsApi[apiFunc] = vi.fn(async () => {
        throw new Error('fake error')
      })
      queryPresetsStore.storeState = StoreState.active
      queryPresetsStore.csrfToken = csrfToken
      queryPresetsStore.projectUuid = projectUuid
      queryPresetsStore.presetSets = {}
      queryPresetsStore.presetSets[presetSetUuid] = copy(
        retrievePresetSetResponse
      )
      queryPresetsStore.presetSets[presetSetUuid][`${category}_set`][0] =
        payload

      expect(queryPresetsStore.serverInteractions).toEqual(0)

      await expect(
        queryPresetsStore.destroyPresets(category, presetSetUuid, presetsUuid)
      ).rejects.toThrow('fake error')

      expect(queryPresetsApi[apiFunc]).toHaveBeenCalled(1)
      expect(queryPresetsApi[apiFunc]).toHaveBeenNthCalledWith(
        1,
        csrfToken,
        presetsUuid
      )

      expect(Object.keys(queryPresetsStore.presetSets).length).toBe(1)
      expect(Object.keys(queryPresetsStore.presetSets)).toEqual([presetSetUuid])
      expect(queryPresetsStore.storeState).toEqual(StoreState.active)
      expect(queryPresetsStore.serverInteractions).toEqual(0)
      expect(queryPresetsStore.storeStateMessage).toEqual(
        `Deleting ${cat.title}...`
      )
    }
  )
})

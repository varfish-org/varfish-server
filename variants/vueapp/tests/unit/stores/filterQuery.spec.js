import { createTestingPinia } from '@pinia/testing'
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'
import { setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('useFilterQueryStore', () => {
  let filterQueryStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createTestingPinia({ createSpy: vi.fn }))
    filterQueryStore = useFilterQueryStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('smoke test', async () => {
    expect(true).not.toBe(false)
    const _ = filterQueryStore
  })
})

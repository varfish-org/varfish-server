import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { useVariantDetailsStore } from '@/variants/stores/variantDetails'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('useVariantDetailsStore', () => {
  let variantDetailsStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createTestingPinia({ createSpy: vi.fn }))
    variantDetailsStore = useVariantDetailsStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('smoke test', async () => {
    expect(true).not.toBe(false)
    const _ = variantDetailsStore
  })
})

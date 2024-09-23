import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('useVariantQueryStore', () => {
  let variantQueryStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createTestingPinia({ createSpy: vi.fn }))
    variantQueryStore = useVariantQueryStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('smoke test', async () => {
    expect(true).not.toBe(false)
    const _ = variantQueryStore
  })
})

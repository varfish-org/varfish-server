import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'
import { QueryStates } from '@/variants/enums'

import { useVariantQueryStore } from './variantQuery'

vi.mock('@/variants/api/variantClient')

/** Error as thrown by `fetchHelper` for a non-2xx response. */
const apiError = (status: number, data: any) =>
  Object.assign(new Error('API request failed'), {
    response: { status },
    data,
  })

describe('useVariantQueryStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(VariantClient).mockReset()
  })

  /** Return store whose query creation fails with the given error. */
  const setupStore = (error: Error) => {
    vi.mocked(VariantClient).mockImplementation(
      () => ({ createQuery: vi.fn().mockRejectedValue(error) }) as any,
    )
    const store = useVariantQueryStore()
    store.querySettings = {}
    return store
  }

  test('shows the validation messages when the query is rejected', async () => {
    const store = setupStore(
      apiError(400, {
        query_settings: [
          '$.gnomad_exomes_frequency: 0.1 is greater than the maximum of 0.05',
        ],
      }),
    )

    await store.submitQuery()

    expect(store.queryState).toBe(QueryStates.Error.value)
    expect(store.queryStateMsg).toBe(
      '$.gnomad_exomes_frequency: 0.1 is greater than the maximum of 0.05',
    )
  })

  test('reports an error without message when the query creation fails otherwise', async () => {
    const store = setupStore(
      apiError(500, { detail: '<!DOCTYPE html><html>Server Error</html>' }),
    )

    await store.submitQuery()

    expect(store.queryState).toBe(QueryStates.Error.value)
    expect(store.queryStateMsg).toBeNull()
  })
})

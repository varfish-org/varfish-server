import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { SvClient } from '@/svs/api/strucvarClient'
import { QueryStates } from '@/variants/enums'

import { useSvQueryStore } from './svQuery'

vi.mock('@/svs/api/strucvarClient')

/** Error as thrown by `fetchHelper` for a non-2xx response. */
const apiError = (status: number, data: any) =>
  Object.assign(new Error('API request failed'), {
    response: { status },
    data,
  })

describe('useSvQueryStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(SvClient).mockReset()
  })

  /** Return store whose query creation fails with the given error. */
  const setupStore = (error: Error) => {
    vi.mocked(SvClient).mockImplementation(
      () => ({ createSvQuery: vi.fn().mockRejectedValue(error) }) as any,
    )
    const store = useSvQueryStore()
    store.querySettings = {}
    return store
  }

  test('shows the validation messages when the query is rejected', async () => {
    const store = setupStore(
      apiError(400, {
        query_settings: ['$.sv_size_min: -1 is less than the minimum of 0'],
      }),
    )

    await store.submitQuery()

    expect(store.queryState).toBe(QueryStates.Error.value)
    expect(store.queryStateMsg).toBe(
      '$.sv_size_min: -1 is less than the minimum of 0',
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

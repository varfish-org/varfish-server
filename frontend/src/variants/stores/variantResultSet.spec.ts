import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'

import { useVariantResultSetStore } from './variantResultSet'

vi.mock('@/variants/api/variantClient')

/** Promise that is resolved from the outside, to control response order. */
const deferred = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((res) => {
    resolve = res
  })
  return { promise, resolve }
}

const queryResultSet = { sodar_uuid: 'query-result-set' }
const caseResultSet = { sodar_uuid: 'case-result-set' }
const rowResultSet = { sodar_uuid: 'row-result-set', case: 'case-uuid' }

describe('useVariantResultSetStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(VariantClient).mockReset()
  })

  /** Return store with the given client mock. */
  const setupStore = (client: any) => {
    vi.mocked(VariantClient).mockImplementation(() => client)
    const store = useVariantResultSetStore()
    store.extraAnnoFields = []
    return store
  }

  test('shows the query result set requested by the query view', async () => {
    const store = setupStore({
      listQueryResultSet: vi.fn().mockResolvedValue([queryResultSet]),
    })

    store.resultSetSource = 'query'
    await store.loadResultSetViaQuery('query-uuid')

    expect(store.resultSetUuid).toBe('query-result-set')
  })

  test('discards a query result set that arrives after the case result set was requested', async () => {
    const queryResponse = deferred<any[]>()
    const store = setupStore({
      listQueryResultSet: vi.fn().mockReturnValue(queryResponse.promise),
      retrieveCase: vi
        .fn()
        .mockResolvedValue({ smallvariantqueryresultset: caseResultSet }),
    })

    store.resultSetSource = 'query'
    const queryLoad = store.loadResultSetViaQuery('query-uuid')
    await store.loadResultSetViaCase('case-uuid')
    queryResponse.resolve([queryResultSet])
    await queryLoad

    expect(store.resultSetUuid).toBe('case-result-set')
  })

  test('discards a query result set requested after the case result set', async () => {
    const store = setupStore({
      listQueryResultSet: vi.fn().mockResolvedValue([queryResultSet]),
      retrieveCase: vi
        .fn()
        .mockResolvedValue({ smallvariantqueryresultset: caseResultSet }),
    })

    store.resultSetSource = 'query'
    await store.loadResultSetViaCase('case-uuid')
    await store.loadResultSetViaQuery('query-uuid')

    expect(store.resultSetUuid).toBe('case-result-set')
  })

  test('discards a case result set that arrives after a result row was requested', async () => {
    const caseResponse = deferred<any>()
    const store = setupStore({
      retrieveCase: vi.fn().mockReturnValue(caseResponse.promise),
      retrieveQueryResultRow: vi.fn().mockResolvedValue({
        sodar_uuid: 'row-uuid',
        smallvariantqueryresultset: 'row-result-set',
      }),
      retrieveQueryResultSet: vi.fn().mockResolvedValue(rowResultSet),
    })

    const caseLoad = store.loadResultSetViaCase('case-uuid')
    await store.fetchResultSetViaRow('row-uuid')
    caseResponse.resolve({ smallvariantqueryresultset: caseResultSet })
    await caseLoad

    expect(store.resultSetUuid).toBe('row-result-set')
  })

  test("discards a result row's result set that arrives after the case result set was requested", async () => {
    const rowResponse = deferred<any>()
    const store = setupStore({
      retrieveQueryResultRow: vi.fn().mockReturnValue(rowResponse.promise),
      retrieveQueryResultSet: vi.fn().mockResolvedValue(rowResultSet),
      retrieveCase: vi
        .fn()
        .mockResolvedValue({ smallvariantqueryresultset: caseResultSet }),
    })

    const rowLoad = store.fetchResultSetViaRow('row-uuid')
    await store.loadResultSetViaCase('case-uuid')
    rowResponse.resolve({
      sodar_uuid: 'row-uuid',
      smallvariantqueryresultset: 'row-result-set',
    })
    await rowLoad

    expect(store.resultSetUuid).toBe('case-result-set')
    expect(store.resultRow).toBeNull()
  })
})

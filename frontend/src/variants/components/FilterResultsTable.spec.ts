import { createTestingPinia } from '@pinia/testing'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'

import FilterResultsTable from './FilterResultsTable.vue'

vi.mock('@/variants/api/variantClient')

describe('FilterResultsTable', () => {
  test('loads the rows of a result set that is set after mounting', async () => {
    const listQueryResultRow = vi.fn().mockResolvedValue({ results: [] })
    vi.mocked(VariantClient).mockImplementation(
      () => ({ listQueryResultRow }) as any,
    )
    const pinia = createTestingPinia({ createSpy: vi.fn })
    const resultSetStore = useVariantResultSetStore(pinia)
    resultSetStore.extraAnnoFields = []
    shallowMount(FilterResultsTable, { global: { plugins: [pinia] } })
    await flushPromises()

    resultSetStore.resultSet = { result_row_count: 0 }
    resultSetStore.resultSetUuid = 'case-result-set'
    await flushPromises()

    expect(listQueryResultRow).toHaveBeenCalledWith(
      'case-result-set',
      expect.anything(),
    )
  })
})

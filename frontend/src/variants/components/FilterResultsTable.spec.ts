import { createTestingPinia } from '@pinia/testing'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import EasyDataTable from 'vue3-easy-data-table'

import { VariantClient } from '@/variants/api/variantClient'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
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

describe('FilterResultsTable row classes', () => {
  /** Return the row class function the table is configured with. */
  const mountRowClassName = (flags: any) => {
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listQueryResultRow: vi.fn().mockResolvedValue({ results: [] }),
        }) as any,
    )
    const pinia = createTestingPinia({ createSpy: vi.fn })
    const resultSetStore = useVariantResultSetStore(pinia)
    resultSetStore.extraAnnoFields = []
    resultSetStore.lastVisited = 'visited-row'
    const flagsStore = useVariantFlagsStore(pinia)
    flagsStore.caseFlags = new Map() as any
    vi.mocked(flagsStore.getFlags).mockReturnValue(flags)
    const wrapper = shallowMount(FilterResultsTable, {
      global: { plugins: [pinia] },
    })
    return wrapper.findComponent(EasyDataTable).props('bodyRowClassName')
  }

  const payload = {
    release: 'GRCh37',
    chromosome: '1',
    start: 100,
    reference: 'A',
    alternative: 'G',
  }

  test('marks the last visited row in addition to its flag color', () => {
    const rowClassName = mountRowClassName({ flag_summary: 'positive' })

    expect(
      rowClassName({ sodar_uuid: 'visited-row', payload }, 1).split(' ').sort(),
    ).toEqual(['last-visited-row', 'positive-row'])
  })

  test('marks an unflagged last visited row', () => {
    const rowClassName = mountRowClassName(undefined)

    expect(rowClassName({ sodar_uuid: 'visited-row', payload }, 1)).toBe(
      'last-visited-row',
    )
  })

  test('colors other rows by their flags only', () => {
    const rowClassName = mountRowClassName({ flag_summary: 'positive' })

    expect(rowClassName({ sodar_uuid: 'other-row', payload }, 1)).toBe(
      'positive-row',
    )
  })
})

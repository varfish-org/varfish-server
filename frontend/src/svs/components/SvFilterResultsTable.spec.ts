import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import EasyDataTable from 'vue3-easy-data-table'

import { SvClient } from '@/svs/api/strucvarClient'
import { useSvFlagsStore } from '@/svs/stores/strucvarFlags'
import { useSvResultSetStore } from '@/svs/stores/svResultSet'

import SvFilterResultsTable from './SvFilterResultsTable.vue'

vi.mock('@/svs/api/strucvarClient')

describe('SvFilterResultsTable row classes', () => {
  /** Return the row class function the table is configured with. */
  const mountRowClassName = (flags: any) => {
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listSvQueryResultRow: vi.fn().mockResolvedValue({ results: [] }),
        }) as any,
    )
    const pinia = createTestingPinia({ createSpy: vi.fn })
    useSvResultSetStore(pinia).lastVisited = 'visited-row'
    const svFlagsStore = useSvFlagsStore(pinia)
    svFlagsStore.caseFlags = new Map() as any
    vi.mocked(svFlagsStore.getFlags).mockReturnValue(flags)
    const wrapper = shallowMount(SvFilterResultsTable, {
      global: { plugins: [pinia] },
    })
    return wrapper.findComponent(EasyDataTable).props('bodyRowClassName')
  }

  test('marks the last visited row in addition to its flag color', () => {
    const rowClassName = mountRowClassName({ flag_summary: 'positive' })

    expect(
      rowClassName({ sodar_uuid: 'visited-row' }, 1).split(' ').sort(),
    ).toEqual(['last-visited-row', 'positive-row'])
  })

  test('marks the last visited row in addition to its bookmark color', () => {
    const rowClassName = mountRowClassName({ flag_candidate: true })

    expect(
      rowClassName({ sodar_uuid: 'visited-row' }, 1).split(' ').sort(),
    ).toEqual(['bookmarked-row', 'last-visited-row'])
  })

  test('marks an unflagged last visited row', () => {
    const rowClassName = mountRowClassName(undefined)

    expect(rowClassName({ sodar_uuid: 'visited-row' }, 1)).toBe(
      'last-visited-row',
    )
  })

  test('colors other rows by their flags only', () => {
    const rowClassName = mountRowClassName({ flag_summary: 'positive' })

    expect(rowClassName({ sodar_uuid: 'other-row' }, 1)).toBe('positive-row')
  })
})

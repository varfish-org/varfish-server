import { columnDefs } from '@cases/components/CaseListPaneCases.values.js'
import CaseListPaneCases from '@cases/components/CaseListPaneCases.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterAll, beforeAll, describe, expect, test, vi } from 'vitest'

import casesState from '../../data/casesStoreData.json'
import { waitAG, waitRAF } from '../../helpers.js'

const makeWrapper = () => {
  return mount(CaseListPaneCases, {
    global: {
      plugins: [
        createTestingPinia({
          initialState: { cases: casesState },
          createSpy: vi.fn,
        }),
      ],
    },
    shallow: true,
  })
}

describe('CaseListPaneCases.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Set reproducible time
    vi.useFakeTimers('modern')
    vi.setSystemTime(new Date(2020, 3, 1))
  })

  afterAll(() => {
    vi.useRealTimers()
  })

  test('test rendering', async () => {
    const wrapper = makeWrapper()
    await waitAG(wrapper)
    await waitRAF()

    expect(wrapper.findAll('ag-grid-vue-stub').length).toBe(1)
  })

  test('test column cellRenderer 0 / index', () => {
    expect(columnDefs[0].field).toEqual('index')
    expect(columnDefs[0].cellRenderer({ value: 1 })).toEqual(
      '<span class="text-muted">#1</span>'
    )
  })

  test('test column valueGetter 3 / individuals', () => {
    expect(columnDefs[3].field).toEqual('individuals')
    expect(
      columnDefs[3].valueGetter({
        data: { pedigree: [{ name: 'x' }, { name: 'y' }] },
      })
    ).toEqual('x, y')
  })

  test('test column valueFormatter 4 / num_small_vars', () => {
    expect(columnDefs[4].field).toEqual('num_small_vars')
    expect(columnDefs[4].valueFormatter({ value: 1000000 })).toEqual(
      '1,000,000'
    )
  })

  test('test column valueFormatter 5 / num_svs', () => {
    expect(columnDefs[5].field).toEqual('num_svs')
    expect(columnDefs[5].valueFormatter({ value: 1000000 })).toEqual(
      '1,000,000'
    )
  })

  test('test column valueFormatter 6 / date_created', () => {
    expect(columnDefs[6].field).toEqual('date_created')
    expect(
      columnDefs[6].valueFormatter({ value: '2020-01-26T15:52:37.674189Z' })
    ).toEqual('2 months ago')
  })
})

import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import ColumnSizeFitter from '@/variants/components/ColumnSizeFitter.vue'

describe('ColumnSizeFitter.vue', () => {
  test('size to fit button works', async () => {
    const gridApi = {
      sizeColumnsToFit: vi.fn(),
    }

    const wrapper = shallowMount(ColumnSizeFitter, {
      props: {
        gridApi,
      },
    })

    const sizeToFitBtn =
      wrapper.findAll('#columnSizeFitter')[0].wrapperElement.childNodes[0]
    await sizeToFitBtn.click()
    expect(gridApi.sizeColumnsToFit).toHaveBeenCalled()
  })

  test('auto size all button works', async () => {
    const columnApi = {
      getColumns: vi.fn(),
      autoSizeColumns: vi.fn(),
    }
    columnApi.getColumns.mockReturnValueOnce([
      {
        getId() {
          return 'theId'
        },
      },
    ])

    const wrapper = shallowMount(ColumnSizeFitter, {
      props: {
        columnApi,
      },
    })

    const autoSizeAllBtn =
      wrapper.findAll('#columnSizeFitter')[0].wrapperElement.childNodes[1]
    await autoSizeAllBtn.click()
    expect(columnApi.getColumns).toHaveBeenCalled()
    expect(columnApi.autoSizeColumns).toHaveBeenCalled()
    expect(columnApi.autoSizeColumns).toHaveBeenNthCalledWith(1, ['theId'])
  })

  test('auto size all button works with empty columnApi', async () => {
    const wrapper = shallowMount(ColumnSizeFitter, {
      props: {},
    })

    const autoSizeAllBtn =
      wrapper.findAll('#columnSizeFitter')[0].wrapperElement.childNodes[1]
    await autoSizeAllBtn.click()
  })
})

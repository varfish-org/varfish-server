import { shallowMount } from '@vue/test-utils'
import Multiselect from '@vueform/multiselect'
import { describe, test } from 'vitest'

import ColumnControl from '@/variants/components/ColumnControl.vue'

describe('ColumnControl.vue', () => {
  test('set column controls', async () => {
    const wrapper = shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: [0, 1],
      },
    })

    const selectors = wrapper.findAll('select')
    const displayDetails = selectors[0]
    const displayFrequency = selectors[1]
    const displayConstraint = selectors[2]
    const displayColumns = wrapper.findComponent(Multiselect)

    await displayDetails.setValue(1)
    await displayFrequency.setValue(1)
    await displayConstraint.setValue(1)
    await displayColumns.setValue([0, 1, 2])
  })

  test('set column controls empty display columns', () => {
    shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: null,
      },
    })
  })

  test('set column controls without column api', async () => {
    const wrapper = shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: [0, 1],
      },
    })
    const selectors = wrapper.findAll('select')
    const displayDetails = selectors[0]
    const displayFrequency = selectors[1]
    const displayConstraint = selectors[2]
    const displayColumns = wrapper.findComponent(Multiselect)

    await displayDetails.setValue(1)
    await displayFrequency.setValue(1)
    await displayConstraint.setValue(1)
    await displayColumns.setValue([0, 1, 2])
  })
})

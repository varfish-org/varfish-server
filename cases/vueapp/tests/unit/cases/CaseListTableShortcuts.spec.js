import CaseListTableShortcuts from '@cases/components/CaseListTableShortcuts.vue'
import { mount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

const makeWrapper = (props) => {
  return mount(CaseListTableShortcuts, {
    props,
  })
}

describe('CaseListTableShortcuts.vue', () => {
  test('test with small vars and svs', () => {
    const props = {
      params: {
        data: {
          num_small_vars: 42,
          num_svs: 40,
        },
      },
    }

    const wrapper = makeWrapper(props)

    expect(wrapper.findAll('button').length).toBe(3)
    expect(wrapper.findAll('button')[0].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[1].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[2].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
  })

  test('test with no small vars', () => {
    const props = {
      params: {
        data: {
          num_svs: 40,
        },
      },
    }
    const wrapper = makeWrapper(props)

    expect(wrapper.findAll('button').length).toBe(3)
    expect(wrapper.findAll('button')[0].wrapperElement.outerHTML).toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[1].wrapperElement.outerHTML).toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[2].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
  })

  test('test with no svs', () => {
    const props = {
      params: {
        data: {
          num_small_vars: 42,
        },
      },
    }
    const wrapper = makeWrapper(props)

    expect(wrapper.findAll('button').length).toBe(3)
    expect(wrapper.findAll('button')[0].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[1].wrapperElement.outerHTML).not.toMatch(
      /disabled/
    )
    expect(wrapper.findAll('button')[2].wrapperElement.outerHTML).toMatch(
      /disabled/
    )
  })
})

import CaseListProgressBar from '@cases/components/CaseListProgressBar.vue'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

const makeWrapper = (casesState = {}) => {
  return mount(CaseListProgressBar, {
    shallow: true,
    global: {
      plugins: [
        createTestingPinia({
          initialState: { cases: casesState },
          createSpy: vi.fn,
        }),
      ],
    },
  })
}

describe('CaseListProgressBar.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('render without cases', () => {
    const wrapper = makeWrapper({ cases: {}, caseList: [] })

    expect(wrapper.findAll('.progress-bar').length).toBe(1)
    expect(wrapper.findAll('.progress-bar')[0].html()).toMatch(
      /no samples in project/
    )
  })

  test('render with cases', () => {
    const case1 = { status: 'initial' }
    const wrapper = makeWrapper({ cases: { one: case1 }, caseList: [case1] })

    expect(wrapper.findAll('.progress-bar').length).toBe(1)
    expect(wrapper.findAll('.progress-bar')[0].html()).toMatch(
      /1\/1 \(100.00%\) initial/
    )
  })
})

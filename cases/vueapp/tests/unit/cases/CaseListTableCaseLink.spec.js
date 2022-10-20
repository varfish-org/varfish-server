import CaseListTableCaseLink from '@cases/components/CaseListTableCaseLink.vue'
import { mount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'
import { createRouterMock, injectRouterMock } from 'vue-router-mock'

const makeWrapper = (props) => {
  return mount(CaseListTableCaseLink, {
    props,
  })
}

describe('CaseListTableCaseLink.vue', () => {
  const router = createRouterMock({
    spy: {
      create: (fn) => vi.fn(fn),
      reset: (spy) => spy.mockReset(),
    },
  })

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    // Inject the mock router
    injectRouterMock(router)
  })

  const props = {
    params: {
      data: {
        name: 'name',
        sodar_uuid: 'fake-uuid',
      },
    },
  }

  test('test with display only', () => {
    const wrapper = makeWrapper(props)

    expect(wrapper.findAll('a').length).toBe(1)
    expect(wrapper.findAll('a')[0].wrapperElement.innerText).toMatch(
      RegExp(props.params.data.name)
    )
  })

  test('test with click', () => {
    const wrapper = makeWrapper(props)

    wrapper.findAll('a')[0].wrapperElement.click()

    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/detail/fake-uuid')
  })
})

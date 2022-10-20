import CaseDetailHeader from '@cases/components/CaseDetailHeader.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'
import { createRouterMock, injectRouterMock } from 'vue-router-mock'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

describe('CaseDetailHeader.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailHeader)

    expect(wrapper.html()).matches(/<small>NO CASE<\/small>/)
  })

  test('test with case detail store data', async () => {
    const wrapper = makeWrapper(
      CaseDetailHeader,
      {},
      { caseObj: caseDetailsStoreData.caseObj }
    )

    expect(wrapper.html()).matches(/<small class="text-muted">NA12878<\/small>/)
  })

  test('test click back to project', async () => {
    const router = createRouterMock({
      spy: {
        create: (fn) => vi.fn(fn),
        reset: (spy) => spy.mockReset(),
      },
    })
    injectRouterMock(router)

    const wrapper = makeWrapper(
      CaseDetailHeader,
      {},
      { caseObj: caseDetailsStoreData.caseObj }
    )

    wrapper.findAll('a')[1].wrapperElement.click()

    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/')
  })
})

// Work around issue with igv.js accessing document.head.children when included.
document.head.appendChild(document.createElement('title'))

import CaseDetailContent from '@/cases/components/CaseDetail/Content.vue'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'
import { createRouterMock, injectRouterMock } from 'vue-router-mock'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailContent.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  const router = createRouterMock({
    spy: {
      create: (fn) => vi.fn(fn),
      reset: (spy) => spy.mockReset(),
    },
  })

  beforeEach(() => {
    router.reset()
    // Inject the mock router
    injectRouterMock(router)
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailContent)

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.findAll('a.nav-link').length).toBe(3)
  })

  test('test with some data', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.findAll('a.nav-link').length).toBe(3)
  })

  test('test click quality control', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[1].trigger('click')

    expect(router.push).toHaveBeenCalledTimes(1)
    expect(router.push).toHaveBeenCalledWith({
      name: 'case-detail-qc',
      params: {
        case: caseDetailsStoreData.caseObj.sodar_uuid,
      },
    })

    // expect(wrapper.html()).not.matches(/<pane-case-stub/)
    // expect(wrapper.html()).matches(/<pane-qc-stub/)
    // expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
  })

  test('test click quality control, then overview', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[1].trigger('click')
    await wrapper.findAll('a.nav-link')[0].trigger('click')

    expect(router.push).toHaveBeenCalledTimes(2)
    expect(router.push).toHaveBeenCalledWith({
      name: 'case-detail-qc',
      params: {
        case: caseDetailsStoreData.caseObj.sodar_uuid,
      },
    })
    expect(router.push).toHaveBeenCalledWith({
      name: 'case-detail-overview',
      params: {
        case: caseDetailsStoreData.caseObj.sodar_uuid,
      },
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
  })

  test('test click variant annotation', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[2].trigger('click')

    expect(router.push).toHaveBeenCalledTimes(1)
    expect(router.push).toHaveBeenCalledWith({
      name: 'case-detail-annotation',
      params: {
        case: caseDetailsStoreData.caseObj.sodar_uuid,
      },
    })

    // expect(wrapper.html()).not.matches(/<pane-case-stub/)
    // expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    // expect(wrapper.html()).matches(/<pane-annotations-stub/)
  })
})

import casesApi from '@cases/api/cases.js'
import CaseDetail from '@cases/components/CaseDetail.vue'
import { flushPromises } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'
import { createRouterMock, getRouter, injectRouterMock } from 'vue-router-mock'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import casesStoreData from '../../data/casesStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

// Mock out the cases API
vi.mock('@cases/api/cases.js')

describe('CaseDetail.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  beforeEach(() => {
    // Mock out jquery dollar function for showing modals.
    const valResult = vi.fn()
    valResult.change = vi.fn()
    const mockJQueryResult = vi.fn()
    mockJQueryResult.prop = vi.fn()
    mockJQueryResult.val = vi.fn()
    mockJQueryResult.val.mockReturnValue(valResult)
    mockJQueryResult.change = vi.fn()
    const mockJQuery = vi.fn(function () {
      return this
    })
    mockJQuery.mockReturnValue(mockJQueryResult)
    global.$ = mockJQuery

    // Setup and inject mock router.
    const router = createRouterMock({
      spy: {
        create: (fn) => vi.fn(fn),
        reset: (spy) => spy.mockReset(),
      },
    })
    injectRouterMock(router)
  })

  const documentHtml = `
    <div>
      <input type="checkbox" id="vueapp-filtration-inline-help" checked="" />
      <input type="hidden" id="vueapp-filtration-complexity-mode" value="basic" />
      <div id="sodar-ss-app-context" app-context="{appContextStr}" />
      <div id="app"></div>
    </div>
  `

  test('smoke test with empty data', async () => {
    const wrapper = makeWrapper(
      CaseDetail,
      undefined,
      undefined,
      undefined,
      documentHtml
    )

    expect(wrapper.html()).matches(/<case-detail-header-stub>/)
    expect(wrapper.html()).matches(/<case-detail-content-stub>/)
  })

  test('smoke test with case detail store data', async () => {
    // mock out clinvarApi.listCases for casesStore.initialize
    casesApi.fetchCaseComments.mockResolvedValue([])
    casesApi.fetchVarAnnos.mockResolvedValue([])
    casesApi.fetchSvAnnos.mockResolvedValue([])
    casesApi.fetchCaseGeneAnnotation.mockResolvedValue([])

    // setup mock router's params
    const router = getRouter()
    router.setParams({ case: caseDetailsStoreData.caseObj.sodar_uuid })

    // mount components
    const wrapper = makeWrapper(
      CaseDetail,
      {
        cases: casesStoreData,
        caseDetails: caseDetailsStoreData,
      },
      undefined,
      undefined,
      documentHtml
    )

    flushPromises()

    expect(wrapper.html()).matches(
      /<case-detail-header-stub caseobj="\[object Object\]"/
    )
    expect(wrapper.html()).matches(/<case-detail-content-stub>/)
  })
})

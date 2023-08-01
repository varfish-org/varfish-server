// Work around issue with igv.js accessing document.head.children when included.
document.head.appendChild(document.createElement('title'))

import CaseDetailContent from '@cases/components/CaseDetail/Content.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../../data/caseDetailsStoreData.json'
import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailContent.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailContent)

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)
    expect(wrapper.findAll('a.nav-link').length).toBe(4)
  })

  test('test with some data', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)
    expect(wrapper.findAll('a.nav-link').length).toBe(4)
  })

  test('test click quality control', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(4)
    await wrapper.findAll('a.nav-link')[1].trigger('click')

    expect(wrapper.html()).not.matches(/<pane-case-stub/)
    expect(wrapper.html()).matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)
  })

  test('test click quality control, then overview', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(4)
    await wrapper.findAll('a.nav-link')[1].trigger('click')
    await wrapper.findAll('a.nav-link')[0].trigger('click')

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)
  })

  test('test click variant annotation', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(4)
    await wrapper.findAll('a.nav-link')[2].trigger('click')

    expect(wrapper.html()).not.matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)
  })

  test('test click genome browser', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).not.matches(/<genome-browser-stub/)

    expect(wrapper.findAll('a.nav-link').length).toBe(4)
    await wrapper.findAll('a.nav-link')[3].trigger('click')

    expect(wrapper.html()).not.matches(/<pane-case-stub/)
    expect(wrapper.html()).not.matches(/<pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<pane-annotations-stub/)
    expect(wrapper.html()).matches(/<genome-browser-stub/)
  })
})

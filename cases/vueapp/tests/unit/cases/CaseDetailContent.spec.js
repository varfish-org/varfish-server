import CaseDetailContent from '@cases/components/CaseDetailContent.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import caseDetailsStoreData from '../../data/caseDetailsStoreData.json'
import { makeWrapper } from './CaseDetail.common.js'

describe('CaseDetailContent.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with empty data', async () => {
    const wrapper = makeWrapper(CaseDetailContent)

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/CaseVariantAnnotation/)
    expect(wrapper.findAll('a.nav-link').length).toBe(3)
  })

  test('test with some data', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/CaseVariantAnnotation/)
    expect(wrapper.findAll('a.nav-link').length).toBe(3)
  })

  test('test click quality control', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/CaseVariantAnnotation/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[1].trigger('click')

    expect(wrapper.html()).not.matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-annotations-stub/)
  })

  test('test click quality control, then overview', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/CaseVariantAnnotation/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[1].trigger('click')
    await wrapper.findAll('a.nav-link')[0].trigger('click')

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-annotations-stub/)
  })

  test('test click variant annotation', async () => {
    const wrapper = makeWrapper(CaseDetailContent, {
      caseDetails: caseDetailsStoreData,
    })

    expect(wrapper.html()).matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).not.matches(/CaseVariantAnnotation/)

    expect(wrapper.findAll('a.nav-link').length).toBe(3)
    await wrapper.findAll('a.nav-link')[2].trigger('click')

    expect(wrapper.html()).not.matches(/<case-detail-pane-case-stub/)
    expect(wrapper.html()).not.matches(/<case-detail-pane-qc-stub/)
    expect(wrapper.html()).matches(/<case-detail-pane-annotations-stub/)
  })
})

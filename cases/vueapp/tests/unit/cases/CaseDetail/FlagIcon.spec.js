import CaseDetailFlagIcon from '@cases/components/CaseDetail/FlagIcon.vue'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import { makeWrapper } from '../CaseDetailApp.common'

describe('CaseDetailFlagIcon.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })

  test('test with flag=flag_bookmarked', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_bookmarked' },
    )

    expect(wrapper.html()).matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=flag_for_validation', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_for_validation' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=flag_candidate', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_candidate' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=flag_final_causative', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_final_causative' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=flag_no_disease_association', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_no_disease_association' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=XXX', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_segregates' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=flag_doesnt_segregate', async () => {
    const wrapper = makeWrapper(
      CaseDetailFlagIcon,
      {},
      { flag: 'flag_doesnt_segregate' },
    )

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).not.matches(/NO FLAG/)
  })

  test('test with flag=null', async () => {
    const wrapper = makeWrapper(CaseDetailFlagIcon, {}, { flag: null })

    expect(wrapper.html()).not.matches(/<fa-solid-star-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flask-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-heart-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-flag-checkered-stub>/)
    expect(wrapper.html()).not.matches(/<cil-link-broken-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-up-stub>/)
    expect(wrapper.html()).not.matches(/<fa-solid-thumbs-down-stub>/)
    expect(wrapper.html()).matches(/NO FLAG/)
  })
})

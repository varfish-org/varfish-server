import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { SvClient } from '@/svs/api/strucvarClient'

import { useSvCommentsStore } from './svComments'

vi.mock('@/svs/api/strucvarClient')

/** Promise that is resolved from the outside, to control response order. */
const deferred = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((res) => {
    resolve = res
  })
  return { promise, resolve }
}

const strucvarA: Strucvar = {
  svType: 'DEL',
  genomeBuild: 'grch37',
  chrom: '1',
  start: 100,
  stop: 1000,
  userRepr: 'DEL-grch37-1-100-1000',
}
const strucvarB: Strucvar = {
  svType: 'DUP',
  genomeBuild: 'grch37',
  chrom: '2',
  start: 200,
  stop: 2000,
  userRepr: 'DUP-grch37-2-200-2000',
}
const commentA = { sodar_uuid: 'comment-a', text: 'about A' }
const commentB = { sodar_uuid: 'comment-b', text: 'about B' }

describe('useSvCommentsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(SvClient).mockReset()
  })

  /** Return store for case "case-uuid" in project "project-uuid". */
  const setupStore = () => {
    const store = useSvCommentsStore()
    store.projectUuid = 'project-uuid'
    store.caseUuid = 'case-uuid'
    return store
  }

  test('retrieveComments keeps the comments of the most recently requested SV', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listComment = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(() => ({ listComment }) as any)
    const store = setupStore()

    const retrievalA = store.retrieveComments(strucvarA, 'case-uuid')
    const retrievalB = store.retrieveComments(strucvarB, 'case-uuid')
    responseB.resolve([commentB])
    await retrievalB
    responseA.resolve([commentA])
    await retrievalA

    expect(store.sv).toEqual(strucvarB)
    expect(store.comments).toEqual([commentB])
  })

  test('retrieveComments clears the comments of the previous SV while loading', async () => {
    const responseB = deferred<any[]>()
    const listComment = vi
      .fn()
      .mockResolvedValueOnce([commentA])
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(() => ({ listComment }) as any)
    const store = setupStore()
    await store.retrieveComments(strucvarA, 'case-uuid')

    const retrievalB = store.retrieveComments(strucvarB, 'case-uuid')

    expect(store.sv).toEqual(strucvarB)
    expect(store.comments).toBeNull()
    responseB.resolve([commentB])
    await retrievalB
  })

  test('retrieveProjectWideVariantComments keeps the comments of the most recently requested SV', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listProjectComment = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(
      () => ({ listProjectComment }) as any,
    )
    const store = setupStore()

    const retrievalA = store.retrieveProjectWideVariantComments(strucvarA)
    const retrievalB = store.retrieveProjectWideVariantComments(strucvarB)
    responseB.resolve([commentB])
    await retrievalB
    responseA.resolve([commentA])
    await retrievalA

    expect(store.projectWideVariantComments).toEqual([commentB])
  })
})

import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'

import { useVariantCommentsStore } from './variantComments'

vi.mock('@/variants/api/variantClient')

/** Promise that is resolved from the outside, to control response order. */
const deferred = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((res) => {
    resolve = res
  })
  return { promise, resolve }
}

const seqvarA: Seqvar = {
  genomeBuild: 'grch37',
  chrom: '1',
  pos: 100,
  del: 'A',
  ins: 'G',
  userRepr: 'grch37-1-100-A-G',
}
const seqvarB: Seqvar = {
  genomeBuild: 'grch37',
  chrom: '2',
  pos: 200,
  del: 'C',
  ins: 'T',
  userRepr: 'grch37-2-200-C-T',
}
const commentA = { sodar_uuid: 'comment-a', text: 'about A' }
const commentB = { sodar_uuid: 'comment-b', text: 'about B' }

describe('useVariantCommentsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(VariantClient).mockReset()
  })

  /** Return store for case "case-uuid" in project "project-uuid". */
  const setupStore = () => {
    const store = useVariantCommentsStore()
    store.projectUuid = 'project-uuid'
    store.caseUuid = 'case-uuid'
    return store
  }

  test('retrieveComments keeps the comments of the most recently requested variant', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listComment = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(() => ({ listComment }) as any)
    const store = setupStore()

    const retrievalA = store.retrieveComments(seqvarA)
    const retrievalB = store.retrieveComments(seqvarB)
    responseB.resolve([commentB])
    await retrievalB
    responseA.resolve([commentA])
    await retrievalA

    expect(store.seqvar).toEqual(seqvarB)
    expect(store.comments).toEqual([commentB])
  })

  test('retrieveComments clears the comments of the previous variant while loading', async () => {
    const responseB = deferred<any[]>()
    const listComment = vi
      .fn()
      .mockResolvedValueOnce([commentA])
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(() => ({ listComment }) as any)
    const store = setupStore()
    await store.retrieveComments(seqvarA)

    const retrievalB = store.retrieveComments(seqvarB)

    expect(store.seqvar).toEqual(seqvarB)
    expect(store.comments).toBeNull()
    responseB.resolve([commentB])
    await retrievalB
  })

  test('retrieveProjectWideVariantComments keeps the comments of the most recently requested variant', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listProjectComment = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(
      () => ({ listProjectComment }) as any,
    )
    const store = setupStore()

    const retrievalA = store.retrieveProjectWideVariantComments(seqvarA)
    const retrievalB = store.retrieveProjectWideVariantComments(seqvarB)
    responseB.resolve([commentB])
    await retrievalB
    responseA.resolve([commentA])
    await retrievalA

    expect(store.projectWideVariantComments).toEqual([commentB])
  })

  test('createComment does not add its comment to the comments of another variant requested meanwhile', async () => {
    const creation = deferred<any>()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listComment: async (_caseUuid: string, seqvar: Seqvar) =>
            seqvar === seqvarA ? [] : [commentB],
          createComment: vi.fn().mockReturnValue(creation.promise),
        }) as any,
    )
    const store = setupStore()
    await store.retrieveComments(seqvarA)

    const creatingA = store.createComment(seqvarA, 'about A', 'result-row-uuid')
    await store.retrieveComments(seqvarB)
    creation.resolve(commentA)
    await creatingA

    expect(store.comments).toEqual([commentB])
  })
})

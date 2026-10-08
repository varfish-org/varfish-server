import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'

import { useVariantFlagsStore } from './variantFlags'

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
const flagsA = { sodar_uuid: 'flags-a' }
const flagsB = { sodar_uuid: 'flags-b' }

describe('useVariantFlagsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(VariantClient).mockReset()
  })

  /** Return store for case "case-uuid" in project "project-uuid". */
  const setupStore = () => {
    const store = useVariantFlagsStore()
    store.projectUuid = 'project-uuid'
    store.caseUuid = 'case-uuid'
    return store
  }

  test('retrieveFlags keeps the flags of the most recently requested variant', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listFlags = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(() => ({ listFlags }) as any)
    const store = setupStore()

    const retrievalA = store.retrieveFlags(seqvarA, 'case-uuid')
    const retrievalB = store.retrieveFlags(seqvarB, 'case-uuid')
    responseB.resolve([flagsB])
    await retrievalB
    responseA.resolve([flagsA])
    await retrievalA

    expect(store.seqvar).toEqual(seqvarB)
    expect(store.flags).toEqual(flagsB)
  })

  test('retrieveFlags clears the flags of the previous variant while loading', async () => {
    const responseB = deferred<any[]>()
    const listFlags = vi
      .fn()
      .mockResolvedValueOnce([flagsA])
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(() => ({ listFlags }) as any)
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    const retrievalB = store.retrieveFlags(seqvarB, 'case-uuid')

    expect(store.seqvar).toEqual(seqvarB)
    expect(store.flags).toBeNull()
    responseB.resolve([flagsB])
    await retrievalB
  })

  test('retrieveProjectWideVariantFlags keeps the flags of the most recently requested variant', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listProjectFlags = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(VariantClient).mockImplementation(
      () => ({ listProjectFlags }) as any,
    )
    const store = setupStore()

    const retrievalA = store.retrieveProjectWideVariantFlags(seqvarA)
    const retrievalB = store.retrieveProjectWideVariantFlags(seqvarB)
    responseB.resolve([flagsB])
    await retrievalB
    responseA.resolve([flagsA])
    await retrievalA

    expect(store.projectWideVariantFlags).toEqual([flagsB])
  })

  test('updateFlags refuses to write when the store holds another variant', async () => {
    const updateFlags = vi.fn()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          updateFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    await expect(
      store.updateFlags(seqvarB, { flag_bookmarked: true }),
    ).rejects.toThrow()
    expect(updateFlags).not.toHaveBeenCalled()
  })

  test('deleteFlags refuses to write when the store holds another variant', async () => {
    const deleteFlags = vi.fn()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          deleteFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    await expect(store.deleteFlags(seqvarB)).rejects.toThrow()
    expect(deleteFlags).not.toHaveBeenCalled()
  })

  test('updateFlags writes the flags of the variant being displayed', async () => {
    const updateFlags = vi
      .fn()
      .mockResolvedValue({ ...flagsA, flag_bookmarked: true })
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          updateFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    await store.updateFlags(seqvarA, { flag_bookmarked: true })

    expect(updateFlags).toHaveBeenCalledWith('flags-a', expect.anything())
    expect(store.flags).toEqual({ ...flagsA, flag_bookmarked: true })
  })

  test('createFlags does not show its result after another variant was requested', async () => {
    const creation = deferred<any>()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, seqvar: Seqvar) =>
            seqvar === seqvarA ? [] : [flagsB],
          createFlags: vi.fn().mockReturnValue(creation.promise),
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    const creatingA = store.createFlags(seqvarA, {}, 'result-row-uuid')
    await store.retrieveFlags(seqvarB, 'case-uuid')
    creation.resolve(flagsA)
    await creatingA

    expect(store.flags).toEqual(flagsB)
  })

  test('updateFlags does not show its result after another variant was requested', async () => {
    const update = deferred<any>()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, seqvar: Seqvar) =>
            seqvar === seqvarA ? [flagsA] : [flagsB],
          updateFlags: vi.fn().mockReturnValue(update.promise),
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(seqvarA, 'case-uuid')

    const updatingA = store.updateFlags(seqvarA, { flag_bookmarked: true })
    await store.retrieveFlags(seqvarB, 'case-uuid')
    update.resolve({ ...flagsA, flag_bookmarked: true })
    await updatingA

    expect(store.flags).toEqual(flagsB)
  })

  test('deleteFlags does not clear the flags of another variant requested meanwhile', async () => {
    const deletion = deferred<void>()
    vi.mocked(VariantClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, seqvar: Seqvar) =>
            seqvar === seqvarA ? [flagsA] : [flagsB],
          deleteFlags: vi.fn().mockReturnValue(deletion.promise),
        }) as any,
    )
    const store = setupStore()
    store.caseFlags.set('flags-a', flagsA)
    store.caseFlags.set('flags-b', flagsB)
    await store.retrieveFlags(seqvarA, 'case-uuid')

    const deletingA = store.deleteFlags(seqvarA)
    await store.retrieveFlags(seqvarB, 'case-uuid')
    deletion.resolve()
    await deletingA

    expect(store.flags).toEqual(flagsB)
    expect([...store.caseFlags.keys()]).toEqual(['flags-b'])
  })
})

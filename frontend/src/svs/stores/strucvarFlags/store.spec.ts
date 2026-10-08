import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { SvClient } from '@/svs/api/strucvarClient'

import { useSvFlagsStore } from './store'

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
const flagsA = { sodar_uuid: 'flags-a' }
const flagsB = { sodar_uuid: 'flags-b' }

describe('useSvFlagsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(SvClient).mockReset()
  })

  /** Return store for case "case-uuid" in project "project-uuid". */
  const setupStore = () => {
    const store = useSvFlagsStore()
    store.projectUuid = 'project-uuid'
    store.caseUuid = 'case-uuid'
    return store
  }

  test('retrieveFlags keeps the flags of the most recently requested SV', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listFlags = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(() => ({ listFlags }) as any)
    const store = setupStore()

    const retrievalA = store.retrieveFlags(strucvarA, 'case-uuid')
    const retrievalB = store.retrieveFlags(strucvarB, 'case-uuid')
    responseB.resolve([flagsB])
    await retrievalB
    responseA.resolve([flagsA])
    await retrievalA

    expect(store.sv).toEqual(strucvarB)
    expect(store.flags).toEqual(flagsB)
  })

  test('retrieveFlags clears the flags of the previous SV while loading', async () => {
    const responseB = deferred<any[]>()
    const listFlags = vi
      .fn()
      .mockResolvedValueOnce([flagsA])
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(() => ({ listFlags }) as any)
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    const retrievalB = store.retrieveFlags(strucvarB, 'case-uuid')

    expect(store.sv).toEqual(strucvarB)
    expect(store.flags).toBeNull()
    responseB.resolve([flagsB])
    await retrievalB
  })

  test('retrieveProjectWideVariantFlags keeps the flags of the most recently requested SV', async () => {
    const responseA = deferred<any[]>()
    const responseB = deferred<any[]>()
    const listProjectFlags = vi
      .fn()
      .mockReturnValueOnce(responseA.promise)
      .mockReturnValueOnce(responseB.promise)
    vi.mocked(SvClient).mockImplementation(() => ({ listProjectFlags }) as any)
    const store = setupStore()

    const retrievalA = store.retrieveProjectWideVariantFlags(strucvarA)
    const retrievalB = store.retrieveProjectWideVariantFlags(strucvarB)
    responseB.resolve([flagsB])
    await retrievalB
    responseA.resolve([flagsA])
    await retrievalA

    expect(store.projectWideVariantFlags).toEqual([flagsB])
  })

  test('updateFlags refuses to write when the store holds another SV', async () => {
    const updateFlags = vi.fn()
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          updateFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    await expect(
      store.updateFlags(strucvarB, { flag_bookmarked: true }),
    ).rejects.toThrow()
    expect(updateFlags).not.toHaveBeenCalled()
  })

  test('deleteFlags refuses to write when the store holds another SV', async () => {
    const deleteFlags = vi.fn()
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          deleteFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    await expect(store.deleteFlags(strucvarB)).rejects.toThrow()
    expect(deleteFlags).not.toHaveBeenCalled()
  })

  test('updateFlags writes the flags of the SV being displayed', async () => {
    const updateFlags = vi
      .fn()
      .mockResolvedValue({ ...flagsA, flag_bookmarked: true })
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: vi.fn().mockResolvedValue([flagsA]),
          updateFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    await store.updateFlags(strucvarA, { flag_bookmarked: true })

    expect(updateFlags).toHaveBeenCalledWith('flags-a', expect.anything())
    expect(store.flags).toEqual({ ...flagsA, flag_bookmarked: true })
  })
})

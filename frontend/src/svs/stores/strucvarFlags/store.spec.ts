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

  test('createFlags does not show its result after another SV was requested', async () => {
    const creation = deferred<any>()
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [] : [flagsB],
          createFlags: vi.fn().mockReturnValue(creation.promise),
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    const creatingA = store.createFlags(strucvarA, {}, 'result-row-uuid')
    await store.retrieveFlags(strucvarB, 'case-uuid')
    creation.resolve(flagsA)
    await creatingA

    expect(store.flags).toEqual(flagsB)
  })

  test('updateFlags does not show its result after another SV was requested', async () => {
    const update = deferred<any>()
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [flagsA] : [flagsB],
          updateFlags: vi.fn().mockReturnValue(update.promise),
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    const updatingA = store.updateFlags(strucvarA, { flag_bookmarked: true })
    await store.retrieveFlags(strucvarB, 'case-uuid')
    update.resolve({ ...flagsA, flag_bookmarked: true })
    await updatingA

    expect(store.flags).toEqual(flagsB)
  })

  test('deleteFlags does not clear the flags of another SV requested meanwhile', async () => {
    const deletion = deferred<void>()
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [flagsA] : [flagsB],
          deleteFlags: vi.fn().mockReturnValue(deletion.promise),
        }) as any,
    )
    const store = setupStore()
    store.caseFlags.set('flags-a', flagsA)
    store.caseFlags.set('flags-b', flagsB)
    await store.retrieveFlags(strucvarA, 'case-uuid')

    const deletingA = store.deleteFlags(strucvarA)
    await store.retrieveFlags(strucvarB, 'case-uuid')
    deletion.resolve()
    await deletingA

    expect(store.flags).toEqual(flagsB)
    expect([...store.caseFlags.keys()]).toEqual(['flags-b'])
  })

  test('flagAsArtifact creates negative flags for an SV other than the current one', async () => {
    const createFlags = vi.fn().mockResolvedValue({ sodar_uuid: 'flags-b' })
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [flagsA] : [],
          createFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    await store.flagAsArtifact(strucvarB, 'result-row-uuid')

    expect(createFlags).toHaveBeenCalledWith(
      'case-uuid',
      strucvarB,
      expect.objectContaining({
        release: 'GRCh37',
        chromosome: '2',
        start: 200,
        end: 2000,
        sv_type: 'DUP',
        sodar_uuid: 'result-row-uuid',
        flag_summary: 'negative',
        flag_visual: 'negative',
      }),
    )
  })

  test('flagAsArtifact sets existing flags of an SV other than the current one to negative', async () => {
    const updateFlags = vi.fn().mockResolvedValue(flagsB)
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [flagsA] : [flagsB],
          updateFlags,
        }) as any,
    )
    const store = setupStore()
    await store.retrieveFlags(strucvarA, 'case-uuid')

    await store.flagAsArtifact(strucvarB, 'result-row-uuid')

    expect(updateFlags).toHaveBeenCalledWith(
      'flags-b',
      expect.objectContaining({
        flag_summary: 'negative',
        flag_visual: 'negative',
      }),
    )
  })

  test('flagAsArtifact flags each of two SVs flagged in quick succession', async () => {
    const createFlags = vi.fn().mockResolvedValue({ sodar_uuid: 'flags-b' })
    const updateFlags = vi.fn().mockResolvedValue(flagsA)
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) =>
            strucvar === strucvarA ? [flagsA] : [],
          createFlags,
          updateFlags,
        }) as any,
    )
    const store = setupStore()

    await Promise.all([
      store.flagAsArtifact(strucvarA, 'result-row-a'),
      store.flagAsArtifact(strucvarB, 'result-row-b'),
    ])

    expect(updateFlags).toHaveBeenCalledTimes(1)
    expect(updateFlags).toHaveBeenCalledWith('flags-a', expect.anything())
    expect(createFlags).toHaveBeenCalledTimes(1)
    expect(createFlags).toHaveBeenCalledWith(
      'case-uuid',
      strucvarB,
      expect.anything(),
    )
  })

  test('flagAsArtifact still flags an SV after flagging the previous one failed', async () => {
    const createFlags = vi.fn().mockResolvedValue({ sodar_uuid: 'flags-b' })
    vi.mocked(SvClient).mockImplementation(
      () =>
        ({
          listFlags: async (_caseUuid: string, strucvar: Strucvar) => {
            if (strucvar === strucvarA) {
              throw new Error('server error')
            }
            return []
          },
          createFlags,
        }) as any,
    )
    const store = setupStore()

    const flaggingA = store.flagAsArtifact(strucvarA, 'result-row-a')
    const flaggingB = store.flagAsArtifact(strucvarB, 'result-row-b')

    await expect(flaggingA).rejects.toThrow('server error')
    await flaggingB
    expect(createFlags).toHaveBeenCalledWith(
      'case-uuid',
      strucvarB,
      expect.anything(),
    )
  })
})

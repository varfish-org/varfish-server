import {
  BreakendStrucvarImpl,
  InsertionStrucvarImpl,
  LinearStrucvarImpl,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'

import { jumpToLocus } from './lib'

/** Return the locus that `jumpToLocus` requested from IGV. */
const requestedLocus = (fetchMock: ReturnType<typeof vi.fn>): string => {
  const url = new URL(fetchMock.mock.calls[0][0] as string)
  return url.searchParams.get('locus') as string
}

describe('jumpToLocus', () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue(new Response())
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('does not call IGV without a variant', async () => {
    await jumpToLocus(undefined)

    expect(fetchMock).not.toHaveBeenCalled()
  })

  test('uses the full span for a linear SV', async () => {
    await jumpToLocus(new LinearStrucvarImpl('DEL', 'grch37', '17', 100, 200))

    expect(requestedLocus(fetchMock)).toBe('17:100-200')
  })

  test('uses a one-base window for an insertion', async () => {
    await jumpToLocus(new InsertionStrucvarImpl('grch37', '17', 100))

    expect(requestedLocus(fetchMock)).toBe('17:100-101')
  })

  // A breakend has two breakpoints, potentially on different chromosomes.  Sending both as a
  // space-delimited locus list makes IGV open them side by side in its multi-locus view.
  test('uses both breakends for a BND', async () => {
    await jumpToLocus(new BreakendStrucvarImpl('grch37', '17', '22', 100, 200))

    expect(requestedLocus(fetchMock)).toBe('17:100-101 22:200-201')
  })

  test('normalizes the mitochondrial chromosome on the partner breakend', async () => {
    await jumpToLocus(new BreakendStrucvarImpl('grch37', '17', 'MT', 100, 200))

    expect(requestedLocus(fetchMock)).toBe('17:100-101 chrM:200-201')
  })

  // Regression: the mitochondrial chromosome reaches us as `MT` on GRCh37 and as
  // `chrM`/`chrMT` on GRCh38, and the breakend path strips the `chr` prefix.  IGV
  // only understands `chrM`.
  test.each(['MT', 'M', 'chrMT', 'chrM'])(
    'normalizes the mitochondrial chromosome %s to chrM',
    async (chrom) => {
      await jumpToLocus(
        new LinearStrucvarImpl('DEL', 'grch37', chrom, 100, 200),
      )

      expect(requestedLocus(fetchMock)).toBe('chrM:100-200')
    },
  )
})

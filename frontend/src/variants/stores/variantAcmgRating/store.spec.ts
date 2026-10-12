import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { VariantClient } from '@/variants/api/variantClient'

import { useVariantAcmgRatingStore } from './store'

vi.mock('@/variants/api/variantClient', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/variants/api/variantClient')>()),
  VariantClient: vi.fn(),
}))

const acmgRating = {
  sodarUuid: 'acmg-rating-uuid',
  genomeBuild: 'grch37',
  chrom: '1',
  pos: 100,
  del: 'A',
  ins: 'G',
  ps1: 2,
} as any

describe('useVariantAcmgRatingStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(VariantClient).mockReset()
  })

  test('updateAcmgRating sends the result row the variant was annotated from', async () => {
    const updateAcmgRating = vi.fn().mockResolvedValue(acmgRating)
    vi.mocked(VariantClient).mockImplementation(
      () => ({ updateAcmgRating }) as any,
    )
    const store = useVariantAcmgRatingStore()
    store.acmgRating = acmgRating

    await store.updateAcmgRating(acmgRating, 'result-row-uuid')

    expect(updateAcmgRating).toHaveBeenCalledWith(
      'acmg-rating-uuid',
      acmgRating,
      'result-row-uuid',
    )
  })
})

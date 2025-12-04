import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('useVariantQueryStore', () => {
  let variantQueryStore

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()

    setActivePinia(createTestingPinia({ createSpy: vi.fn }))
    variantQueryStore = useVariantQueryStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('smoke test', async () => {
    expect(true).not.toBe(false)
    const _ = variantQueryStore
  })

  test('lastSubmittedQuerySettings is initially null', () => {
    expect(variantQueryStore.lastSubmittedQuerySettings).toBeNull()
  })

  test('lastSubmittedQuerySettings can be set and retrieved', () => {
    const testSettings = {
      database: 'refseq',
      var_type_snv: true,
      gnomad_genomes_frequency: 0.002,
    }

    variantQueryStore.lastSubmittedQuerySettings = testSettings

    expect(variantQueryStore.lastSubmittedQuerySettings).not.toBeNull()
    expect(variantQueryStore.lastSubmittedQuerySettings.database).toBe('refseq')
    expect(variantQueryStore.lastSubmittedQuerySettings.var_type_snv).toBe(true)
    expect(
      variantQueryStore.lastSubmittedQuerySettings.gnomad_genomes_frequency,
    ).toBe(0.002)
  })

  test('lastSubmittedQuerySettings persists after querySettings changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_indel: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_indel: true,
    }

    // Change current settings
    variantQueryStore.querySettings.database = 'ensembl'
    variantQueryStore.querySettings.var_type_indel = false

    // lastSubmittedQuerySettings should remain unchanged
    expect(variantQueryStore.lastSubmittedQuerySettings.database).toBe('refseq')
    expect(variantQueryStore.lastSubmittedQuerySettings.var_type_indel).toBe(
      true,
    )
  })

  test('lastSubmittedQuerySettings is cleared on $reset', () => {
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      require_in_clinvar: false,
    }

    variantQueryStore.$reset()

    expect(variantQueryStore.lastSubmittedQuerySettings).toBeNull()
  })

  test('comparing querySettings with lastSubmittedQuerySettings detects changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gnomad_exomes_frequency: 0.002,
      exac_frequency: 0.002,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gnomad_exomes_frequency: 0.002,
      exac_frequency: 0.002,
    }

    // No changes - JSON stringify should match
    expect(
      JSON.stringify(variantQueryStore.querySettings) ===
        JSON.stringify(variantQueryStore.lastSubmittedQuerySettings),
    ).toBe(true)

    // Make a change
    variantQueryStore.querySettings.database = 'ensembl'

    // Should detect changes
    expect(
      JSON.stringify(variantQueryStore.querySettings) ===
        JSON.stringify(variantQueryStore.lastSubmittedQuerySettings),
    ).toBe(false)
  })

  test('deep object changes are detected', () => {
    variantQueryStore.querySettings = {
      quality: {
        'NA12878-N1-DNA1-WES1': {
          dp_het: 10,
          dp_hom: 5,
        },
      },
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      quality: {
        'NA12878-N1-DNA1-WES1': {
          dp_het: 10,
          dp_hom: 5,
        },
      },
    }

    // No changes initially
    expect(
      JSON.stringify(variantQueryStore.querySettings) ===
        JSON.stringify(variantQueryStore.lastSubmittedQuerySettings),
    ).toBe(true)

    // Deep change
    variantQueryStore.querySettings.quality['NA12878-N1-DNA1-WES1'].dp_het = 15

    // Should detect changes
    expect(
      JSON.stringify(variantQueryStore.querySettings) ===
        JSON.stringify(variantQueryStore.lastSubmittedQuerySettings),
    ).toBe(false)
  })
})

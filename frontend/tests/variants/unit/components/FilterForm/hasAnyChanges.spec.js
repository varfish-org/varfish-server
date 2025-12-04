import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { computed } from 'vue'

import { useVariantQueryStore } from '@/variants/stores/variantQuery'

describe('FilterForm - hasAnyChanges computed logic', () => {
  let variantQueryStore

  beforeEach(() => {
    setActivePinia(createTestingPinia({ createSpy: vi.fn }))
    variantQueryStore = useVariantQueryStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // This replicates the hasAnyChanges logic from FilterForm.vue
  const createHasAnyChanges = () => {
    return computed(() => {
      if (
        !variantQueryStore.lastSubmittedQuerySettings ||
        !variantQueryStore.querySettings
      ) {
        return false
      }
      const currentSettings = variantQueryStore.querySettings
      const lastSettings = variantQueryStore.lastSubmittedQuerySettings

      return JSON.stringify(currentSettings) !== JSON.stringify(lastSettings)
    })
  }

  test('hasAnyChanges is false when lastSubmittedQuerySettings is null', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = null

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(false)
  })

  test('hasAnyChanges is false when querySettings is null', () => {
    variantQueryStore.querySettings = null
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(false)
  })

  test('hasAnyChanges is false when both settings are null', () => {
    variantQueryStore.querySettings = null
    variantQueryStore.lastSubmittedQuerySettings = null

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(false)
  })

  test('hasAnyChanges is false when settings are identical', () => {
    const settings = {
      database: 'refseq',
      var_type_snv: true,
      var_type_mnv: true,
      var_type_indel: true,
      gnomad_genomes_frequency: 0.002,
    }

    variantQueryStore.querySettings = { ...settings }
    variantQueryStore.lastSubmittedQuerySettings = { ...settings }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(false)
  })

  test('hasAnyChanges is true when database changes', () => {
    variantQueryStore.querySettings = {
      database: 'ensembl',
      var_type_snv: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when boolean value changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: false,
      var_type_mnv: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
      var_type_mnv: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when number value changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: 0.01,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: 0.002,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when null changes to value', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: 0.002,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: null,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when value changes to null', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: null,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gnomad_genomes_frequency: 0.002,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when object property changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      genotype: {
        'NA12878-N1-DNA1-WES1': 'het',
      },
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      genotype: {
        'NA12878-N1-DNA1-WES1': 'hom',
      },
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when nested object changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      quality: {
        'NA12878-N1-DNA1-WES1': {
          dp_het: 15,
          dp_hom: 5,
        },
      },
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      quality: {
        'NA12878-N1-DNA1-WES1': {
          dp_het: 10,
          dp_hom: 5,
        },
      },
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when array changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gene_allowlist: ['BRCA1', 'BRCA2'],
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gene_allowlist: ['BRCA1'],
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when array order changes', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      gene_allowlist: ['BRCA2', 'BRCA1'],
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      gene_allowlist: ['BRCA1', 'BRCA2'],
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when new property is added', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: true,
      require_in_clinvar: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when property is removed', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
      require_in_clinvar: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is true when multiple properties change', () => {
    variantQueryStore.querySettings = {
      database: 'ensembl',
      var_type_snv: false,
      var_type_mnv: true,
      gnomad_genomes_frequency: 0.01,
      require_in_clinvar: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
      var_type_mnv: false,
      gnomad_genomes_frequency: 0.002,
      require_in_clinvar: false,
    }

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(true)
  })

  test('hasAnyChanges is false for identical complex nested objects', () => {
    const settings = {
      database: 'refseq',
      genotype: {
        'NA12878-N1-DNA1-WES1': 'het',
        'NA12891-N1-DNA1-WES1': 'any',
      },
      quality: {
        'NA12878-N1-DNA1-WES1': {
          dp_het: 10,
          dp_hom: 5,
          ab: 0.2,
          gq: 10,
        },
      },
      gene_allowlist: ['BRCA1', 'BRCA2'],
      effects: ['missense_variant', 'stop_gained'],
    }

    variantQueryStore.querySettings = JSON.parse(JSON.stringify(settings))
    variantQueryStore.lastSubmittedQuerySettings = JSON.parse(
      JSON.stringify(settings),
    )

    const hasAnyChanges = createHasAnyChanges()

    expect(hasAnyChanges.value).toBe(false)
  })

  test('hasAnyChanges reactively updates when settings change', () => {
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: true,
    }
    variantQueryStore.lastSubmittedQuerySettings = {
      database: 'refseq',
      var_type_snv: true,
    }

    const hasAnyChanges = createHasAnyChanges()

    // Initially no changes
    expect(hasAnyChanges.value).toBe(false)

    // Modify current settings
    variantQueryStore.querySettings = {
      database: 'ensembl',
      var_type_snv: true,
    }

    // Should detect change
    expect(hasAnyChanges.value).toBe(true)

    // Restore to match
    variantQueryStore.querySettings = {
      database: 'refseq',
      var_type_snv: true,
    }

    // Should be false again
    expect(hasAnyChanges.value).toBe(false)
  })
})

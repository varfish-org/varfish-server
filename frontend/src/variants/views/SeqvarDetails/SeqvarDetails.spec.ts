import { useGeneInfoStore } from '@bihealth/reev-frontend-lib/stores/geneInfo'
import { createTestingPinia } from '@pinia/testing'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'

import SeqvarDetails from './SeqvarDetails.vue'

describe('SeqvarDetails', () => {
  /** Mount the view for a result row with the given HGNC ID; return the gene info store. */
  const mountWithHgncId = async (hgncId: string) => {
    const pinia = createTestingPinia({ createSpy: vi.fn })
    const resultSetStore = useVariantResultSetStore(pinia)
    resultSetStore.caseUuid = 'case-uuid'
    resultSetStore.resultRow = {
      release: 'GRCh37',
      chromosome: '1',
      start: 100,
      reference: 'A',
      alternative: 'G',
      payload: { hgnc_id: hgncId },
    } as any
    shallowMount(SeqvarDetails, {
      props: { projectUuid: 'project-uuid', resultRowUuid: 'row-uuid' },
      global: { plugins: [pinia] },
    })
    await flushPromises()
    return useGeneInfoStore(pinia)
  }

  test('loads the gene of a variant with HGNC ID', async () => {
    const geneInfoStore = await mountWithHgncId('HGNC:1100')

    expect(geneInfoStore.initialize).toHaveBeenCalledWith('HGNC:1100', 'grch37')
  })

  test('does not load gene data for a variant without HGNC ID', async () => {
    const geneInfoStore = await mountWithHgncId('')

    expect(geneInfoStore.initialize).not.toHaveBeenCalled()
    expect(geneInfoStore.clearData).toHaveBeenCalled()
  })
})

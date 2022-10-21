import ColumnControl from '@variants/components/ColumnControl.vue'
import { shallowMount } from '@vue/test-utils'
import Multiselect from '@vueform/multiselect'
import { describe, expect, test, vi } from 'vitest'

describe('ColumnControl.vue', () => {
  test('set column controls', async () => {
    const columnApi = {
      setColumnsVisible: vi.fn(),
      setColumnVisible: vi.fn(),
    }
    const wrapper = shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: [0, 1],
        columnApi: columnApi,
      },
    })

    const selectors = wrapper.findAll('select')
    const displayDetails = selectors[0]
    const displayFrequency = selectors[1]
    const displayConstraint = selectors[2]
    const displayColumns = wrapper.findComponent(Multiselect)

    await displayDetails.setValue(1)
    await displayFrequency.setValue(1)
    await displayConstraint.setValue(1)
    await displayColumns.setValue([0, 1, 2])

    expect(columnApi.setColumnVisible).toHaveBeenCalledTimes(13)
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      1,
      'clinvar',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      2,
      'exac_pLI',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      3,
      'exac_mis_z',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      4,
      'exac_syn_z',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      5,
      'gnomad_loeuf',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      6,
      'gnomad_pLI',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      7,
      'gnomad_mis_z',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      9,
      'effect_summary',
      true
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      10,
      'effect',
      true
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      11,
      'hgvs_p',
      true
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      12,
      'hgvs_c',
      false
    )
    expect(columnApi.setColumnVisible).toHaveBeenNthCalledWith(
      13,
      'exon_dist',
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenCalledTimes(9)
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      1,
      ['position', 'reference', 'alternative'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      2,
      ['exac_frequency', 'exac_homozygous'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      3,
      ['thousand_genomes_frequency', 'thousand_genomes_homozygous'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      4,
      ['gnomad_exomes_frequency', 'gnomad_exomes_homozygous'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      5,
      ['gnomad_genomes_frequency', 'gnomad_genomes_homozygous'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      6,
      ['inhouse_carriers', 'inhouse_hom_alt'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      7,
      ['mtdb_frequency', 'mtdb_count'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      8,
      ['helixmtdb_frequency', 'helixmtdb_hom_count'],
      false
    )
    expect(columnApi.setColumnsVisible).toHaveBeenNthCalledWith(
      9,
      ['mitomap_frequency', 'mitomap_count'],
      false
    )
  })

  test('set column controls empty display columns', () => {
    const columnApi = {
      setColumnsVisible: vi.fn(),
      setColumnVisible: vi.fn(),
    }
    shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: null,
        columnApi: columnApi,
      },
    })
  })

  test('set column controls without column api', async () => {
    const wrapper = shallowMount(ColumnControl, {
      props: {
        displayDetails: 0,
        displayFrequency: 0,
        displayConstraint: 0,
        displayColumns: [0, 1],
        columnApi: null,
      },
    })
    const selectors = wrapper.findAll('select')
    const displayDetails = selectors[0]
    const displayFrequency = selectors[1]
    const displayConstraint = selectors[2]
    const displayColumns = wrapper.findComponent(Multiselect)

    await displayDetails.setValue(1)
    await displayFrequency.setValue(1)
    await displayConstraint.setValue(1)
    await displayColumns.setValue([0, 1, 2])
  })
})

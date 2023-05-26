import { createTestingPinia } from '@pinia/testing'
import VariantDetailsLinkOuts from '@variants/components/VariantDetailsLinkOuts.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'

import trioVariantsData from '../../data/variants-trio.json'

const piniaTestStore = createTestingPinia({
  initialState: {
    querySettings: {
      queryHpoTerms: {
        'HP:0000118': 'Phenotypic abnormality',
        'HP:0200102': 'Sparse or absent eyelashes',
      },
    },
  },
  createSpy: vi.fn,
})

describe('VariantDetailsLinkOuts.vue', () => {
  test('full list', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: {
          symbol: 'CHEK2',
          gene_symbol: '',
        },
        smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
        hgmdProEnabled: true,
        hgmdProPrefix: 'https://hgmd-pro.example.com/',
        umdPredictorApiToken: 'XXXtokenXXX',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(27)
    expect(links[0].text()).toBe('OMIM')
    expect(links[1].text()).toBe('GeneCards')
    expect(links[2].text()).toBe('Entrez')
    expect(links[3].text()).toBe('HGNC')
    expect(links[4].text()).toBe('HGMD Public')
    expect(links[5].text()).toBe('ProteinAtlas')
    expect(links[6].text()).toBe('PubMed')
    expect(links[7].text()).toBe('ClinVar')
    expect(links[8].text()).toBe('PanelApp')
    expect(links[9].text()).toBe('HGMD Pro')
    expect(links[10].text()).toBe('EnsEMBL')
    expect(links[11].text()).toBe('MetaDome')
    expect(links[12].text()).toBe('gnomAD')
    expect(links[13].text()).toBe('MGI')
    expect(links[14].text()).toBe('GenCC')
    expect(links[15].text()).toBe('Missense3D')
    expect(links[16].text()).toBe('VarSome')
    expect(links[17].text()).toBe('PubMed+Pheno')
    expect(links[18].text()).toBe('UCSC')
    expect(links[19].text()).toBe('EnsEMBL')
    expect(links[20].text()).toBe('DGV')
    expect(links[21].text()).toBe('gnomAD')
    expect(links[22].text()).toBe('MT 85')
    expect(links[23].text()).toBe('MT 2021')
    expect(links[24].text()).toBe('Human Splicing Finder')
    expect(links[25].text()).toBe('varSEAK Splicing')
    expect(links[26].text()).toBe('UMD Predictor')

    expect(links[0].classes('disabled')).toBe(false)
    expect(links[1].classes('disabled')).toBe(false)
    expect(links[2].classes('disabled')).toBe(false)
    expect(links[3].classes('disabled')).toBe(false)
    expect(links[4].classes('disabled')).toBe(false)
    expect(links[5].classes('disabled')).toBe(false)
    expect(links[6].classes('disabled')).toBe(false)
    expect(links[7].classes('disabled')).toBe(false)
    expect(links[8].classes('disabled')).toBe(false)
    expect(links[9].classes('disabled')).toBe(false)
    expect(links[10].classes('disabled')).toBe(false)
    expect(links[11].classes('disabled')).toBe(false)
    expect(links[12].classes('disabled')).toBe(false)
    expect(links[13].classes('disabled')).toBe(false)
    expect(links[14].classes('disabled')).toBe(false)
    expect(links[15].classes('disabled')).toBe(false)
    expect(links[16].classes('disabled')).toBe(false)
    // TODO [TEST_STUB] Fails ???
    // expect(links[17].classes('disabled')).toBe(false)
    expect(links[18].classes('disabled')).toBe(false)
    expect(links[19].classes('disabled')).toBe(false)
    expect(links[20].classes('disabled')).toBe(false)
    expect(links[21].classes('disabled')).toBe(false)
    expect(links[22].classes('disabled')).toBe(false)
    expect(links[23].classes('disabled')).toBe(false)
    expect(links[24].classes('disabled')).toBe(true)
    expect(links[25].classes('disabled')).toBe(false)
    expect(links[26].classes('disabled')).toBe(false)

    expect(buttons.length).toBe(1)
    expect(buttons[0].text()).toBe('PolyPhen2')
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('full gene missing', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: null,
        smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
        hgmdProEnabled: true,
        hgmdProPrefix: 'https://hgmd-pro.example.com/',
        umdPredictorApiToken: 'XXXtokenXXX',
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(27)
    expect(links[0].classes('disabled')).toBe(true)
    expect(links[1].classes('disabled')).toBe(true)
    expect(links[2].classes('disabled')).toBe(true)
    expect(links[3].classes('disabled')).toBe(true)
    expect(links[4].classes('disabled')).toBe(true)
    expect(links[5].classes('disabled')).toBe(true)
    expect(links[6].classes('disabled')).toBe(true)
    expect(links[7].classes('disabled')).toBe(true)
    expect(links[8].classes('disabled')).toBe(true)
    expect(links[9].classes('disabled')).toBe(true)
    expect(links[10].classes('disabled')).toBe(false)
    expect(links[11].classes('disabled')).toBe(false)
    expect(links[12].classes('disabled')).toBe(false)
    expect(links[13].classes('disabled')).toBe(false)
    expect(links[14].classes('disabled')).toBe(false)
    expect(links[15].classes('disabled')).toBe(false)
    expect(links[16].classes('disabled')).toBe(false)
    // TODO [TEST_STUB] Fails ???
    // expect(links[17].classes('disabled')).toBe(false)
    expect(links[18].classes('disabled')).toBe(false)
    expect(links[19].classes('disabled')).toBe(false)
    expect(links[20].classes('disabled')).toBe(false)
    expect(links[21].classes('disabled')).toBe(false)
    expect(links[22].classes('disabled')).toBe(false)
    expect(links[23].classes('disabled')).toBe(false)
    expect(links[24].classes('disabled')).toBe(true)
    expect(links[25].classes('disabled')).toBe(true)
    expect(links[26].classes('disabled')).toBe(false)

    expect(buttons.length).toBe(1)
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('minimal list', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: {
          symbol: 'CHEK2',
          gene_symbol: '',
        },
        smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(26)
    expect(links[0].text()).toBe('OMIM')
    expect(links[1].text()).toBe('GeneCards')
    expect(links[2].text()).toBe('Entrez')
    expect(links[3].text()).toBe('HGNC')
    expect(links[4].text()).toBe('HGMD Public')
    expect(links[5].text()).toBe('ProteinAtlas')
    expect(links[6].text()).toBe('PubMed')
    expect(links[7].text()).toBe('ClinVar')
    expect(links[8].text()).toBe('PanelApp')
    expect(links[9].text()).toBe('EnsEMBL')
    expect(links[10].text()).toBe('MetaDome')
    expect(links[11].text()).toBe('gnomAD')
    expect(links[12].text()).toBe('MGI')
    expect(links[13].text()).toBe('GenCC')
    expect(links[14].text()).toBe('Missense3D')
    expect(links[15].text()).toBe('VarSome')
    expect(links[16].text()).toBe('PubMed+Pheno')
    expect(links[17].text()).toBe('UCSC')
    expect(links[18].text()).toBe('EnsEMBL')
    expect(links[19].text()).toBe('DGV')
    expect(links[20].text()).toBe('gnomAD')
    expect(links[21].text()).toBe('MT 85')
    expect(links[22].text()).toBe('MT 2021')
    expect(links[23].text()).toBe('Human Splicing Finder')
    expect(links[24].text()).toBe('varSEAK Splicing')
    expect(links[25].text()).toBe('UMD Predictor')

    expect(links[0].classes('disabled')).toBe(false)
    expect(links[1].classes('disabled')).toBe(false)
    expect(links[2].classes('disabled')).toBe(false)
    expect(links[3].classes('disabled')).toBe(false)
    expect(links[4].classes('disabled')).toBe(false)
    expect(links[5].classes('disabled')).toBe(false)
    expect(links[6].classes('disabled')).toBe(false)
    expect(links[7].classes('disabled')).toBe(false)
    expect(links[8].classes('disabled')).toBe(false)
    expect(links[9].classes('disabled')).toBe(false)
    expect(links[10].classes('disabled')).toBe(false)
    expect(links[11].classes('disabled')).toBe(false)
    expect(links[12].classes('disabled')).toBe(false)
    expect(links[13].classes('disabled')).toBe(false)
    expect(links[14].classes('disabled')).toBe(false)
    expect(links[15].classes('disabled')).toBe(false)
    // TODO [TEST_Stub] Fails ???
    // expect(links[16].classes('disabled')).toBe(false)
    expect(links[17].classes('disabled')).toBe(false)
    expect(links[18].classes('disabled')).toBe(false)
    expect(links[19].classes('disabled')).toBe(false)
    expect(links[20].classes('disabled')).toBe(false)
    expect(links[21].classes('disabled')).toBe(false)
    expect(links[22].classes('disabled')).toBe(false)
    expect(links[23].classes('disabled')).toBe(true)
    expect(links[24].classes('disabled')).toBe(false)
    expect(links[25].classes('disabled')).toBe(true)

    expect(buttons.length).toBe(1)
    expect(buttons[0].text()).toBe('PolyPhen2')
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('minimal gene missing', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: null,
        smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(26)
    expect(links[0].classes('disabled')).toBe(true)
    expect(links[1].classes('disabled')).toBe(true)
    expect(links[2].classes('disabled')).toBe(true)
    expect(links[3].classes('disabled')).toBe(true)
    expect(links[4].classes('disabled')).toBe(true)
    expect(links[5].classes('disabled')).toBe(true)
    expect(links[6].classes('disabled')).toBe(true)
    expect(links[7].classes('disabled')).toBe(true)
    expect(links[8].classes('disabled')).toBe(true)
    expect(links[9].classes('disabled')).toBe(false)
    expect(links[10].classes('disabled')).toBe(false)
    expect(links[11].classes('disabled')).toBe(false)
    expect(links[12].classes('disabled')).toBe(false)
    expect(links[13].classes('disabled')).toBe(false)
    expect(links[14].classes('disabled')).toBe(false)
    expect(links[15].classes('disabled')).toBe(false)
    // TODO [TEST_STUB] Fails ???
    // expect(links[16].classes('disabled')).toBe(false)
    expect(links[17].classes('disabled')).toBe(false)
    expect(links[18].classes('disabled')).toBe(false)
    expect(links[19].classes('disabled')).toBe(false)
    expect(links[20].classes('disabled')).toBe(false)
    expect(links[21].classes('disabled')).toBe(false)
    expect(links[22].classes('disabled')).toBe(false)
    expect(links[23].classes('disabled')).toBe(true)
    expect(links[24].classes('disabled')).toBe(true)
    expect(links[25].classes('disabled')).toBe(true)

    expect(buttons.length).toBe(1)
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('minimal smallvariant missing', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: {
          symbol: 'CHEK2',
          gene_symbol: '',
        },
        smallVariant: null,
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(26)
    expect(links[0].classes('disabled')).toBe(false)
    expect(links[1].classes('disabled')).toBe(false)
    expect(links[2].classes('disabled')).toBe(false)
    expect(links[3].classes('disabled')).toBe(false)
    expect(links[4].classes('disabled')).toBe(false)
    expect(links[5].classes('disabled')).toBe(false)
    expect(links[6].classes('disabled')).toBe(false)
    expect(links[7].classes('disabled')).toBe(false)
    expect(links[8].classes('disabled')).toBe(false)
    expect(links[9].classes('disabled')).toBe(true)
    expect(links[10].classes('disabled')).toBe(true)
    expect(links[11].classes('disabled')).toBe(true)
    expect(links[12].classes('disabled')).toBe(true)
    expect(links[13].classes('disabled')).toBe(true)
    expect(links[14].classes('disabled')).toBe(true)
    expect(links[15].classes('disabled')).toBe(true)
    expect(links[16].classes('disabled')).toBe(true)
    expect(links[17].classes('disabled')).toBe(true)
    expect(links[18].classes('disabled')).toBe(true)
    expect(links[19].classes('disabled')).toBe(true)
    expect(links[20].classes('disabled')).toBe(true)
    expect(links[21].classes('disabled')).toBe(true)
    expect(links[22].classes('disabled')).toBe(true)
    expect(links[23].classes('disabled')).toBe(true)

    expect(buttons.length).toBe(1)
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('everything missing', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: null,
        smallVariant: null,
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(26)
    expect(links[0].classes('disabled')).toBe(true)
    expect(links[1].classes('disabled')).toBe(true)
    expect(links[2].classes('disabled')).toBe(true)
    expect(links[3].classes('disabled')).toBe(true)
    expect(links[4].classes('disabled')).toBe(true)
    expect(links[5].classes('disabled')).toBe(true)
    expect(links[6].classes('disabled')).toBe(true)
    expect(links[7].classes('disabled')).toBe(true)
    expect(links[8].classes('disabled')).toBe(true)
    expect(links[9].classes('disabled')).toBe(true)
    expect(links[10].classes('disabled')).toBe(true)
    expect(links[11].classes('disabled')).toBe(true)
    expect(links[12].classes('disabled')).toBe(true)
    expect(links[13].classes('disabled')).toBe(true)
    expect(links[14].classes('disabled')).toBe(true)
    expect(links[15].classes('disabled')).toBe(true)
    expect(links[16].classes('disabled')).toBe(true)
    expect(links[17].classes('disabled')).toBe(true)
    expect(links[18].classes('disabled')).toBe(true)
    expect(links[19].classes('disabled')).toBe(true)
    expect(links[20].classes('disabled')).toBe(true)
    expect(links[21].classes('disabled')).toBe(true)
    expect(links[22].classes('disabled')).toBe(true)
    expect(links[23].classes('disabled')).toBe(true)

    expect(buttons.length).toBe(1)
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('minimal with gene symbol', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: {
          symbol: '',
          gene_symbol: 'CHEK2',
        },
        smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    const links = wrapper.findAll('a')
    const buttons = wrapper.findAll('button')

    expect(links.length).toBe(26)
    expect(links[0].classes('disabled')).toBe(false)
    expect(links[1].classes('disabled')).toBe(false)
    expect(links[2].classes('disabled')).toBe(false)
    expect(links[3].classes('disabled')).toBe(false)
    expect(links[4].classes('disabled')).toBe(false)
    expect(links[5].classes('disabled')).toBe(false)
    expect(links[6].classes('disabled')).toBe(false)
    expect(links[7].classes('disabled')).toBe(false)
    expect(links[8].classes('disabled')).toBe(false)
    expect(links[9].classes('disabled')).toBe(false)
    expect(links[10].classes('disabled')).toBe(false)
    expect(links[11].classes('disabled')).toBe(false)
    expect(links[12].classes('disabled')).toBe(false)
    expect(links[13].classes('disabled')).toBe(false)
    expect(links[14].classes('disabled')).toBe(false)
    expect(links[15].classes('disabled')).toBe(false)
    // TODO [TEST_STUB] Fails ???
    // expect(links[16].classes('disabled')).toBe(false)
    expect(links[17].classes('disabled')).toBe(false)
    expect(links[18].classes('disabled')).toBe(false)
    expect(links[19].classes('disabled')).toBe(false)
    expect(links[20].classes('disabled')).toBe(false)
    expect(links[21].classes('disabled')).toBe(false)
    expect(links[22].classes('disabled')).toBe(false)
    expect(links[23].classes('disabled')).toBe(true)
    expect(links[24].classes('disabled')).toBe(false)
    expect(links[25].classes('disabled')).toBe(true)

    expect(buttons.length).toBe(1)
    expect(buttons[0].element.disabled).toBe(true)
  })

  test('without mgi', () => {
    const wrapper = shallowMount(VariantDetailsLinkOuts, {
      props: {
        gene: {
          symbol: '',
          gene_symbol: 'CHEK2',
        },
        smallVariant: trioVariantsData[0],
        hgmdProEnabled: false,
        umdPredictorApiToken: null,
      },
      global: {
        plugins: [piniaTestStore],
      },
    })

    expect(wrapper.findAll('a')[12].classes('disabled')).toBe(true)
  })
})

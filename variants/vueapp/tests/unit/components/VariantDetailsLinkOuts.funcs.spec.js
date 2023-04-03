import {
  getGeneSymbol,
  getLinkoutDgv,
  getLinkoutEnsembl,
  getLinkoutEnsemblGene,
  getLinkoutEntrez,
  getLinkoutGenCC,
  getLinkoutGnomad,
  getLinkoutGnomadGene,
  getLinkoutMetaDome,
  getLinkoutMgi,
  getLinkoutMissense3D,
  getLinkoutPubMedPheno,
  getLinkoutUcsc,
  getLinkoutUmd,
  getLinkoutVariantValidator,
  getLinkoutVarseak,
  getLinkoutVarsome,
} from '@variants/components/VariantDetailsLinkOuts.funcs.js'
import { describe, expect, test } from 'vitest'

import trioVariantsData from '../../data/variants-trio.json'

const smallvariantBasedFunctions = [
  getLinkoutDgv,
  getLinkoutEnsembl,
  getLinkoutEnsemblGene,
  getLinkoutGnomad,
  getLinkoutGnomadGene,
  getLinkoutUcsc,
  getLinkoutVariantValidator,
  getLinkoutVarsome,
]

const geneSymbol = {
  symbol: 'CHEK2',
  gene_symbol: '',
  entrez_id: 'xxx',
}

const geneGeneSymbol = {
  symbol: '',
  gene_symbol: 'CHEK2',
  entrez_id: 'xxx',
}

const geneNoEntrez = {
  symbol: '',
  gene_symbol: 'CHEK2',
  entrez_id: null,
}

const hpoTerms = {
  'HP:0000118': 'Phenotypic abnormality',
  'HP:0200102': 'Sparse or absent eyelashes',
}

const httpLinkRegex = /^https?:\/\/.*/
const emptyLinkRegex = /^#$/

describe('VariantDetailsLinkOuts.funcs.js', () => {
  test('getGeneSymbol with symbol', () => {
    expect(getGeneSymbol(geneSymbol)).toBe('CHEK2')
  })

  test('getGeneSymbol with geneSymbol', () => {
    expect(getGeneSymbol(geneGeneSymbol)).toBe('CHEK2')
  })

  test('getGeneSymbol empty', () => {
    expect(getGeneSymbol(null)).toBeUndefined()
  })

  test('getLinkoutEntrez', () => {
    expect(getLinkoutEntrez(geneSymbol)).toMatch(httpLinkRegex)
    expect(getLinkoutEntrez(geneSymbol)).toMatch(/xxx$/)
  })

  test('getLinkoutEntrez empty', () => {
    expect(getLinkoutEntrez(null)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutEntrez ', () => {
    expect(getLinkoutEntrez(geneNoEntrez)).toMatch(httpLinkRegex)
    expect(getLinkoutEntrez(geneNoEntrez)).toMatch(
      /&quot;Homo\+sapiens&quot;\)$/
    )
  })

  test('smallvariant-based functions on release GRCh37', () => {
    for (const fun of smallvariantBasedFunctions) {
      expect(fun(trioVariantsData[0])).toMatch(httpLinkRegex)
    }
  })

  test('smallvariant-based functions on release GRCh38', () => {
    for (const fun of smallvariantBasedFunctions) {
      expect(fun({ ...trioVariantsData[0], release: 'GRCh38' })).toMatch(
        httpLinkRegex
      )
    }
  })

  test('smallvariant-based functions on unknown release', () => {
    for (const fun of smallvariantBasedFunctions) {
      expect(fun({ ...trioVariantsData[0], release: 'UNKNOWN' })).toMatch(
        emptyLinkRegex
      )
    }
  })

  test('smallvariant-based functions empty', () => {
    for (const fun of smallvariantBasedFunctions) {
      expect(fun(null)).toMatch(emptyLinkRegex)
    }
  })

  test('getLinkoutVarseak', () => {
    expect(getLinkoutVarseak(trioVariantsData[0], geneSymbol)).toMatch(
      httpLinkRegex
    )
    expect(
      getLinkoutVarseak(
        { ...trioVariantsData[0], release: 'GRCh38' },
        geneSymbol
      )
    ).toMatch(httpLinkRegex)
    expect(
      getLinkoutVarseak(
        { ...trioVariantsData[0], release: 'UNKNOWN' },
        geneSymbol
      )
    ).toMatch(httpLinkRegex)
  })

  test('getLinkoutVarseak no smallvariant', () => {
    expect(getLinkoutVarseak(null, geneSymbol)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutVarseak no gene', () => {
    expect(getLinkoutVarseak(trioVariantsData[0], null)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutVarseak empty', () => {
    expect(getLinkoutVarseak(null, null)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutUmd on release GRCh37', () => {
    expect(getLinkoutUmd('TOKEN', trioVariantsData[0])).toMatch(httpLinkRegex)
  })

  test('getLinkoutUmd on release GRCh38', () => {
    expect(
      getLinkoutUmd('TOKEN', { ...trioVariantsData[0], release: 'GRCh38' })
    ).toMatch(emptyLinkRegex)
  })

  test('getLinkoutUmd on unknown release', () => {
    expect(
      getLinkoutUmd('TOKEN', { ...trioVariantsData[0], release: 'UNKNOWN' })
    ).toMatch(emptyLinkRegex)
  })

  test('getLinkoutUmd empty', () => {
    expect(getLinkoutUmd('TOKEN', null)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutGenCC', () => {
    expect(getLinkoutGenCC(trioVariantsData[0])).toMatch(httpLinkRegex)
    expect(
      getLinkoutGenCC({ ...trioVariantsData[0], release: 'GRCh38' })
    ).toMatch(httpLinkRegex)
    expect(
      getLinkoutGenCC({ ...trioVariantsData[0], release: 'UNKNOWN' })
    ).toMatch(httpLinkRegex)
  })

  test('getLinkoutGenCC hgnc_id missing', () => {
    expect(getLinkoutGenCC({ ...trioVariantsData[0], hgnc_id: null })).toMatch(
      emptyLinkRegex
    )
  })

  test('getLinkoutMetaDome', () => {
    expect(getLinkoutMetaDome(trioVariantsData[0])).toMatch(httpLinkRegex)
    expect(
      getLinkoutMetaDome({ ...trioVariantsData[0], release: 'GRCh38' })
    ).toMatch(httpLinkRegex)
    expect(
      getLinkoutMetaDome({ ...trioVariantsData[0], release: 'UNKNOWN' })
    ).toMatch(httpLinkRegex)
  })

  test('getLinkoutMetaDome empty', () => {
    expect(getLinkoutMetaDome(null)).toMatch(emptyLinkRegex)
  })

  test('getLinkoutMgi', () => {
    expect(getLinkoutMgi({ ...trioVariantsData[0], mgi_id: 'xxx' })).toMatch(
      httpLinkRegex
    )
    expect(
      getLinkoutMgi({
        ...trioVariantsData[0],
        mgi_id: 'xxx',
        release: 'GRCh38',
      })
    ).toMatch(httpLinkRegex)
    expect(
      getLinkoutMgi({
        ...trioVariantsData[0],
        mgi_id: 'xxx',
        release: 'UNKNOWN',
      })
    ).toMatch(httpLinkRegex)
  })

  test('getLinkoutMgi mgi_id missing', () => {
    expect(getLinkoutMgi({ ...trioVariantsData[0], mgi_id: null })).toMatch(
      emptyLinkRegex
    )
  })

  test('getLinkoutMissense3D', () => {
    expect(getLinkoutMissense3D(trioVariantsData[0])).toMatch(httpLinkRegex)
    expect(
      getLinkoutMissense3D({ ...trioVariantsData[0], release: 'GRCh38' })
    ).toMatch(httpLinkRegex)
    expect(
      getLinkoutMissense3D({ ...trioVariantsData[0], release: 'UNKNOWN' })
    ).toMatch(httpLinkRegex)
  })

  test('getLinkoutMissense3D uniprot_ids missing', () => {
    expect(
      getLinkoutMissense3D({ ...trioVariantsData[0], uniprot_ids: null })
    ).toMatch(emptyLinkRegex)
  })

  test('getLinkoutPubMedPheno', () => {
    expect(getLinkoutPubMedPheno(geneSymbol, hpoTerms)).toBe(
      'https://www.ncbi.nlm.nih.gov/pubmed/?term=CHEK2 AND ((phenotypic AND abnormality) OR (sparse AND absent AND eyelashes))'
    )
  })

  test('getLinkoutPubMedPheno gene missing', () => {
    expect(getLinkoutPubMedPheno(null, hpoTerms)).toMatch(/^#$/)
  })
})

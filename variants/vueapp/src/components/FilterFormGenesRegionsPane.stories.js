import FilterFormGenesRegionsPane from '@variants/components/FilterFormGenesRegionsPane.vue'
import { reactive } from 'vue'

export default {
  title: 'Variants / Filter Form Genes & Regions',
  component: FilterFormGenesRegionsPane,
  parameters: {
    fetchMock: {
      mocks: [
        {
          matcher: {
            name: 'matchAll',
            method: 'GET',
            url: '*',
          },
          response: (url, _options, _request) => {
            const genes = [
              {
                hgnc_id: 'HGNC:12403',
                symbol: 'TTN',
                ensembl_gene_id: 'ENSG00000155657',
                entrez_id: '7273',
              },
              {
                hgnc_id: 'HGNC:20324',
                symbol: 'TGDS',
                ensembl_gene_id: 'ENSG00000088451',
                entrez_id: '23483',
              },
              {
                hgnc_id: 'HGNC:29661',
                symbol: 'OMA1',
                ensembl_gene_id: 'ENSG00000162600',
                entrez_id: '115209',
              },
            ]

            for (const gene of genes) {
              for (const val of Object.values(gene)) {
                if (url.endsWith(val)) {
                  return {
                    status: 200,
                    body: gene,
                  }
                }
              }
            }
            return {
              status: 404,
            }
          },
        },
      ],
    },
  },
}

const Template = (args) => ({
  components: { FilterFormGenesRegionsPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormGenesRegionsPane\n' +
    '    csrf-token="fake"\n' +
    '    lookup-gene-api-endpoint="/geneinfo/api/lookup-gene/"\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :filtration-complexity-mode="args.filtrationComplexityMode"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const WithRegion = Template.bind({})
WithRegion.args = {
  showFiltrationInlineHelp: false,
  filtrationComplexityMode: 'dev',
  querySettings: reactive({
    gene_blocklist: [],
    gene_allowlist: [],
    genomic_region: ['chr1', 'chrX:1,000,000-2,000,000'],
  }),
}

export const WithInvalidRegion = Template.bind({})
WithInvalidRegion.args = {
  showFiltrationInlineHelp: false,
  filtrationComplexityMode: 'dev',
  querySettings: reactive({
    gene_blocklist: ['TGDS'],
    gene_allowlist: ['TGDS'],
    genomic_region: ['chr1', 'chrX:1,000,000-2,000,000', 'invalid'],
  }),
}

export const WithAllowListAndHelp = Template.bind({})
WithAllowListAndHelp.args = {
  showFiltrationInlineHelp: true,
  filtrationComplexityMode: 'dev',
  querySettings: reactive({
    gene_blocklist: [],
    gene_allowlist: ['TGDS', 'TTN'],
    genomic_region: [],
  }),
}

export const WithBlockListAndHelp = Template.bind({})
WithBlockListAndHelp.args = {
  showFiltrationInlineHelp: true,
  filtrationComplexityMode: 'dev',
  querySettings: reactive({
    gene_blocklist: ['TGDS', 'TTN'],
    gene_allowlist: [],
    genomic_region: [],
  }),
}

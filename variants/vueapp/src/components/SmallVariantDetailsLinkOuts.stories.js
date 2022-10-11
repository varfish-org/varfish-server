import trioVariantsData from '@variantsTest/data/variants-trio.json'

import SmallVariantDetailsLinkOuts from './SmallVariantDetailsLinkOuts.vue'

export default {
  title: 'Variants / Small Variant Details Link-Outs',
  component: SmallVariantDetailsLinkOuts,
}

const Template = (args) => ({
  components: { SmallVariantDetailsLinkOuts },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsLinkOuts\n' +
    '    :gene="args.gene"\n' +
    '    :small-variant="args.smallVariant"\n' +
    '    :hgmd-pro-enabled="args.hgmdProEnabled"\n' +
    '    :hgmd-pro-prefix="args.hgmdProPrefix"\n' +
    '    :umd-predictor-api-token="args.umdPredictorApiToken"\n' +
    '/>',
})

export const FullList = Template.bind({})
FullList.args = {
  gene: {
    symbol: 'CHEK2',
    gene_symbol: '',
  },
  smallVariant: trioVariantsData[0],
  hgmdProEnabled: true,
  hgmdProPrefix: 'https://hgmd-pro.example.com/',
  umdPredictorApitoken: 'XXXtokenXXX',
}

export const MinimalList = Template.bind({})
MinimalList.args = {
  gene: {
    symbol: 'CHEK2',
    gene_symbol: '',
  },
  smallVariant: trioVariantsData[0],
  hgmdProEnabled: false,
  umdPredictorApitoken: null,
}

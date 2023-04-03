import trioVariantsData from '@variantsTest/data/variants-trio.json'

import VariantDetailsLinkOuts from './VariantDetailsLinkOuts.vue'

export default {
  title: 'Variants / Small Variant Details Link-Outs',
  component: VariantDetailsLinkOuts,
}

const Template = (args) => ({
  components: { VariantDetailsLinkOuts },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsLinkOuts\n' +
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
  smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
  hgmdProEnabled: true,
  hgmdProPrefix: 'https://hgmd-pro.example.com/',
  umdPredictorApiToken: 'XXXtokenXXX',
}

export const MinimalList = Template.bind({})
MinimalList.args = {
  gene: {
    symbol: 'CHEK2',
    gene_symbol: '',
  },
  smallVariant: trioVariantsData[0],
  hgmdProEnabled: false,
  umdPredictorApiToken: null,
}

export const FullGeneMissing = Template.bind({})
FullGeneMissing.args = {
  gene: null,
  smallVariant: { ...trioVariantsData[0], mgi_id: 'xxx' },
  hgmdProEnabled: true,
  hgmdProPrefix: 'https://hgmd-pro.example.com/',
  umdPredictorApiToken: 'XXXtokenXXX',
}

export const MinimalGeneMissing = Template.bind({})
MinimalGeneMissing.args = {
  gene: null,
  smallVariant: trioVariantsData[0],
  hgmdProEnabled: false,
  umdPredictorApiToken: null,
}

export const MinimalSmallVariantMissing = Template.bind({})
MinimalSmallVariantMissing.args = {
  gene: {
    symbol: 'CHEK2',
    gene_symbol: '',
  },
  smallVariant: null,
  hgmdProEnabled: false,
  umdPredictorApiToken: null,
}

export const AllMissing = Template.bind({})
AllMissing.args = {
  gene: null,
  smallVariant: null,
  hgmdProEnabled: false,
  umdPredictorApiToken: null,
}

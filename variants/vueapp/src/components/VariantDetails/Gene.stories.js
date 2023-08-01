import VariantDetailsGene from '@variants/components/VariantDetails/Gene.vue'
import brca1GeneInfo from '@variantsTest/data/data/gene-brca1-geneinfo.json'
import mtdnaGeneinfo from '@variantsTest/data/data/gene-mtdna-geneinfo.json'
import brca1SmallVar from '@variantsTest/data/data/var-brca1-missense-benign-smallvar.json'
import mtdnaSmallVar from '@variantsTest/data/data/var-brca1-missense-benign-smallvar.json'

export default {
  title: 'Variants / Small Variant Details Gene',
  component: VariantDetailsGene,
}

const Template = (args) => ({
  components: { VariantDetailsGene },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsGene\n' +
    '    :gene="args.gene"\n' +
    '    :small-var="args.smallVar"\n' +
    '    :hgmd-pro-enabled="args.hgmdProEnabled"\n' +
    '    :hgmd-pro-prefix="args.hgmdProPrefix"\n' +
    '/>',
})

export const Autosomal = Template.bind({})
Autosomal.args = {
  hgmdProEnabled: true,
  hgmdProPrefix: 'https://my.qiagendigitalinsights.com/bbp/view/hgmd/pro',
  smallVar: brca1SmallVar,
  gene: brca1GeneInfo,
}

export const Mitochondrial = Template.bind({})
Mitochondrial.args = {
  hgmdProEnabled: true,
  hgmdProPrefix: 'https://my.qiagendigitalinsights.com/bbp/view/hgmd/pro',
  smallVar: mtdnaSmallVar,
  gene: mtdnaGeneinfo,
}

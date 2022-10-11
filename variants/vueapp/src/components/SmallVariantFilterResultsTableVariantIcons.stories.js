import SmallVariantFilterResultsTableVariantIcons from './SmallVariantFilterResultsTableVariantIcons.vue'

export default {
  title: 'Variants / Result Table Cell Variant Icons',
  component: SmallVariantFilterResultsTableVariantIcons,
}

const Template = (args) => ({
  components: { SmallVariantFilterResultsTableVariantIcons },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantFilterResultsTableVariantIcons\n' +
    '    :params="args.params"\n' +
    '/>',
})

export const AllActive = Template.bind({})
AllActive.args = {
  params: {
    data: {
      flag_count: 1,
      comment_count: 1,
      acmg_class_override: null,
      acmg_class_auto: 4,
      symbol: null,
      gene_symbol: 'GENE',
      rsid: 'rs12345',
      in_clinvar: true,
      vcv: 'VCV123',
      summary_pathogenicity_label: 'pathogenic',
      hgmd_public_overlap: true,
    },
  },
}

export const AllInactive = Template.bind({})
AllInactive.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: null,
      symbol: null,
      gene_symbol: null,
      rsid: null,
      in_clinvar: false,
      vcv: null,
      summary_pathogenicity_label: null,
      hgmd_public_overlap: false,
    },
  },
}

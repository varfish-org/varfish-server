import FilterResultsTableVariantIcons from '@variants/components/FilterResultsTableVariantIcons.vue'

export default {
  title: 'Variants / Result Table Cell Variant Icons',
  component: FilterResultsTableVariantIcons,
}

const Template = (args) => ({
  components: { FilterResultsTableVariantIcons },
  setup() {
    return { args }
  },
  template:
    '<FilterResultsTableVariantIcons\n' + '    :params="args.params"\n' + '/>',
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

export const Acmg1 = Template.bind({})
Acmg1.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: 1,
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

export const Acmg2 = Template.bind({})
Acmg2.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: 2,
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

export const Acmg3 = Template.bind({})
Acmg3.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: 3,
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

export const Acmg4 = Template.bind({})
Acmg4.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: 4,
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

export const Acmg5 = Template.bind({})
Acmg5.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: null,
      acmg_class_auto: 5,
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

export const AcmgOverride = Template.bind({})
AcmgOverride.args = {
  params: {
    data: {
      flag_count: 0,
      comment_count: 0,
      acmg_class_override: 4,
      acmg_class_auto: 2,
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

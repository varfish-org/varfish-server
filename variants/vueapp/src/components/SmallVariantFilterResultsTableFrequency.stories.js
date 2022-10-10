import SmallVariantFilterResultsTableFrequency from './SmallVariantFilterResultsTableFrequency.vue'

export default {
  title: 'Variants / Result Table Cell Frequency',
  component: SmallVariantFilterResultsTableFrequency,
}

const Template = (args) => ({
  components: { SmallVariantFilterResultsTableFrequency },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantFilterResultsTableFrequency\n' +
    '    :params="args.params"\n' +
    '/>',
})

export const WithWarning = Template.bind({})
WithWarning.args = {
  params: {
    value: 0.00001,
    data: {
      exac_frequency: 0.011,
      thousand_genomes_frequency: 0.011,
      gnomad_exomes_frequency: 0.011,

      inhouse_hom_alt: 51,
      exac_homozygous: 51,
      thousand_genomes_homozygous: 51,
      gnomad_exomes_homozygous: 51,
    },
  },
}

export const NoWarning = Template.bind({})
NoWarning.args = {
  params: {
    value: 0.00001,
    data: {
      exac_frequency: 0.009,
      thousand_genomes_frequency: 0.009,
      gnomad_exomes_frequency: 0.009,

      inhouse_hom_alt: 49,
      exac_homozygous: 49,
      thousand_genomes_homozygous: 49,
      gnomad_exomes_homozygous: 49,
    },
  },
}

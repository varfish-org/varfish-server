import FilterResultsTableGeneIcons from '@variants/components/FilterResultsTableGeneIcons.vue'

export default {
  title: 'Variants / Result Table Cell Gene Icons',
  component: FilterResultsTableGeneIcons,
}

const Template = (args) => ({
  components: { FilterResultsTableGeneIcons },
  setup() {
    return { args }
  },
  template:
    '<FilterResultsTableGeneIcons\n' + '    :params="args.params"\n' + '/>',
})

export const AcmgGene = Template.bind({})
AcmgGene.args = {
  params: {
    data: {
      acmg_symbol: 'true',
      modes_of_inheritance: ['AD', 'AR'],
      disease_gene: 'true',
    },
  },
}

export const DiseaseGene = Template.bind({})
DiseaseGene.args = {
  params: {
    data: {
      acmg_symbol: null,
      modes_of_inheritance: ['AR'],
      disease_gene: 'true',
    },
  },
}

export const NoDiseaseGene = Template.bind({})
NoDiseaseGene.args = {
  params: {
    data: {
      acmg_symbol: null,
      modes_of_inheritance: [],
      disease_gene: 'false',
    },
  },
}

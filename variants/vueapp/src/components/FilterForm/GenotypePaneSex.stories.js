import FilterFormGenotypePaneSex from '@variants/components/FilterForm/GenotypePaneSex.vue'

export default {
  title: 'Variants / Filter Form Genotype Sex',
  component: FilterFormGenotypePaneSex,
}

const Template = (args) => ({
  components: { FilterFormGenotypePaneSex },
  setup() {
    return { args }
  },
  template: '<FilterFormGenotypePaneSex \n' + '    :sex="args.sex"\n' + '/>',
})

export const Male = Template.bind({})
Male.args = {
  sex: 1,
}

export const Female = Template.bind({})
Female.args = {
  sex: 2,
}

export const Unknown = Template.bind({})
Unknown.args = {
  sex: 0,
}

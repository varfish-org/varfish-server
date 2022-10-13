import FilterFormGenotypePaneAffected from './FilterFormGenotypePaneAffected.vue'

export default {
  title: 'Variants / Filter Form Genotype Affected',
  component: FilterFormGenotypePaneAffected,
}

const Template = (args) => ({
  components: { FilterFormGenotypePaneAffected },
  setup() {
    return { args }
  },
  template:
    '<FilterFormGenotypePaneAffected \n' +
    '    :affected="args.affected"\n' +
    '/>',
})

export const Unaffected = Template.bind({})
Unaffected.args = {
  affected: 1,
}

export const Affected = Template.bind({})
Affected.args = {
  affected: 2,
}

export const Unknown = Template.bind({})
Unknown.args = {
  affected: 0,
}

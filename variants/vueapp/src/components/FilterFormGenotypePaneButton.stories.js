import FilterFormGenotypePaneButton from './FilterFormGenotypePaneButton.vue'

export default {
  title: 'Variants / Filter Form Genotype Button',
  component: FilterFormGenotypePaneButton,
}

const Template = (args) => ({
  components: { FilterFormGenotypePaneButton },
  setup() {
    return { args }
  },
  template: '<FilterFormGenotypePaneButton/>',
})

export const Example = Template.bind({})
Example.args = {}

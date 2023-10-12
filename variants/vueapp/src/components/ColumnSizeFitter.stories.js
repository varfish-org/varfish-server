import ColumnSizeFitter from '@variants/components/ColumnSizeFitter.vue'

export default {
  title: 'Variants / Column Size Fitter',
  component: ColumnSizeFitter,
}

const Template = (args) => ({
  components: { ColumnSizeFitter },
  setup() {
    return { args }
  },
  template: '<ColumnSizeFitter />',
})

export const Example = Template.bind({})
Example.args = {
  params: {},
}

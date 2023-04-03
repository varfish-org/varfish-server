import ColumnControl from './ColumnControl.vue'

export default {
  title: 'Variants / Column Control',
  component: ColumnControl,
  parameters: {},
}

const Template = (args) => ({
  components: { ColumnControl },
  setup() {
    return { args }
  },
  template:
    '<div class="d-flex flex-row">\n' +
    '<ColumnControl\n' +
    '    v-model:display-details="args.displayDetails"\n' +
    '    v-model:display-frequency="args.displayFrequency"\n' +
    '    v-model:display-constraint="args.displayConstraint"\n' +
    '    v-model:display-columns="args.displayColumns"\n' +
    '/>\n' +
    '</div>',
})

export const Example = Template.bind({})
Example.args = {
  displayDetails: 0,
  displayFrequency: 0,
  displayConstraint: 0,
  displayColumns: [0, 1],
}

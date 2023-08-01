import VariantDetailsFlagsIndicator from '@varfish/components/VariantDetailsFlagsIndicator.vue'

export default {
  title: 'Variants / Small Variant Details Comments Flags',
  component: VariantDetailsFlagsIndicator,
}

const Template = (args) => ({
  components: { VariantDetailsFlagsIndicator },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsFlagsIndicator\n' +
    '    :flag-state="args.flagState"\n' +
    '/>',
})

export const Positive = Template.bind({})
Positive.args = {
  flagState: 'positive',
}

export const Uncertain = Template.bind({})
Uncertain.args = {
  flagState: 'uncertain',
}

export const Negative = Template.bind({})
Negative.args = {
  flagState: 'negative',
}

export const Empty = Template.bind({})
Empty.args = {
  flagState: 'empty',
}

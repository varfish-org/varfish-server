import VariantDetailsCommentsFlagsIndicator from './VariantDetailsCommentsFlagsIndicator.vue'

export default {
  title: 'Variants / Small Variant Details Comments Flags',
  component: VariantDetailsCommentsFlagsIndicator,
}

const Template = (args) => ({
  components: { VariantDetailsCommentsFlagsIndicator },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsCommentsFlagsIndicator\n' +
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

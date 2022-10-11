import SmallVariantDetailsCommentsFlagsIndicator from './SmallVariantDetailsCommentsFlagsIndicator.vue'

export default {
  title: 'Variants / Small Variant Details Comments Flags',
  component: SmallVariantDetailsCommentsFlagsIndicator,
}

const Template = (args) => ({
  components: { SmallVariantDetailsCommentsFlagsIndicator },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsCommentsFlagsIndicator\n' +
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

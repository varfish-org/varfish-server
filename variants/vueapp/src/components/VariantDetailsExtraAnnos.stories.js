import VariantDetailsExtraAnnos from './VariantDetailsExtraAnnos.vue'

export default {
  title: 'Variants / Small Variant Details Extra Annos',
  component: VariantDetailsExtraAnnos,
}

const Template = (args) => ({
  components: { VariantDetailsExtraAnnos },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsExtraAnnos\n' +
    '    :extra-annos="args.extraAnnos"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  extraAnnos: {
    annotations: { anno1: 123, anno2: 456 },
  },
}

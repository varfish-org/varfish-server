import SmallVariantDetailsExtraAnnos from './SmallVariantDetailsExtraAnnos.vue'

export default {
  title: 'Variants / Small Variant Details Extra Annos',
  component: SmallVariantDetailsExtraAnnos,
}

const Template = (args) => ({
  components: { SmallVariantDetailsExtraAnnos },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsExtraAnnos\n' +
    '    :extra-annos="args.extraAnnos"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  extraAnnos: {
    annotations: { anno1: 123, anno2: 456 },
  },
}

import knownGeneAaData from '@variantsTest/data/known-gene-aa.json'

import SmallVariantDetailsConservation from './SmallVariantDetailsConservation.vue'

export default {
  title: 'Variants / Small Variant Details Conservation',
  component: SmallVariantDetailsConservation,
}

const Template = (args) => ({
  components: { SmallVariantDetailsConservation },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsConservation\n' +
    '    :knownGeneAa="args.knownGeneAa"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  knownGeneAa: knownGeneAaData,
}

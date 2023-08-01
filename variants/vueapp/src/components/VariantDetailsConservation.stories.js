import VariantDetailsConservation from '@variants/components/VariantDetailsConservation.vue'
import knownGeneAaData from '@variantsTest/data/known-gene-aa.json'

export default {
  title: 'Variants / Small Variant Details Conservation',
  component: VariantDetailsConservation,
}

const Template = (args) => ({
  components: { VariantDetailsConservation },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsConservation\n' +
    '    :knownGeneAa="args.knownGeneAa"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  knownGeneAa: knownGeneAaData,
}

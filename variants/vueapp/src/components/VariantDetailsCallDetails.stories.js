import VariantDetailsCallDetails from '@variants/components/VariantDetailsCallDetails.vue'
import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details Calls',
  component: VariantDetailsCallDetails,
}

const Template = (args) => ({
  components: { VariantDetailsCallDetails },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsCallDetails\n' +
    '    :case-description="args.case"\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  case: trioCaseData,
  smallVariant: trioVariantsData[0],
}

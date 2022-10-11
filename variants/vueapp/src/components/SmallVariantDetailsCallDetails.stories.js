import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

import SmallVariantDetailsCallDetails from './SmallVariantDetailsCallDetails.vue'

export default {
  title: 'Variants / Small Variant Details Calls',
  component: SmallVariantDetailsCallDetails,
}

const Template = (args) => ({
  components: { SmallVariantDetailsCallDetails },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsCallDetails\n' +
    '    :case-description="args.case"\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  case: trioCaseData,
  smallVariant: trioVariantsData[0],
}

import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

import VariantDetailsAcmgRating from './VariantDetailsAcmgRating.vue'

export default {
  title: 'Variants / Small Variant Details Calls',
  component: VariantDetailsAcmgRating,
}

const Template = (args) => ({
  components: { VariantDetailsAcmgRating },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsAcmgRating\n' +
    '    :case-description="args.case"\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  case: trioCaseData,
  smallVariant: trioVariantsData[0],
}

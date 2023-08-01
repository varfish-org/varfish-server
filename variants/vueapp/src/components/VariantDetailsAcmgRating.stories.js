import VariantDetailsAcmgRating from '@variants/components/VariantDetailsAcmgRating.vue'
import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details ACMG',
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

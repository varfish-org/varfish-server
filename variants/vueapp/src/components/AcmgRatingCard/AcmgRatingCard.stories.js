import AcmgRatingCard from './AcmgRatingCard.vue'
import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details ACMG',
  component: AcmgRatingCard,
}

const Template = (args) => ({
  components: { AcmgRatingCard },
  setup() {
    return { args }
  },
  template:
    '<AcmgRatingCard\n' + '    :small-variant="args.smallVariant"\n' + '/>',
})

export const Example = Template.bind({})
Example.args = {
  case: trioCaseData,
  smallVariant: trioVariantsData[0],
}

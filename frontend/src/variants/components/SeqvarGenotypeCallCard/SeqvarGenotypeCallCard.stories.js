import SeqvarGenotypeCallCard from '@/variants/components/SeqvarGenotypeCallCard/SeqvarGenotypeCallCard.vue'
import trioCaseData from '@/variantsTest/data/case-trio.json'
import trioVariantsData from '@/variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details Calls',
  component: SeqvarGenotypeCallCard,
}

const Template = (args) => ({
  components: { SeqvarGenotypeCallCard },
  setup() {
    return { args }
  },
  template:
    '<SeqvarGenotypeCallCard\n' +
    '    :case-description="args.case"\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  case: trioCaseData,
  smallVariant: trioVariantsData[0],
}

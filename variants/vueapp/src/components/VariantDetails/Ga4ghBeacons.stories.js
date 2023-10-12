import VariantDetailsGa4ghBeacons from '@variants/components/VariantDetails/Ga4ghBeacons.vue'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details GA4GH Beacons',
  component: VariantDetailsGa4ghBeacons,
}

const Template = (args) => ({
  components: { VariantDetailsGa4ghBeacons },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsGa4ghBeacons\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  smallVariant: trioVariantsData[0],
}

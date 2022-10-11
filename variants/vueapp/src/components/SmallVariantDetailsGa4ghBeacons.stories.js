import trioVariantsData from '@variantsTest/data/variants-trio.json'

import SmallVariantDetailsGa4ghBeacons from './SmallVariantDetailsGa4ghBeacons.vue'

export default {
  title: 'Variants / Small Variant Details GA4GH Beacons',
  component: SmallVariantDetailsGa4ghBeacons,
}

const Template = (args) => ({
  components: { SmallVariantDetailsGa4ghBeacons },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsGa4ghBeacons\n' +
    '    :small-variant="args.smallVariant"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  smallVariant: trioVariantsData[0],
}

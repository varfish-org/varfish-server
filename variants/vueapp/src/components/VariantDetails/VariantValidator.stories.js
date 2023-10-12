import VariantDetailsVariantValidator from '@variants/components/VariantDetails/VariantValidator.vue'
import { VariantValidatorStates } from '@variants/enums'
import variantValidatorResultsData from '@variantsTest/data/variant-validator.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

export default {
  title: 'Variants / Small Variant Details VariantValidator',
  component: VariantDetailsVariantValidator,
}

const Template = (args) => ({
  components: { VariantDetailsVariantValidator },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsVariantValidator\n' +
    '    :small-variant="args.smallVariant"\n' +
    '    v-model:variant-validator-state="args.variantValidatorState"\n' +
    '    v-model:variant-validator-results="args.variantValidatorResults"\n' +
    '/>',
})

export const Initial = Template.bind({})
Initial.args = {
  smallVariant: trioVariantsData[0],
  variantValidatorState: VariantValidatorStates.Initial,
  variantValidatorResults: null,
}

export const Running = Template.bind({})
Running.args = {
  smallVariant: trioVariantsData[0],
  variantValidatorState: VariantValidatorStates.Running,
  variantValidatorResults: null,
}

export const Done = Template.bind({})
Done.args = {
  smallVariant: trioVariantsData[0],
  variantValidatorState: VariantValidatorStates.Done,
  variantValidatorResults: variantValidatorResultsData,
}

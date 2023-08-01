import VariantDetailsFreqs from '@variants/components/VariantDetailsFreqs.vue'
import brca1SmallVar from '@variantsTest/data/data/var-brca1-missense-benign-smallvar.json'
import mtdnaSmallVar from '@variantsTest/data/data/var-brca1-missense-benign-smallvar.json'
import brca1VarAnnos from '@variantsTest/data/data/var-brca1-missense-benign-varanno.json'
import mtdnaVarAnnos from '@variantsTest/data/data/var-brca1-missense-benign-varannos.json'

export default {
  title: 'Variants / Small Variant Details Frequencies',
  component: VariantDetailsFreqs,
}

const Template = (args) => ({
  components: { VariantDetailsFreqs },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsFreqs\n' +
    '    :small-var="args.smallVar"\n' +
    '    :var-annos="args.varAnnos"\n' +
    '/>',
})

export const Autosomal = Template.bind({})
Autosomal.args = {
  smallVar: brca1SmallVar,
  varAnnos: brca1VarAnnos,
}

export const Mitochondrial = Template.bind({})
Mitochondrial.args = {
  smallVar: mtdnaSmallVar,
  varAnnos: mtdnaVarAnnos,
}

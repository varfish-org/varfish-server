import VariantDetailsTranscripts from './VariantDetailsTranscripts.vue'

export default {
  title: 'Variants / Small Variant Details Transcripts',
  component: VariantDetailsTranscripts,
}

const Template = (args) => ({
  components: { VariantDetailsTranscripts },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsTranscripts\n' +
    '    :effect-details="args.effectDetails"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  effectDetails: [
    {
      transcriptId: 'NM_002222.5',
      variantEffects: ['missense_variant'],
      hgvsNucleotides: 'c.6835C>T',
      hgvsProtein: 'p.(R2279W)',
    },
    {
      transcriptId: 'XM_005265109.1',
      variantEffects: ['stop_lost'],
      hgvsNucleotides: 'c.6955C>T',
      hgvsProtein: 'p.(R2319W)',
    },
    {
      transcriptId: 'XM_005265110.1',
      variantEffects: ['synonymous_variant'],
      hgvsNucleotides: 'c.6956C>T',
      hgvsProtein: 'p.(R2310W)',
    },
  ],
}

import SmallVariantDetailsTranscripts from './SmallVariantDetailsTranscripts.vue'

export default {
  title: 'Variants / Small Variant Details Transcripts',
  component: SmallVariantDetailsTranscripts,
}

const Template = (args) => ({
  components: { SmallVariantDetailsTranscripts },
  setup() {
    return { args }
  },
  template:
    '<SmallVariantDetailsTranscripts\n' +
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
      variantEffects: ['missense_variant'],
      hgvsNucleotides: 'c.6955C>T',
      hgvsProtein: 'p.(R2319W)',
    },
  ],
}

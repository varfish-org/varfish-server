import FilterFormEffectPane from '@/variants/components/FilterForm/EffectPane.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import querySettingsSingleton from '../../../data/query-settings-singleton.json'

describe('FilterFormEffectPane.vue', () => {
  test('effects advanced with help', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: true,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.findAll('input').length).toBe(47)
    expect(wrapper.findAll('.alert-secondary').length).toBe(6)
  })

  test('effects simple with help', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'simple',
        showFiltrationInlineHelp: true,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.findAll('input').length).toBe(13)
    expect(wrapper.findAll('.alert-secondary').length).toBe(5)

    const effectGroupAll = wrapper.find('#effect-group-all')
    const effectGroupNonsynonymous = wrapper.find('#effect-group-nonsynonymous')
    const effectGroupSplicing = wrapper.find('#effect-group-splicing')
    const effectGroupCoding = wrapper.find('#effect-group-coding')
    const effectGroupUtrIntronic = wrapper.find('#effect-group-utr_intronic')
    const effectGroupNoncoding = wrapper.find('#effect-group-noncoding')
    const effectGroupNonsense = wrapper.find('#effect-group-nonsense')

    await effectGroupAll.setValue()
    await effectGroupNonsynonymous.setValue()
    await effectGroupSplicing.setValue()
    await effectGroupCoding.setValue()
    await effectGroupUtrIntronic.setValue()
    await effectGroupNoncoding.setValue()
    await effectGroupNonsense.setValue()

    expect(effectGroupAll.element.checked).toBeTruthy()
    expect(effectGroupNonsynonymous.element.checked).toBeTruthy()
    expect(effectGroupSplicing.element.checked).toBeTruthy()
    expect(effectGroupCoding.element.checked).toBeTruthy()
    expect(effectGroupUtrIntronic.element.checked).toBeTruthy()
    expect(effectGroupNoncoding.element.checked).toBeTruthy()
    expect(effectGroupNonsense.element.checked).toBeTruthy()
  })

  test('effects normal', () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'normal',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.findAll('input').length).toBe(13)
    expect(wrapper.findAll('.alert-secondary').length).toBe(0)
  })

  test('effects variant types', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    const effectVartypesSnv = wrapper.find('#effect-vartypes-var_type_snv')
    const effectVartypesIndel = wrapper.find('#effect-vartypes-var_type_indel')
    const effectVartypesMnv = wrapper.find('#effect-vartypes-var_type_mnv')

    await effectVartypesMnv.setValue(false)

    expect(effectVartypesSnv.element.checked).toBeTruthy()
    expect(effectVartypesIndel.element.checked).toBeTruthy()
    expect(effectVartypesMnv.element.checked).toBeFalsy()
  })

  test('effects transcripts', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })
    const effectTranscriptsCoding = wrapper.find(
      '#effect-transcripts-transcripts_coding',
    )
    const effectTranscriptsNoncoding = wrapper.find(
      '#effect-transcripts-transcripts_noncoding',
    )

    await effectTranscriptsNoncoding.setValue()

    expect(effectTranscriptsCoding.element.checked).toBeTruthy()
    expect(effectTranscriptsNoncoding.element.checked).toBeTruthy()
  })

  test('effects maxexondist', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    const input = wrapper.get('#max-exon-dist')

    await input.setValue('123')

    expect(input.element.value).toBe('123')
  })

  test('effects detailed', async () => {
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    const detailedEffectDisruptiveInframeDeletion = wrapper.get(
      '#detailed-effect-disruptive_inframe_deletion',
    )
    const detailedEffectDisruptiveInframeInsertion = wrapper.get(
      '#detailed-effect-disruptive_inframe_insertion',
    )
    const detailedEffectFeatureTruncation = wrapper.get(
      '#detailed-effect-feature_truncation',
    )
    const detailedEffectFrameshiftElongation = wrapper.get(
      '#detailed-effect-frameshift_elongation',
    )
    const detailedEffectFrameshiftTruncation = wrapper.get(
      '#detailed-effect-frameshift_truncation',
    )
    const detailedEffectFrameshiftVariant = wrapper.get(
      '#detailed-effect-frameshift_variant',
    )
    const detailedEffectInframeDeletion = wrapper.get(
      '#detailed-effect-inframe_deletion',
    )
    const detailedEffectInframeInsertion = wrapper.get(
      '#detailed-effect-inframe_insertion',
    )
    const detailedEffectInternalFeatureElongation = wrapper.get(
      '#detailed-effect-internal_feature_elongation',
    )
    const detailedEffectMissenseVariant = wrapper.get(
      '#detailed-effect-missense_variant',
    )
    const detailedEffectMnv = wrapper.get('#detailed-effect-mnv')
    const detailedEffectStartLost = wrapper.get('#detailed-effect-start_lost')
    const detailedEffectStopGained = wrapper.get('#detailed-effect-stop_gained')
    const detailedEffectStopRetainedVariant = wrapper.get(
      '#detailed-effect-stop_retained_variant',
    )
    const detailedEffectStopLost = wrapper.get('#detailed-effect-stop_lost')
    const detailedEffectSynonymousVariant = wrapper.get(
      '#detailed-effect-synonymous_variant',
    )
    const detailedEffectDirectTandemDuplication = wrapper.get(
      '#detailed-effect-direct_tandem_duplication',
    )
    const detailedEffectDownstreamGeneVariant = wrapper.get(
      '#detailed-effect-downstream_gene_variant',
    )
    const detailedEffectCodingTranscriptIntronVariant = wrapper.get(
      '#detailed-effect-coding_transcript_intron_variant',
    )
    const detailedEffectIntergenicVariant = wrapper.get(
      '#detailed-effect-intergenic_variant',
    )
    const detailedEffectUpstreamGeneVariant = wrapper.get(
      '#detailed-effect-upstream_gene_variant',
    )
    const detailedEffectExonLossVariant = wrapper.get(
      '#detailed-effect-exon_loss_variant',
    )
    const detailedEffect3PrimeUTRExonVariant = wrapper.get(
      '#detailed-effect-3_prime_UTR_exon_variant',
    )
    const detailedEffect3PrimeUTRIntronVariant = wrapper.get(
      '#detailed-effect-3_prime_UTR_intron_variant',
    )
    const detailedEffect5PrimeUTRExonVariant = wrapper.get(
      '#detailed-effect-5_prime_UTR_exon_variant',
    )
    const detailedEffect5PrimeUTRIntronVariant = wrapper.get(
      '#detailed-effect-5_prime_UTR_intron_variant',
    )
    const detailedEffectNonCodingTranscriptExonVariant = wrapper.get(
      '#detailed-effect-non_coding_transcript_exon_variant',
    )
    const detailedEffectNonCodingTranscriptIntronVariant = wrapper.get(
      '#detailed-effect-non_coding_transcript_intron_variant',
    )
    const detailedEffectSpliceAcceptorVariant = wrapper.get(
      '#detailed-effect-splice_acceptor_variant',
    )
    const detailedEffectSpliceDonorVariant = wrapper.get(
      '#detailed-effect-splice_donor_variant',
    )
    const detailedEffectSpliceRegionVariant = wrapper.get(
      '#detailed-effect-splice_region_variant',
    )
    const detailedEffectStructuralVariant = wrapper.get(
      '#detailed-effect-structural_variant',
    )
    const detailedEffectTranscriptAblation = wrapper.get(
      '#detailed-effect-transcript_ablation',
    )
    const detailedEffectComplexSubstitution = wrapper.get(
      '#detailed-effect-complex_substitution',
    )

    await detailedEffectDisruptiveInframeDeletion.setValue()
    await detailedEffectDisruptiveInframeInsertion.setValue()
    await detailedEffectFeatureTruncation.setValue()
    await detailedEffectFrameshiftElongation.setValue()
    await detailedEffectFrameshiftTruncation.setValue()
    await detailedEffectFrameshiftVariant.setValue()
    await detailedEffectInframeDeletion.setValue()
    await detailedEffectInframeInsertion.setValue()
    await detailedEffectMissenseVariant.setValue()
    await detailedEffectMnv.setValue()
    await detailedEffectInternalFeatureElongation.setValue()
    await detailedEffectStartLost.setValue()
    await detailedEffectStopGained.setValue()
    await detailedEffectStopRetainedVariant.setValue()
    await detailedEffectStopLost.setValue()
    await detailedEffectSynonymousVariant.setValue()
    await detailedEffectDirectTandemDuplication.setValue()
    await detailedEffectDownstreamGeneVariant.setValue()
    await detailedEffectCodingTranscriptIntronVariant.setValue()
    await detailedEffectIntergenicVariant.setValue()
    await detailedEffectUpstreamGeneVariant.setValue()
    await detailedEffectExonLossVariant.setValue()
    await detailedEffect3PrimeUTRExonVariant.setValue()
    await detailedEffect3PrimeUTRIntronVariant.setValue()
    await detailedEffect5PrimeUTRExonVariant.setValue()
    await detailedEffect5PrimeUTRIntronVariant.setValue()
    await detailedEffectNonCodingTranscriptExonVariant.setValue()
    await detailedEffectNonCodingTranscriptIntronVariant.setValue()
    await detailedEffectSpliceAcceptorVariant.setValue()
    await detailedEffectSpliceDonorVariant.setValue()
    await detailedEffectSpliceRegionVariant.setValue()
    await detailedEffectStructuralVariant.setValue()
    await detailedEffectTranscriptAblation.setValue()
    await detailedEffectComplexSubstitution.setValue()

    expect(detailedEffectDisruptiveInframeDeletion.element.checked).toBeTruthy()
    expect(
      detailedEffectDisruptiveInframeInsertion.element.checked,
    ).toBeTruthy()
    expect(detailedEffectFeatureTruncation.element.checked).toBeTruthy()
    expect(detailedEffectFrameshiftElongation.element.checked).toBeTruthy()
    expect(detailedEffectFrameshiftTruncation.element.checked).toBeTruthy()
    expect(detailedEffectFrameshiftVariant.element.checked).toBeTruthy()
    expect(detailedEffectInframeDeletion.element.checked).toBeTruthy()
    expect(detailedEffectInframeInsertion.element.checked).toBeTruthy()
    expect(detailedEffectMissenseVariant.element.checked).toBeTruthy()
    expect(detailedEffectMnv.element.checked).toBeTruthy()
    expect(detailedEffectInternalFeatureElongation.element.checked).toBeTruthy()
    expect(detailedEffectStartLost.element.checked).toBeTruthy()
    expect(detailedEffectStopGained.element.checked).toBeTruthy()
    expect(detailedEffectStopRetainedVariant.element.checked).toBeTruthy()
    expect(detailedEffectStopLost.element.checked).toBeTruthy()
    expect(detailedEffectSynonymousVariant.element.checked).toBeTruthy()
    expect(detailedEffectDirectTandemDuplication.element.checked).toBeTruthy()
    expect(detailedEffectDownstreamGeneVariant.element.checked).toBeTruthy()
    expect(
      detailedEffectCodingTranscriptIntronVariant.element.checked,
    ).toBeTruthy()
    expect(detailedEffectIntergenicVariant.element.checked).toBeTruthy()
    expect(detailedEffectUpstreamGeneVariant.element.checked).toBeTruthy()
    expect(detailedEffectExonLossVariant.element.checked).toBeTruthy()
    expect(detailedEffect3PrimeUTRExonVariant.element.checked).toBeTruthy()
    expect(detailedEffect3PrimeUTRIntronVariant.element.checked).toBeTruthy()
    expect(detailedEffect5PrimeUTRExonVariant.element.checked).toBeTruthy()
    expect(detailedEffect5PrimeUTRIntronVariant.element.checked).toBeTruthy()
    expect(
      detailedEffectNonCodingTranscriptExonVariant.element.checked,
    ).toBeTruthy()
    expect(
      detailedEffectNonCodingTranscriptIntronVariant.element.checked,
    ).toBeTruthy()
    expect(detailedEffectSpliceAcceptorVariant.element.checked).toBeTruthy()
    expect(detailedEffectSpliceDonorVariant.element.checked).toBeTruthy()
    expect(detailedEffectSpliceRegionVariant.element.checked).toBeTruthy()
    expect(detailedEffectStructuralVariant.element.checked).toBeTruthy()
    expect(detailedEffectTranscriptAblation.element.checked).toBeTruthy()
    expect(detailedEffectComplexSubstitution.element.checked).toBeTruthy()
  })

  test('effects empty', () => {
    querySettingsSingleton.effects = null
    shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })
  })

  test('effects trying to get coverage of lines 36-38 but it doesnt work', async () => {
    querySettingsSingleton.effects = null
    const wrapper = shallowMount(FilterFormEffectPane, {
      props: {
        filtrationComplexityMode: 'advanced',
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    await wrapper
      .get('#detailed-effect-disruptive_inframe_deletion')
      .setValue(false)
  })
})

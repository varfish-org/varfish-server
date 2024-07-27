import isEqual from 'fast-deep-equal/es6'
import { Component } from 'vue'

import { LocalFields, Query } from '@/seqvars/types'
import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import ClinvarControls from './ClinvarControls.vue'
import EffectsControls from './EffectsControls.vue'
import FrequencyControls from './frequency/FrequencyControls.vue'
import { GENOTYPE_PRESETS, Pedigree } from './genotype/constants'
import LocusControls from './LocusControls.vue'
import PathogenicityPrioControls from './PathogenicityPrioControls.vue'
import PhenotypePrioControls from './PhenotypePrioControls.vue'
import QualityControls from './QualityControls.vue'
import { isKeyOfObject } from './utils'

type PresetDetails = SeqvarsQueryPresetsSetVersionDetails

const getPresetSetKey = <S extends string>(id: S) =>
  `seqvarsquerypresets${id}_set` as const

type QueryKey = keyof Query & keyof SeqvarsPredefinedQuery

type GetCompareFields<Id extends keyof Query, Preset> = (
  v: LocalFields<Query[Id]> & Preset,
) => unknown[]

export class FilterGroup<
  Id extends QueryKey,
  PresetSetKey extends ReturnType<typeof getPresetSetKey<Id>>,
  Preset extends PresetSetKey extends keyof PresetDetails
    ? PresetDetails[PresetSetKey][number]
    : LocalFields<Query[Id]>,
> {
  id: Id
  title: string
  getCompareFields: GetCompareFields<Id, Preset>
  Component: Component

  constructor(params: {
    id: Id
    title: string
    getCompareFields: GetCompareFields<Id, Preset>
    Component: Component
  }) {
    this.id = params.id
    this.title = params.title
    this.getCompareFields = params.getCompareFields
    this.Component = params.Component
  }

  get queryPresetKey() {
    return `${this.id}presets` as const
  }

  get presetSetKey() {
    return `seqvarsquerypresets${this.id}_set` as const
  }

  matchesPreset(presetDetails: PresetDetails, query: Query): boolean {
    if (!isKeyOfObject(this.presetSetKey, presetDetails)) return false
    const preset = presetDetails[this.presetSetKey].find(
      (p) =>
        isKeyOfObject(this.queryPresetKey, query) &&
        p.sodar_uuid === query[this.queryPresetKey],
    )
    return isEqual(
      this.getCompareFields(query[this.id] as any),
      this.getCompareFields(preset as any),
    )
  }
}

export const GROUPS = [
  new FilterGroup({
    id: 'frequency',
    title: 'Frequency',
    getCompareFields: (v) => [
      v.gnomad_exomes,
      v.gnomad_genomes,
      v.gnomad_mitochondrial,
      v.helixmtdb,
      v.inhouse,
    ],
    Component: FrequencyControls,
  }),

  new FilterGroup({
    id: 'phenotypeprio',
    title: 'Phenotype Priorization',
    getCompareFields: (v) => [
      v.phenotype_prio_enabled,
      v.phenotype_prio_algorithm,
      v.terms,
    ],
    Component: PhenotypePrioControls,
  }),

  new FilterGroup({
    id: 'variantprio',
    title: 'Pathogenicity Priorization',
    getCompareFields: (v) => [v.variant_prio_enabled, v.services],
    Component: PathogenicityPrioControls,
  }),

  new FilterGroup({
    id: 'consequence',
    title: 'Effects',
    getCompareFields: (v) => [
      v.max_distance_to_exon,
      new Set(v.variant_types),
      new Set(v.transcript_types),
      new Set(v.variant_consequences),
    ],
    Component: EffectsControls,
  }),

  new FilterGroup({
    id: 'quality',
    title: 'Quality',
    getCompareFields: (v) =>
      (v.sample_quality_filters ?? []).flatMap((v) => [
        v.filter_active,
        v.max_ad,
        v.min_ab_het,
        v.min_ad,
        v.min_dp_het,
        v.min_dp_hom,
        v.min_gq,
      ]),
    Component: QualityControls,
  }),

  new FilterGroup({
    id: 'clinvar',
    title: 'ClinVar',
    getCompareFields: (v) => [
      v.allow_conflicting_interpretations,
      new Set(v.clinvar_germline_aggregate_description),
      v.clinvar_presence_required,
    ],
    Component: ClinvarControls,
  }),

  new FilterGroup({
    id: 'locus',
    title: 'Genes or Regions',
    getCompareFields: (v) => [v.gene_panels, v.genes, v.genome_regions],
    Component: LocusControls,
  }),
]

export const createGenotypeFromPreset = (
  choice?: SeqvarsGenotypePresetChoice | null,
) => {
  const preset = GENOTYPE_PRESETS[choice ?? 'any']
  return {
    recessive_mode: preset.recessiveMode,
    sample_genotype_choices: (['index', 'father', 'mother'] as Pedigree[]).map(
      (sample) => ({
        enabled: true,
        sample,
        genotype: preset.samples[sample],
        include_no_call: false,
      }),
    ),
  }
}

const getGenotypeCompareField = (v: Query['genotype']) => [
  v.recessive_mode,
  v.sample_genotype_choices,
]

export const matchesGenotypePreset = (
  presetChoice: SeqvarsGenotypePresetChoice | null | undefined,
  query: Query,
) =>
  isEqual(
    getGenotypeCompareField(query.genotype),
    getGenotypeCompareField(createGenotypeFromPreset(presetChoice)),
  )

export const createQualityFromPreset = (
  preset: SeqvarsQueryPresetsQuality,
) => ({
  ...preset,
  sample_quality_filters: ['index', 'father', 'mother'].map((sample) => ({
    sample,
    ...preset,
  })),
})

export const matchesQualityPreset = (
  presetDetails: SeqvarsQueryPresetsSetVersionDetails,
  query: Query,
) => {
  const preset = presetDetails.seqvarsquerypresetsquality_set.find(
    (p) => p.sodar_uuid === query.qualitypresets,
  )
  return !!preset && isEqual(query.quality, createQualityFromPreset(preset))
}

export const matchesPredefinedQuery = (
  presetDetails: SeqvarsQueryPresetsSetVersionDetails,
  pq: SeqvarsPredefinedQuery,
  query: Query,
) =>
  matchesGenotypePreset(pq.genotype?.choice, query) &&
  GROUPS.every((group) =>
    group.id == 'quality'
      ? matchesQualityPreset(presetDetails, query)
      : group.matchesPreset(presetDetails, query),
  )

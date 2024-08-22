import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsQuerySettingsGenotypeRequest,
  SeqvarsQuerySettingsQualityRequest,
} from '@varfish-org/varfish-api/lib'
import isEqual from 'fast-deep-equal/es6'
import { Component } from 'vue'

import { PedigreeObj } from '@/cases/stores/caseDetails'
import { LocalFields, Query } from '@/seqvars/types'

import { isKeyOfObject } from '../utils'
import ClinvarControls from './ClinvarControls.vue'
import EffectsControls from './EffectsControls.vue'
import FrequencyControls from './FrequencyControls.vue'
import LocusControls from './LocusControls.vue'
import PathogenicityPrioControls from './PathogenicityPrioControls.vue'
import PhenotypePrioControls from './PhenotypePrioControls.vue'
import QualityControls from './QualityControls.vue'
import { GENOTYPE_PRESET_TO_RECESSIVE_MODE } from './constants'
import { presetChoiceToGenotypeChoice } from './lib'

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
  hint?: string

  constructor(params: {
    id: Id
    title: string
    getCompareFields: GetCompareFields<Id, Preset>
    Component: Component
    hint?: string
  }) {
    this.id = params.id
    this.title = params.title
    this.getCompareFields = params.getCompareFields
    this.Component = params.Component
    this.hint = params.hint
  }

  get queryPresetKey() {
    return `${this.id}presets` as const
  }

  get presetSetKey() {
    return `seqvarsquerypresets${this.id}_set` as const
  }

  matchesPreset(presetsDetails: PresetDetails, query: Query): boolean {
    if (!isKeyOfObject(this.presetSetKey, presetsDetails)) return false
    const preset = presetsDetails[this.presetSetKey].find(
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
  pedigree: PedigreeObj,
  choice?: SeqvarsGenotypePresetChoice | null,
): SeqvarsQuerySettingsGenotypeRequest => {
  const choice$ = choice ?? 'any'
  const recessiveMode = GENOTYPE_PRESET_TO_RECESSIVE_MODE[choice$]
  const result: SeqvarsQuerySettingsGenotypeRequest = {
    recessive_mode: recessiveMode,
    sample_genotype_choices: presetChoiceToGenotypeChoice(pedigree, choice$),
  }
  return result
}

const getGenotypeCompareField = (v: Query['genotype']) => [
  v.recessive_mode,
  v.sample_genotype_choices,
]

export const matchesGenotypePreset = (
  pedigree: PedigreeObj,
  presetChoice: SeqvarsGenotypePresetChoice | null | undefined,
  query: Query,
): boolean => {
  return isEqual(
    getGenotypeCompareField(query.genotype),
    getGenotypeCompareField(createGenotypeFromPreset(pedigree, presetChoice)),
  )
}

export const createQualityFromPreset = (
  pedigree: PedigreeObj,
  preset: SeqvarsQueryPresetsQuality,
): SeqvarsQuerySettingsQualityRequest => {
  const sampleNames = pedigree.individual_set.map(
    (individual) => individual.name,
  )
  return {
    ...preset,
    sample_quality_filters: sampleNames.map((sample) => ({
      sample,
      ...preset,
    })),
  }
}

export const matchesQualityPreset = (
  pedigree: PedigreeObj,
  presetsDetails: SeqvarsQueryPresetsSetVersionDetails,
  query: Query,
): boolean => {
  const preset = presetsDetails.seqvarsquerypresetsquality_set.find(
    (p) => p.sodar_uuid === query.qualitypresets,
  )
  return (
    !!preset &&
    isEqual(query.quality, createQualityFromPreset(pedigree, preset))
  )
}

export const matchesPredefinedQuery = (
  pedigree: PedigreeObj,
  presetsDetails: SeqvarsQueryPresetsSetVersionDetails,
  pq: SeqvarsPredefinedQuery,
  query: Query,
): boolean =>
  matchesGenotypePreset(pedigree, pq.genotype?.choice, query) &&
  GROUPS.every((group) => {
    // Check whether the lower-level values match.
    const valuesMatch =
      group.id == 'quality'
        ? matchesQualityPreset(pedigree, presetsDetails, query)
        : group.matchesPreset(presetsDetails, query)
    // Check that the selected category entry matches the one from the
    // used predefined query.
    const predefinedQuery = presetsDetails.seqvarspredefinedquery_set.find(
      (p) => p.sodar_uuid === pq.sodar_uuid,
    )
    const categoriesMatch =
      !!predefinedQuery?.[group.id] &&
      !!query?.[group.queryPresetKey] &&
      predefinedQuery[group.id] === query[group.queryPresetKey]
    // Return AND of both checks.
    return valuesMatch && categoriesMatch
  })

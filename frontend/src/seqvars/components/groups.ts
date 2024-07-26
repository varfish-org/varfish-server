import { Query } from '@/seqvars/types'
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import ClinvarControls from './ClinvarControls.vue'
import EffectsControls from './EffectsControls.vue'
import { FilterGroup } from './FilterGroup'
import FrequencyControls from './frequency/FrequencyControls.vue'
import { genotypeFilterGroup } from './genotype/group'
import LocusControls from './LocusControls.vue'
import PathogenicityPrioControls from './PathogenicityPrioControls.vue'
import PhenotypePrioControls from './PhenotypePrioControls.vue'
import QualityControls from './QualityControls.vue'

export const GROUPS = [
  genotypeFilterGroup,

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
    createFromPreset: (preset) => ({
      ...preset,
      sample_quality_filters: ['index', 'father', 'mother'].map((sample) => ({
        sample,
        ...preset,
      })),
    }),
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

export const matchesPredefinedQuery = (
  presetDetails: SeqvarsQueryPresetsSetVersionDetails,
  pq: SeqvarsPredefinedQuery,
  query: Query,
) => GROUPS.every((group) => group.matchesPreset(presetDetails, pq, query))

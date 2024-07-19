import { SeqvarsSampleGenotypeChoiceList } from '@varfish-org/varfish-api/lib'

type SampleId = string

type GenotypeRecessiveFilter = {
  mode: 'recessive' | 'comphet' | 'homozygous'
  index?: SampleId
  parents?: [SampleId, SampleId]
}

type GenotypeSampleFilter = {
  samples: Array<{
    sample: SampleId
    modes: Set<'wild' | 'het' | 'hom' | 'no_call'>
  }>
}

export type GenotypeFilter = GenotypeRecessiveFilter | GenotypeSampleFilter

// Case 1: recessive mode
;[
  {
    sample: 'ProbandChild',
    genotype: 'recessive_index',
  },
  {
    sample: 'ProbandFather',
    genotype: 'recessive_parent',
  },
  {
    sample: 'ProbandMother',
    genotype: 'recessive_parent',
  },
] satisfies SeqvarsSampleGenotypeChoiceList
// (in my)
;({
  mode: 'recessive',
  index: 'ProbandChild',
  parents: ['ProbandFather', 'ProbandMother'],
}) satisfies GenotypeRecessiveFilter

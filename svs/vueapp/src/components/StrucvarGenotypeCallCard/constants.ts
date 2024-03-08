import { GenotypeFieldDescription } from './types'

export const GT_FIELD_DESCRIPTIONS: GenotypeFieldDescription[] = [
  { name: 'copy_number', label: 'copy number' },
  { name: 'quality', label: 'genotype quality' },
  { name: 'genotype', label: 'genotype call' },
  { name: 'paired_end_cov', label: 'total read pairs' },
  { name: 'paired_end_var', label: 'variant read pairs' },
  { name: 'split_read_cov', label: 'total split-reads' },
  { name: 'split_read_var', label: 'variant split reads' },
  { name: 'point_count', label: 'number of bins/targets' },
  { name: 'average_normalized_cov', label: 'average normalized coverage' },
  { name: 'average_mapping_quality', label: 'average mapping quality' },
  {
    name: 'matched_gt_criteria',
    label: 'matched genotype criteria',
    fmt: (val: string | string[]) => {
      if (Array.isArray(val)) {
        return val.join(', ')
      } else {
        return val
      }
    },
  },
  { name: 'effective_genotype', label: 'effective genotype' },
] as const

export const GET_FIELD_MAP: { [key: string]: GenotypeFieldDescription } =
  Object.fromEntries(GT_FIELD_DESCRIPTIONS.map((desc) => [desc.name, desc]))

export const identity = <T>(x: T): T => {
  return x
}

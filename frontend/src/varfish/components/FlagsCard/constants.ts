/** Boolean flag specification for the `FlagsCard` */
export interface BooleanFlagSpec {
  label: string
  icon: string
  key:
    | 'flag_bookmarked'
    | 'flag_incidental'
    | 'flag_for_validation'
    | 'flag_candidate'
    | 'flag_final_causative'
    | 'flag_no_disease_association'
    | 'flag_segregates'
    | 'flag_doesnt_segregate'
}

/** The boolean flags to display in the `FlagsCard`. */
export const BOOLEAN_FLAGS: BooleanFlagSpec[] = [
  {
    label: 'starred',
    icon: 'mdi-star',
    key: 'flag_bookmarked',
  },
  {
    label: 'for validation',
    icon: 'mdi-flask-empty',
    key: 'flag_for_validation',
  },
  {
    label: 'incidental finding',
    icon: 'mdi-dice-5',
    key: 'flag_incidental',
  },
  {
    label: 'candidate',
    icon: 'mdi-cards-heart',
    key: 'flag_candidate',
  },
  {
    label: 'final causative',
    icon: 'mdi-flag-checkered',
    key: 'flag_final_causative',
  },
  {
    label: 'no disease association',
    icon: 'mdi-link-variant-off',
    key: 'flag_no_disease_association',
  },
  {
    label: 'segregates',
    icon: 'mdi-thumb-up',
    key: 'flag_segregates',
  },
  {
    label: 'does not segregate',
    icon: 'mdi-thumb-down',
    key: 'flag_doesnt_segregate',
  },
]

/** Color specificaiton. */
export interface ColorSpec {
  label: string
  value: string
  color: string
  icon: string
}

/** Value for a color flag. */
export const COLOR_VALUES: ColorSpec[] = [
  {
    label: 'positive',
    value: 'positive',
    color: 'red',
    icon: 'mdi-alert-circle',
  },
  {
    label: 'uncertain',
    value: 'uncertain',
    color: 'yellow',
    icon: 'mdi-help-circle',
  },
  {
    label: 'negative',
    value: 'negative',
    color: 'green',
    icon: 'mdi-minus-circle',
  },
  {
    label: 'empty',
    value: 'empty',
    color: 'grey',
    icon: 'mdi-close-circle-outline',
  },
]

/** Specification of a color flag. */
export interface ColorFlagSpec {
  label: string
  key:
    | 'flag_visual'
    | 'flag_molecular'
    | 'flag_phenotype_match'
    | 'flag_summary'
}

/** The color flags to display in the `FlagsCard`. */
export const COLOR_FLAGS: ColorFlagSpec[] = [
  {
    label: 'Visual',
    key: 'flag_visual',
  },
  {
    label: 'Molecular',
    key: 'flag_molecular',
  },
  {
    label: 'Phenotype match',
    key: 'flag_phenotype_match',
  },
  {
    label: 'Summary',
    key: 'flag_summary',
  },
]

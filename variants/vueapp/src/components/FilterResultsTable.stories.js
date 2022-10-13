import trioCaseData from '@variantsTest/data/case-trio.json'
import trioVariantsData from '@variantsTest/data/variants-trio.json'

import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
} from '../enums.js'
import FilterResultsTable from './FilterResultsTable.vue'

export default {
  title: 'Variants / Result Table',
  component: FilterResultsTable,
}

const Template = (args) => ({
  components: { FilterResultsTable },
  setup() {
    return { args }
  },
  template:
    '<FilterResultsTable\n' +
    '    :case="args.case"\n' +
    '    :query-results="args.queryResults"\n' +
    '    v-model:display-details="args.displayDetails"\n' +
    '    v-model:display-frequency="args.displayFrequency"\n' +
    '    v-model:display-constraint="args.displayConstraint"\n' +
    '    v-model:display-columns="args.displayColumns"\n' +
    '/>',
})

export const NormalView = Template.bind({})
NormalView.args = {
  case: trioCaseData,
  queryResults: trioVariantsData,
  displayDetails: DisplayDetails.Coordinates.value,
  displayFrequency: DisplayFrequencies.GnomadExomes.value,
  displayConstraint: DisplayConstraints.GnomadLoeuf.value,
  displayColumns: [DisplayColumns.DistanceSplicesite.value],
}

export const ClinvarView = Template.bind({})
ClinvarView.args = {
  case: trioCaseData,
  queryResults: trioVariantsData,
  displayDetails: DisplayDetails.Clinvar.value,
  displayFrequency: DisplayFrequencies.GnomadExomes.value,
  displayConstraint: DisplayConstraints.GnomadLoeuf.value,
  displayColumns: [],
}

import { reactive } from 'vue'

import FilterFormClinvarPane from './FilterFormClinvarPane.vue'

export default {
  title: 'Variants / Filter Form ClinVar',
  component: FilterFormClinvarPane,
}

const Template = (args) => ({
  components: { FilterFormClinvarPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormClinvarPane\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  showFiltrationInlineHelp: false,
  querySettings: reactive({
    require_in_clinvar: true,
    clinvar_paranoid_mode: false,
    clinvar_include_pathogenic: true,
    clinvar_include_likely_pathogenic: true,
    clinvar_include_uncertain_significance: false,
    clinvar_include_likely_benign: false,
    clinvar_include_benign: false,
  }),
}

export const Disabled = Template.bind({})
Disabled.args = {
  showFiltrationInlineHelp: false,
  querySettings: reactive({
    require_in_clinvar: false,
    clinvar_paranoid_mode: true,
    clinvar_include_pathogenic: true,
    clinvar_include_likely_pathogenic: true,
    clinvar_include_uncertain_significance: false,
    clinvar_include_likely_benign: false,
    clinvar_include_benign: false,
  }),
}

export const WithHelp = Template.bind({})
WithHelp.args = {
  showFiltrationInlineHelp: true,
  querySettings: reactive({
    require_in_clinvar: true,
    clinvar_paranoid_mode: true,
    clinvar_include_pathogenic: true,
    clinvar_include_likely_pathogenic: true,
    clinvar_include_uncertain_significance: true,
    clinvar_include_likely_benign: true,
    clinvar_include_benign: true,
  }),
}

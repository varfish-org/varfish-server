import FilterFormGenotypePane from '@/variants/components/FilterForm/GenotypePane.vue'
import singletonCaseData from '@tests/variants/data/case-singleton.json'
import trioCaseData from '@tests/variants/data/case-trio.json'
import querySettingsSingleton from '@tests/variants/data/query-settings-singleton.json'
import querySettingsTrio from '@tests/variants/data/query-settings-trio.json'
import { reactive } from 'vue'

export default {
  title: 'Variants / Filter Form Genotype',
  component: FilterFormGenotypePane,
}

const Template = (args) => ({
  components: { FilterFormGenotypePane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormGenotypePane\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :case="args.case"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const Trio = Template.bind({})
Trio.args = {
  showFiltrationInlineHelp: false,
  case: trioCaseData,
  querySettings: reactive(querySettingsTrio),
}

export const Singleton = Template.bind({})
Singleton.args = {
  showFiltrationInlineHelp: false,
  case: singletonCaseData,
  querySettings: reactive(querySettingsSingleton),
}

export const TrioWithHelp = Template.bind({})
TrioWithHelp.args = {
  showFiltrationInlineHelp: true,
  case: trioCaseData,
  querySettings: reactive(querySettingsTrio),
}

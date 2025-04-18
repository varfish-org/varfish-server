import singletonCaseData from '@tests/variants/data/case-singleton.json'
import querySettingsSingleton from '@tests/variants/data/query-settings-singleton.json'

import FilterFormFrequencyPane from '@/variants/components/FilterForm/FrequencyPane.vue'

export default {
  title: 'Variants / Filter Form Frequency',
  component: FilterFormFrequencyPane,
}

const Template = (args) => ({
  components: { FilterFormFrequencyPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormFrequencyPane\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :case="args.case"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const Example = Template.bind({})
Example.args = {
  showFiltrationInlineHelp: false,
  case: singletonCaseData,
  querySettings: querySettingsSingleton,
}

export const WithHelp = Template.bind({})
WithHelp.args = {
  showFiltrationInlineHelp: true,
  case: singletonCaseData,
  querySettings: querySettingsSingleton,
}

export const Grch38 = Template.bind({})
Grch38.args = {
  showFiltrationInlineHelp: true,
  case: { ...singletonCaseData, release: 'GRCh38' },
  querySettings: querySettingsSingleton,
}

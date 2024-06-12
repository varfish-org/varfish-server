import FilterFormQualityPane from '@/variants/components/FilterForm/QualityPane.vue'
import singletonCaseData from '@/variantsTest/data/case-singleton.json'
import trioCaseData from '@/variantsTest/data/case-trio.json'
import querySettingsSingleton from '@/variantsTest/data/query-settings-singleton.json'
import querySettingsTrio from '@/variantsTest/data/query-settings-trio.json'
import { reactive } from 'vue'

export default {
  title: 'Variants / Filter Form Quality',
  component: FilterFormQualityPane,
}

const Template = (args) => ({
  components: { FilterFormQualityPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormQualityPane\n' +
    '    :filtration-complexity-mode="args.filtrationComplexityMode"\n' +
    '    :case-obj="args.caseObj"\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const SingletonWithHelp = Template.bind({})
SingletonWithHelp.args = {
  showFiltrationInlineHelp: true,
  caseObj: singletonCaseData,
  querySettings: reactive(querySettingsSingleton),
}

export const Trio = Template.bind({})
Trio.args = {
  showFiltrationInlineHelp: false,
  caseObj: trioCaseData,
  querySettings: reactive(querySettingsTrio),
}

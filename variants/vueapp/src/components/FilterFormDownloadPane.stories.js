import singletonCaseData from '@variantsTest/data/case-singleton.json'
import trioCaseData from '@variantsTest/data/case-trio.json'
import exportSettingsSingleton from '@variantsTest/data/export-settings-singleton.json'
import exportSettingsTrio from '@variantsTest/data/export-settings-trio.json'

import FilterFormDownloadPane from './FilterFormDownloadPane.vue'

export default {
  title: 'Variants / Filter Form Configure Download',
  component: FilterFormDownloadPane,
}

const Template = (args) => ({
  components: { FilterFormDownloadPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormDownloadPane\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :case="args.case"\n' +
    '    :export-settings="args.exportSettings"\n' +
    '/>',
})

export const Trio = Template.bind({})
Trio.args = {
  showFiltrationInlineHelp: false,
  case: trioCaseData,
  exportSettings: exportSettingsTrio,
}

export const SingletonWithHelp = Template.bind({})
SingletonWithHelp.args = {
  showFiltrationInlineHelp: true,
  case: singletonCaseData,
  exportSettings: exportSettingsSingleton,
}

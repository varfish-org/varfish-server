import FilterFormEffectPane from '@variants/components/FilterFormEffectPane.vue'
import querySettingsSingleton from '@variantsTest/data/query-settings-singleton.json'

export default {
  title: 'Variants / Filter Form Effect',
  component: FilterFormEffectPane,
}

const Template = (args) => ({
  components: { FilterFormEffectPane },
  setup() {
    return { args }
  },
  template:
    '<FilterFormEffectPane\n' +
    '    :filtration-complexity-mode="args.filtrationComplexityMode"\n' +
    '    :show-filtration-inline-help="args.showFiltrationInlineHelp"\n' +
    '    :query-settings="args.querySettings"\n' +
    '/>',
})

export const Advanced = Template.bind({})
Advanced.args = {
  filtrationComplexityMode: 'advanced',
  showFiltrationInlineHelp: false,
  querySettings: querySettingsSingleton,
}

export const AdvancedWithHelp = Template.bind({})
AdvancedWithHelp.args = {
  filtrationComplexityMode: 'advanced',
  showFiltrationInlineHelp: true,
  querySettings: querySettingsSingleton,
}

export const Simple = Template.bind({})
Simple.args = {
  filtrationComplexityMode: 'simple',
  showFiltrationInlineHelp: false,
  querySettings: querySettingsSingleton,
}

export const Normal = Template.bind({})
Normal.args = {
  filtrationComplexityMode: 'normal',
  showFiltrationInlineHelp: false,
  querySettings: querySettingsSingleton,
}

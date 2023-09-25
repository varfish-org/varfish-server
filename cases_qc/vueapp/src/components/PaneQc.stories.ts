import PaneQc from '@cases_qc/components/PaneQc.vue'

import { storyData } from './PaneQc.stories.data'

export default {
  title: 'Case Details / QC Pane',
  component: PaneQc,
}

const Template = (args) => ({
  components: { PaneQc },
  setup() {
    return { args }
  },
  template:
    '<div style="width: 400px; height: 400px;">' +
    '<PaneQc\n' +
    '    :stats="args.stats"\n' +
    '/>' +
    '</div>',
})

export const Empty = Template.bind({})
Empty.args = {
  stats: null,
}

export const Dragen = Template.bind({})
Dragen.args = {
  stats: storyData.dragen,
}

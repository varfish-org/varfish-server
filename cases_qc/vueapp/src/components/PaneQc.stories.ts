import PaneQc from '@cases_qc/components/PaneQc.vue'

import { storyData } from './PaneQc.stories.data'

export default {
  title: 'Case Details / QC Pane',
  component: PaneQc,
}

const Template = (args: any) => ({
  components: { PaneQc },
  setup() {
    return { args }
  },
  template:
    '<div>' + '<PaneQc\n' + '    :stats="args.stats"\n' + '/>' + '</div>',
})

export const Empty = Template.bind({})
// @ts-ignore
Empty.args = {
  stats: null,
}

export const Dragen = Template.bind({})
// @ts-ignore
Dragen.args = {
  stats: storyData.dragen,
}

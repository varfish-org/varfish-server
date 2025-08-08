import DistDensPlot from '@/cases_qc/components/DistDensPlot.vue'

import { storyData } from './DistDens.stories.data'

export default {
  title: 'Plots / Distribution Density',
  component: DistDensPlot,
}

const Template = (args: any) => ({
  components: { DistDensPlot },
  setup() {
    return { args }
  },
  template:
    '<div style="width: 400px; height: 400px;">' +
    '<DistDensPlot\n' +
    '    title="insert size distribution"\n' +
    '    :datasets="args.datasets"\n' +
    '    x-label="insert size (bp)"\n' +
    '    y-label="frequency"\n' +
    '    :x-min="0"\n' +
    '    :x-max="1000"\n' +
    '/>' +
    '</div>',
})

export const InsertSizes = Template.bind({})
// @ts-ignore
InsertSizes.args = {
  datasets: [storyData.isize],
}

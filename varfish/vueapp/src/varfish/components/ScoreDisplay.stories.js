import ScoreDisplay from './ScoreDisplay.vue'

export default {
  title: 'Score Display',
  component: ScoreDisplay,
}

const Template = (args) => ({
  components: { ScoreDisplay },
  setup() {
    return { args }
  },
  template:
    '<div style="width: 100px; height: 50px;">' +
    '<ScoreDisplay\n' +
    '    :width="100"\n' +
    '    :height="20"\n' +
    '    :disp-trans-mult="args.dispTransMult"\n' +
    '    :disp-trans-offset="args.dispTransOffset"\n' +
    '    :range-lower="args.rangeLower"\n' +
    '    :range-upper="args.rangeUpper"\n' +
    '    :value="args.value"\n' +
    '    :benign-very-strong-upper="args.benignVeryStrongUpper"\n' +
    '    :benign-strong-upper="args.benignStrongUpper"\n' +
    '    :benign-moderate-upper="args.benignModerateUpper"\n' +
    '    :benign-supporting-upper="args.benignSupportingUpper"\n' +
    '    :pathogenic-supporting-lower="args.pathogenicSupportingLower"\n' +
    '    :pathogenic-moderate-lower="args.pathogenicModerateLower"\n' +
    '    :pathogenic-strong-lower="args.pathogenicStrongLower"\n' +
    '    :pathogenic-very-strong-lower="args.pathogenicVeryStrongLower"\n' +
    '/>' +
    '</div>',
})

export const Minimal = Template.bind({})
Minimal.args = {
  rangeLower: 0,
  rangeUpper: 1,
  value: 0.5,
}

export const Full = Template.bind({})
Full.args = {
  rangeLower: 0,
  rangeUpper: 1,
  value: 0.95,
  benignVeryStrongUpper: 0.1,
  benignStrongUpper: 0.2,
  benignModerateUpper: 0.3,
  benignSupportingUpper: 0.4,
  pathogenicSupportingLower: 0.6,
  pathogenicModerateLower: 0.7,
  pathogenicStrongLower: 0.8,
  pathogenicVeryStrongLower: 0.9,
}

export const Sift = Template.bind({})
Sift.args = {
  rangeLower: 0,
  rangeUpper: 1,
  dispTransOffset: 1,
  dispTransMult: -1,
  value: 0.95,
  benignModerateUpper: 0.673,
  benignSupportingUpper: 0.92,
  pathogenicSupportingLower: 0.999,
  pathogenicModerateLower: 1.0,
}

export const BayesDel = Template.bind({})
BayesDel.args = {
  rangeLower: -1,
  rangeUpper: 1,
  value: 0.5,
  benignModerateUpper: -0.36,
  benignSupportingUpper: -0.18,
  pathogenicSupportingLower: 0.13,
  pathogenicModerateLower: 0.27,
  pathogenicStrongLower: 0.5,
}

export const Gerp = Template.bind({})
Gerp.args = {
  rangeLower: -10,
  rangeUpper: 10,
  value: -3.25,
  benignModerateUpper: -4.54,
  benignSupportingUpper: 2.7,
}

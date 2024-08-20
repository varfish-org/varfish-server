import { reactive } from 'vue'

import TokenizingTextarea from '@/variants/components/TokenizingTextarea.vue'

export default {
  title: 'Variants / Tokenizing Text Area',
  component: TokenizingTextarea,
  parameters: {},
}

const Template = (args) => ({
  components: { TokenizingTextarea },
  setup() {
    return { args }
  },
  template:
    '<div class="row">\n' +
    '<div class="col-12">\n' +
    '<TokenizingTextarea\n' +
    '    v-model="args.data.arr"\n' +
    '    :tokenize="args.tokenize"\n' +
    '    :validate="args.validate"\n' +
    '    :textarea-id="args.textareaId"\n' +
    '/>' +
    '</div>' +
    '</div>',
})

const regexToken = /\S+/g
const regexRegion =
  /^(?<chrom>(chr)?(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|Y|M|MT)(:(?<start>\d+(,\d+)*)-(?<stop>\d+(,\d+)*))?)$/
const validateRegion = (token) => {
  const matches = token.match(regexRegion)
  if (
    matches &&
    matches.groups &&
    matches.groups.start &&
    matches.groups.stop
  ) {
    const start = parseInt(matches.groups.start)
    const stop = parseInt(matches.groups.stop)
    return new Promise((resolved) => {
      resolved({ valid: stop >= start, label: 'example label' })
    })
  } else {
    return new Promise((resolved) => {
      resolved(!!matches)
    })
  }
}

export const RegionsValid = Template.bind({})
RegionsValid.args = {
  data: reactive({
    arr: ['chr1', 'chr1:1,000,000-2,000,000'],
  }),
  tokenize: regexToken,
  validate: validateRegion,
}

export const RegionsInvalid = Template.bind({})
RegionsInvalid.args = {
  data: reactive({
    arr: ['chr1', 'chr1:1,000,000-2,000,000', 'chrX:invalid'],
  }),
  tokenize: regexToken,
  validate: validateRegion,
}

const validateGene = (token) => {
  const validTokens = ['TTN', 'TGDS', 'HGNC:1', 'HGNC:2', 'HGNC:3']
  return validTokens.includes(token)
}

export const GenesValid = Template.bind({})
GenesValid.args = {
  data: reactive({
    arr: ['TTN', 'HGNC:1', 'TGDS'],
  }),
  validate: validateGene,
  textareaId: 'genes',
}

export const GenesInvalid = Template.bind({})
GenesInvalid.args = {
  data: reactive({
    arr: ['TTN', 'HGNC:1', 'TGDS', 'invalid'],
  }),
  validate: validateGene,
  textareaId: 'genes',
}

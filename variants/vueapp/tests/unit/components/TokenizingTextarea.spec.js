import TokenizingTextarea from '@variants/components/TokenizingTextarea.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, test } from 'vitest'
import { reactive } from 'vue'

// import singletonCaseData from '../../data/case-singleton.json'
// import querySettingsSingleton from '../../data/query-settings-singleton.json'

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

const validateGene = (token) => {
  const validTokens = ['TTN', 'TGDS', 'HGNC:1', 'HGNC:2', 'HGNC:3']
  return validTokens.includes(token)
}

describe('TokenizingTextarea.vue', () => {
  test('regions valid', () => {
    shallowMount(TokenizingTextarea, {
      props: {
        data: reactive({
          arr: ['chr1', 'chr1:1,000,000-2,000,000'],
        }),
        tokenize: regexToken,
        validate: validateRegion,
      },
    })
    // TODO [TEST_STUB]
  })

  test('regions invalid', () => {
    shallowMount(TokenizingTextarea, {
      props: {
        data: reactive({
          arr: ['chr1', 'chr1:1,000,000-2,000,000', 'chrX:invalid'],
        }),
        tokenize: regexToken,
        validate: validateRegion,
      },
    })
    // TODO [TEST_STUB]
  })

  test('genes valid', () => {
    shallowMount(TokenizingTextarea, {
      props: {
        data: reactive({
          arr: ['TTN', 'HGNC:1', 'TGDS'],
        }),
        validate: validateGene,
        textareaId: 'genes',
      },
    })
    // TODO [TEST_STUB]
  })

  test('genes invalid', () => {
    shallowMount(TokenizingTextarea, {
      props: {
        data: reactive({
          arr: ['TTN', 'HGNC:1', 'TGDS', 'invalid'],
        }),
        validate: validateGene,
        textareaId: 'genes',
      },
    })
    // TODO [TEST_STUB]
  })
})

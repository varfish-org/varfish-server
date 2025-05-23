// import { createTestingPinia } from '@pinia/testing'
// import VariantDetailsCommentsFlags from '@/variants/components/VariantDetails/CommentsFlags.vue'
// import {
//   emptyAcmgCriteriaRatingTemplate,
//   initialFlagsTemplate,
//   VariantValidatorStates,
// } from '@/variants/enums'
// import { shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import {
  beforeEach,
  describe,
  test,
  /*, vi*/
} from 'vitest'

// const testStores = createTestingPinia({
//   initialState: {
//     variantDetails: {
//       fetched: false,
//       geneId: null,
//       smallVariant: null,
//       flags: [],
//       clinvar: null,
//       knowngeneaa: null,
//       effectDetails: null,
//       extraAnnos: null,
//       populations: null,
//       popFreqs: null,
//       inhouseFreq: null,
//       mitochondrialFreqs: null,
//       gene: null,
//       ncbiSummary: null,
//       ncbiGeneRifs: null,
//       variantValidatorResults: null,
//       beaconAddress: null,
//       setFlagsMode: false,
//       flagsToSubmit: { ...initialFlagsTemplate },
//       acmgCriteriaRatingToSubmit: { ...emptyAcmgCriteriaRatingTemplate },
//       setAcmgCriteriaRatingMode: false,
//       acmgCriteriaRatingConflicting: false,
//       variantValidatorState: VariantValidatorStates.Initial,
//       gridApi: null,
//       queryDetails: null,
//     },
//     variantComments: {
//       comments: null,
//     },
//     filterQuery: {
//       showFiltrationInlineHelp: false,
//       filtrationComplexityMode: null,
//       caseUuid: null,
//       case: null,
//       querySettingsPresets: null,
//       querySettings: null,
//       umdPredictorApiToken: null,
//       hgmdProEnabled: null,
//       hgmdProPrefix: null,
//       ga4ghBeaconNetworkWidgetEnabled: null,
//       exomiserEnabled: null,
//       caddEnabled: null,
//       previousQueryDetails: null,
//       queryUuid: null,
//       queryResults: null,
//       queryInterval: null,
//       queryState: 0,
//       queryLogs: null,
//       queryLogsVisible: false,
//       queryHpoTerms: null,
//       displayDetails: 0,
//       displayFrequency: 0,
//       displayConstraint: 0,
//       displayColumns: [0],
//       quickPresets: null,
//       categoryPresets: {
//         inheritance: null,
//         frequency: null,
//         impact: null,
//         quality: null,
//         chromosomes: null,
//         flags_etc: null,
//       },
//       extraAnnoFields: [],
//     },
//   },
//   createSpy: vi.fn,
// })

describe('VariantDetailsCommentsFlags.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  test('', () => {
    // shallowMount(VariantDetailsCommentsFlags, {
    //   props: {},
    //   global: {
    //     plugins: [testStores],
    //   },
    // })
    // TODO [TEST_STUB]
  })
})

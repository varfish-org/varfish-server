import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import SubmissionList from '@clinvarexport/components/SubmissionList.vue'
import {
  useClinvarExportStore,
  WizardState,
} from '@clinvarexport/stores/clinvar-export.js'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import {
  afterAll,
  afterEach,
  beforeAll,
  describe,
  expect,
  test,
  vi,
} from 'vitest'
import { nextTick } from 'vue'

import { copy } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstAssertionMethod,
  firstFamily,
  firstIndividual,
  firstOrganisation,
  firstSubmission,
  firstSubmissionIndividual,
  firstSubmissionSet,
  firstSubmittingOrg,
  firstUserAnnotation,
  secondIndividual,
  secondOrganisation,
  secondSubmission,
  secondSubmissionIndividual,
  secondSubmittingOrg,
} from '../fixtures.js'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  return mount(SubmissionList, {
    global: {
      plugins: [
        createTestingPinia({
          initialState: { clinvarExport: clinvarExportState },
          createSpy: vi.fn,
        }),
      ],
    },
  })
}

// Mock out the clinvarExport API
vi.mock('@clinvarexport/api/clinvarExport')

describe('SubmissionList.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Mock out jquery dollar function for showing modals
    global.$ = vi.fn()
  })

  afterAll(() => {
    global.$.mockRestore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // Simple case: one submission, complex case: two submission, in one
  // submission list in any case.
  let submissionSet1
  let submission1
  let submissionIndividual1
  let submittingOrg1
  let organisation1
  let individual1
  const setupSimpleCase = () => {
    const result = copy(clinvarExportEmptyState)
    result.wizardState = WizardState.submission
    submissionSet1 = copy(firstSubmissionSet)
    result.submissionSetList = [submissionSet1]
    result.currentSubmissionSet = submissionSet1
    result.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    submission1 = copy(firstSubmission)
    result.submissions[submission1.sodar_uuid] = submission1
    individual1 = copy(firstIndividual)
    result.individuals[individual1.sodar_uuid] = individual1
    submissionIndividual1 = copy(firstSubmissionIndividual)
    result.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    submittingOrg1 = copy(firstSubmittingOrg)
    result.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    organisation1 = copy(firstOrganisation)
    result.organisations[organisation1.sodar_uuid] = organisation1
    family1 = copy(firstFamily)
    result.families[family1.sodar_uuid] = family1
    assertionMethod1 = copy(firstAssertionMethod)
    result.assertionMethods[assertionMethod1.sodar_uuid] = assertionMethod1
    return result
  }

  let submission2
  let individual2
  let submissionIndividual2
  let submittingOrg2
  let organisation2
  let assertionMethod1
  let family1
  const setupComplexCase = () => {
    const result = setupSimpleCase()
    submission2 = copy(secondSubmission)
    result.submissions[submission2.sodar_uuid] = submission2
    submissionSet1.submissions.push(submission2.sodar_uuid)
    individual2 = copy(secondIndividual)
    result.individuals[individual2.sodar_uuid] = individual2
    submissionIndividual2 = copy(secondSubmissionIndividual)
    result.submissionIndividuals[submissionIndividual2.sodar_uuid] =
      submissionIndividual2
    submittingOrg2 = copy(secondSubmittingOrg)
    result.submittingOrgs[submittingOrg2.sodar_uuid] = submittingOrg2
    organisation2 = copy(secondOrganisation)
    result.organisations[organisation2.sodar_uuid] = organisation2
    return result
  }

  // Helper that shows the "add submission" modal; function to be re-used
  // at the beginning of different tests.
  const testAddSubmissionButtonClicked = async (
    setupFunc,
    setupFuncParam = {},
    extraState = {}
  ) => {
    const state = {
      ...setupFunc(setupFuncParam),
      currentSubmission: submission1,
      ...extraState,
    }
    const wrapper = makeWrapper(state)

    global.$.mockReturnValue({
      modal: vi.fn((action) => {
        const classes = wrapper.vm.$refs.modalAddSubmission.classList
        if (action === 'show') {
          if (!classes.contains('show')) {
            classes.remove('fade')
            classes.add('show')
          }
        } else if (action === 'hide') {
          if (!classes.contains('fade')) {
            classes.add('fade')
            classes.remove('show')
          }
        }
      }),
    })

    expect(wrapper.vm.$refs.modalAddSubmission).toBeDefined()
    expect(
      Object.values(wrapper.vm.$refs.modalAddSubmission.classList)
    ).not.toContain('show')
    await wrapper.vm.$refs.buttonAddSubmission.click()
    await nextTick()
    expect(
      Object.values(wrapper.vm.$refs.modalAddSubmission.classList)
    ).toContain('show')

    await flushPromises()

    return wrapper
  }

  test('simple functions', async () => {
    const wrapper = await testAddSubmissionButtonClicked(setupComplexCase)

    expect(wrapper.vm.isValid()).toBe(true)
    expect(wrapper.vm.getEmptySubmissionData()).toEqual({
      record_status: 'novel',
      release_status: 'public',
      significance_status: 'criteria provided, single submitter',
      significance_description: null,
      significance_last_evaluation: new Date().toISOString().substr(0, 10),
      assertion_method: assertionMethod1.sodar_uuid,
      age_of_onset: '',
      inheritance: '',
      variant_type: 'Variation',
      variant_assembly: 'GRCh37',
      variant_chromosome: null,
      variant_start: null,
      variant_stop: null,
      variant_reference: null,
      variant_alternative: null,
      variant_gene: [],
      variant_hgvs: [],

      diseases: [],
      submission_individuals: [],
    })
  })

  test('add submission button clicked shows modal', async () => {
    await testAddSubmissionButtonClicked(setupComplexCase)
  })

  test('show modal and add empty submission', async () => {
    const wrapper = await testAddSubmissionButtonClicked(setupComplexCase)
    const store = useClinvarExportStore()
    store.createSubmissionInCurrentSubmissionSet = vi.fn()

    expect(wrapper.vm.isValid()).toBe(true)
    expect(wrapper.vm.$refs.modalAddSubmission.classList.length).toBe(2)
    expect(wrapper.vm.$refs.modalAddSubmission.classList[0]).toEqual('modal')
    expect(wrapper.vm.$refs.modalAddSubmission.classList[1]).toEqual('show')
    expect(Object.keys(store.submissions).length).toBe(2)
    await wrapper.vm.$refs.buttonAddSelectedSubmissions.click()

    await flushPromises()

    expect(store.createSubmissionInCurrentSubmissionSet).toHaveBeenCalledTimes(
      1
    )
    expect(
      store.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenNthCalledWith(1, {
      smallVariant: null,
      submission: {
        record_status: 'novel',
        release_status: 'public',
        significance_status: 'criteria provided, single submitter',
        significance_description: null,
        significance_last_evaluation: new Date().toISOString().substr(0, 10),
        assertion_method: assertionMethod1.sodar_uuid,
        age_of_onset: '',
        inheritance: '',
        variant_type: 'Variation',
        variant_assembly: 'GRCh37',
        variant_chromosome: null,
        variant_start: null,
        variant_stop: null,
        variant_reference: null,
        variant_alternative: null,
        variant_gene: [],
        variant_hgvs: [],

        diseases: [],
        submission_individuals: [],
      },
      individualUuids: [],
    })
  })

  test('show modal and select case', async () => {
    const wrapper = await testAddSubmissionButtonClicked(setupSimpleCase)
    const store = useClinvarExportStore()
    store.selectCurrentSubmission = vi.fn()

    const userAnnotation = {
      small_variants: [
        {
          ...firstUserAnnotation.small_variants[0],
          variant_start:
            firstUserAnnotation.small_variants[0].variant_start + 1,
          variant_stop: firstUserAnnotation.small_variants[0].variant_stop + 1,
        },
      ],
      small_variant_flags: [
        {
          ...firstUserAnnotation.small_variant_flags[0],
          variant_start:
            firstUserAnnotation.small_variants[0].variant_start + 1,
          variant_stop: firstUserAnnotation.small_variants[0].variant_stop + 1,
          flag_summary: 'positive',
        },
      ],
      small_variant_comments: [],
      acmg_criteria_rating: [
        {
          ...firstUserAnnotation.acmg_criteria_rating[0],
          variant_start:
            firstUserAnnotation.small_variants[0].variant_start + 1,
          variant_stop: firstUserAnnotation.small_variants[0].variant_stop + 1,
        },
      ],
    }

    clinvarExportApi.getUserAnnotations.mockReturnValueOnce(
      Promise.resolve(userAnnotation)
    )

    // Note: we select the family UUID by accessing the store directly
    // as I (Manuel) have not figured out yet how to programatically
    // select the item in the vue-multiselect.
    wrapper.vm.$data.familyUuid = family1.sodar_uuid
    await wrapper.vm.fetchRawModalUserAnnotations()

    await flushPromises()

    expect(clinvarExportApi.getUserAnnotations).toBeCalledTimes(1)
    expect(clinvarExportApi.getUserAnnotations).toHaveBeenNthCalledWith(
      1,
      store.appContext,
      family1.sodar_uuid
    )
    expect(wrapper.vm.$data.rawModalUserAnnotationsCount).toBe(1)
    expect(Object.keys(wrapper.vm.$data.rawModalUserAnnotations)).toEqual([
      'smallVariants',
      'smallVariantFlags',
      'smallVariantComments',
      'acmgCriteriaRating',
    ])
    expect(
      Object.keys(wrapper.vm.$data.rawModalUserAnnotations.acmgCriteriaRating)
    ).toEqual(['GRCh37-17-41201211-T-G'])
    expect(
      Object.keys(wrapper.vm.$data.rawModalUserAnnotations.smallVariantComments)
    ).toEqual([])
    expect(
      Object.keys(wrapper.vm.$data.rawModalUserAnnotations.smallVariantFlags)
    ).toEqual(['GRCh37-17-41201211-T-G'])
    expect(
      Object.keys(wrapper.vm.$data.rawModalUserAnnotations.smallVariants)
    ).toEqual(['GRCh37-17-41201211-T-G'])

    // Note that for some reason, the DOM is not properly updated in tests.
    expect(wrapper.vm.$refs.userAnnotationList.childElementCount).toBe(2)
    expect(wrapper.vm.$data.modalUserAnnotations.length).toBe(1)
    expect(wrapper.vm.$data.selectedSmallVariants).toEqual([])
    await wrapper.vm.$refs.userAnnotationList.children[1].click()
    expect(wrapper.vm.$data.selectedSmallVariants).toEqual([
      'GRCh37-17-41201211-T-G',
    ])
    await nextTick()
    await wrapper.vm.$refs.buttonAddSelectedSubmissions.click()

    await flushPromises()

    expect(store.createSubmissionInCurrentSubmissionSet).toHaveBeenCalledTimes(
      1
    )
    expect(
      store.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenNthCalledWith(1, {
      smallVariant: expect.objectContaining({
        genotype: {
          index: {
            gt: '0/1',
          },
        },
      }),
      submission: expect.objectContaining({
        significance_description: 'Pathogenic',
      }),
      individualUuids: ['88888888-8888-8888-8888-888888888888'],
    })
  })

  test('select first (inactive) submission', async () => {
    const wrapper = await testAddSubmissionButtonClicked(
      setupComplexCase,
      {},
      { currentSubmission: copy(secondSubmission) }
    )
    const store = useClinvarExportStore()
    store.selectCurrentSubmission = vi.fn()
    expect(store.currentSubmission).toEqual(submission2)
    wrapper.vm.$refs.submissionList.$el.childNodes[1].click()

    expect(store.selectCurrentSubmission).toHaveBeenCalledTimes(1)
    expect(store.selectCurrentSubmission).toHaveBeenNthCalledWith(
      1,
      submission1.sodar_uuid
    )
  })

  test('select second (active) submission', async () => {
    const wrapper = await testAddSubmissionButtonClicked(
      setupComplexCase,
      {},
      { currentSubmission: copy(secondSubmission) }
    )
    const store = useClinvarExportStore()
    store.selectCurrentSubmission = vi.fn()
    expect(store.currentSubmission).toEqual(submission2)
    wrapper.vm.$refs.submissionList.$el.childNodes[2].click()

    expect(store.selectCurrentSubmission).toHaveBeenCalledTimes(1)
    expect(store.selectCurrentSubmission).toHaveBeenNthCalledWith(
      1,
      submission2.sodar_uuid
    )
  })
})

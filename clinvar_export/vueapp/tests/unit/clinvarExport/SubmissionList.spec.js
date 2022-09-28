import { createLocalVue, mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionList from '@/components/SubmissionList.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

import { copy, waitNT, waitRAF } from '../../testUtils.js'
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
  rawAppContext,
  secondIndividual,
  secondOrganisation,
  secondSubmission,
  secondSubmissionIndividual,
  secondSubmittingOrg,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionList.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
    // Mock out jquery dollar function for showing modals
    global.$ = jest.fn()
  })

  afterAll(() => {
    global.$.mockRestore()
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      selectCurrentSubmission: jest.fn(),
      updateCurrentSubmission: jest.fn(),
      updateSubmissionIndividual: jest.fn(),
      createSubmissionInCurrentSubmissionSet: jest.fn(),
    }
    const clinvarExport = {
      namespaced: true,
      actions,
      state: () => copy(clinvarExportEmptyState),
    }
    store = new Vuex.Store({
      modules: {
        clinvarExport,
      },
    })
    store.state.clinvarExport.appContext = copy(rawAppContext)
  })

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
    global.$.mockClear()
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
    Vue.set(store.state.clinvarExport, 'wizardState', WizardState.submission)
    submissionSet1 = copy(firstSubmissionSet)
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    submission1 = copy(firstSubmission)
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    individual1 = copy(firstIndividual)
    Vue.set(
      store.state.clinvarExport.individuals,
      individual1.sodar_uuid,
      individual1
    )
    submissionIndividual1 = copy(firstSubmissionIndividual)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    submittingOrg1 = copy(firstSubmittingOrg)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    organisation1 = copy(firstOrganisation)
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    family1 = copy(firstFamily)
    Vue.set(store.state.clinvarExport.families, family1.sodar_uuid, family1)
    assertionMethod1 = copy(firstAssertionMethod)
    Vue.set(
      store.state.clinvarExport.assertionMethods,
      assertionMethod1.sodar_uuid,
      assertionMethod1
    )
  }

  let submission2
  let individual2
  let submissionIndividual2
  let submittingOrg2
  let organisation2
  let assertionMethod1
  let family1
  const setupComplexCase = () => {
    setupSimpleCase()
    submission2 = copy(secondSubmission)
    Vue.set(
      store.state.clinvarExport.submissions,
      submission2.sodar_uuid,
      submission2
    )
    submissionSet1.submissions.push(submission2.sodar_uuid)
    individual2 = copy(secondIndividual)
    Vue.set(
      store.state.clinvarExport.individuals,
      individual2.sodar_uuid,
      individual2
    )
    submissionIndividual2 = copy(secondSubmissionIndividual)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual2.sodar_uuid,
      submissionIndividual2
    )
    submittingOrg2 = copy(secondSubmittingOrg)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg2.sodar_uuid,
      submittingOrg2
    )
    organisation2 = copy(secondOrganisation)
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation2.sodar_uuid,
      organisation2
    )
  }

  // Helper that shows the "add submission" modal; function to be re-used
  // at the beginning of different tests.
  const testAddSubmissionButtonClicked = async (setupFunc) => {
    setupFunc()

    const wrapper = mount(SubmissionList, {
      store,
      localVue,
    })

    global.$.mockReturnValue({
      modal: jest.fn((action) => {
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

    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)

    expect(wrapper.vm.$refs.modalAddSubmission).toBeDefined()
    expect(wrapper.vm.$refs.modalAddSubmission.classList).not.toContain('show')
    await wrapper.vm.$refs.buttonAddSubmission.click()
    await waitNT(wrapper.vm)
    await waitRAF()
    expect(wrapper.vm.$refs.modalAddSubmission.classList).toContain('show')

    await flushPromises()

    return wrapper
  }

  test('simple functions', async () => {
    const wrapper = await testAddSubmissionButtonClicked(setupComplexCase)
    const submissionList = wrapper.vm.$root.$children[0]

    expect(submissionList.isValid()).toBe(true)
    expect(submissionList.getEmptySubmissionData()).toEqual({
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
    const submissionList = wrapper.vm.$root.$children[0]

    expect(submissionList.isValid()).toBe(true)
    expect(wrapper.vm.$refs.modalAddSubmission.classList).toContain('show')
    expect(Object.keys(store.state.clinvarExport.submissions).length).toBe(2)
    await wrapper.vm.$refs.buttonAddSelectedSubmissions.click()

    await flushPromises()

    expect(
      actions.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenCalledTimes(1)
    expect(
      actions.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenNthCalledWith(1, expect.anything(), {
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
    const submissionList = wrapper.vm.$root.$children[0]

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
    Vue.set(submissionList.$data, 'familyUuid', family1.sodar_uuid)
    await submissionList.fetchRawModalUserAnnotations()

    await flushPromises()

    expect(clinvarExportApi.getUserAnnotations).toBeCalledTimes(1)
    expect(clinvarExportApi.getUserAnnotations).toHaveBeenNthCalledWith(
      1,
      store.state.clinvarExport.appContext,
      family1.sodar_uuid
    )
    expect(submissionList.$data.rawModalUserAnnotationsCount).toBe(1)
    expect(Object.keys(submissionList.$data.rawModalUserAnnotations)).toEqual([
      'smallVariants',
      'smallVariantFlags',
      'smallVariantComments',
      'acmgCriteriaRating',
    ])
    expect(
      Object.keys(
        submissionList.$data.rawModalUserAnnotations.acmgCriteriaRating
      )
    ).toEqual(['GRCh37-17-41201211-T-G'])
    expect(
      Object.keys(
        submissionList.$data.rawModalUserAnnotations.smallVariantComments
      )
    ).toEqual([])
    expect(
      Object.keys(
        submissionList.$data.rawModalUserAnnotations.smallVariantFlags
      )
    ).toEqual(['GRCh37-17-41201211-T-G'])
    expect(
      Object.keys(submissionList.$data.rawModalUserAnnotations.smallVariants)
    ).toEqual(['GRCh37-17-41201211-T-G'])

    // Note that for some reason, the DOM is not properly updated in tests.
    expect(wrapper.vm.$refs.userAnnotationList.childElementCount).toBe(2)
    expect(submissionList.$data.modalUserAnnotations.length).toBe(1)
    expect(submissionList.$data.selectedSmallVariants).toEqual([])
    await wrapper.vm.$refs.userAnnotationList.children[1].click()
    expect(submissionList.$data.selectedSmallVariants).toEqual([
      'GRCh37-17-41201211-T-G',
    ])
    await waitNT(wrapper.vm)
    await waitRAF()
    await wrapper.vm.$refs.buttonAddSelectedSubmissions.click()

    await flushPromises()

    expect(
      actions.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenCalledTimes(1)
    expect(
      actions.createSubmissionInCurrentSubmissionSet
    ).toHaveBeenNthCalledWith(1, expect.anything(), {
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
    const wrapper = await testAddSubmissionButtonClicked(setupComplexCase)
    const submissionList = wrapper.vm.$root.$children[0]
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission2)
    expect(store.state.clinvarExport.currentSubmission).toEqual(submission2)
    submissionList.$refs.submissionList.$el.childNodes[0].click()

    expect(actions.selectCurrentSubmission).toHaveBeenCalledTimes(1)
    expect(actions.selectCurrentSubmission).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      submission1.sodar_uuid
    )
  })

  test('select second (active) submission', async () => {
    const wrapper = await testAddSubmissionButtonClicked(setupComplexCase)
    const submissionList = wrapper.vm.$root.$children[0]
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission2)
    expect(store.state.clinvarExport.currentSubmission).toEqual(submission2)
    submissionList.$refs.submissionList.$el.childNodes[1].click()

    expect(actions.selectCurrentSubmission).toHaveBeenCalledTimes(1)
    expect(actions.selectCurrentSubmission).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      submission2.sodar_uuid
    )
  })
})

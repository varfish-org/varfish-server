import { createLocalVue, shallowMount } from '@vue/test-utils'
import BootstrapVue from 'bootstrap-vue'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionCaseList from '@/components/SubmissionCaseList.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

import { copy } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstIndividual,
  firstOrganisation,
  firstSubmission,
  firstSubmissionIndividual,
  firstSubmissionSet,
  firstSubmitter,
  firstSubmittingOrg,
  rawAppContext,
  secondIndividual,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(BootstrapVue)
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionCaseList.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      updateCurrentSubmission: jest.fn(),
      moveCurrentSubmission: jest.fn(),
      deleteCurrentSubmission: jest.fn(),
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

  // In these tests we consider the simple case of having one submission
  // set only and to initially be in the submission set state
  let organisation1
  let submitter1
  let submittingOrg1
  let submissionSet1
  let submission1
  let submissionIndividual1
  let individual1
  let individual2
  const setupSimpleCase = () => {
    organisation1 = copy(firstOrganisation)
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    submitter1 = copy(firstSubmitter)
    Vue.set(
      store.state.clinvarExport.submitters,
      submitter1.sodar_uuid,
      submitter1
    )
    submittingOrg1 = copy(firstSubmittingOrg)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    submission1 = copy(firstSubmission)
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    submissionSet1 = copy(firstSubmissionSet)
    Vue.set(store.state.clinvarExport, 'wizardState', WizardState.submissionSet)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    submissionIndividual1 = copy(firstSubmissionIndividual)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    individual1 = copy(firstIndividual)
    Vue.set(
      store.state.clinvarExport.individuals,
      individual1.sodar_uuid,
      individual1
    )
    individual2 = copy(secondIndividual)
    Vue.set(
      store.state.clinvarExport.individuals,
      individual2.sodar_uuid,
      individual2
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(store.state.clinvarExport, 'wizardState', WizardState.submissions)
  }

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
  })

  test('check computed properties', async () => {
    setupSimpleCase()

    const wrapper = shallowMount(SubmissionCaseList, {
      store,
      localVue,
    })
    const submissionCaseList = wrapper.vm.$root.$children[0]

    expect(submissionCaseList.caseCount).toEqual(1)
    expect(submissionCaseList.caseSubmissionIndividuals).toEqual([
      { wrapped: submissionIndividual1 },
    ])
  })

  test('check functions', async () => {
    setupSimpleCase()

    const wrapper = shallowMount(SubmissionCaseList, {
      store,
      localVue,
    })
    const submissionCaseList = wrapper.vm.$root.$children[0]

    expect(submissionCaseList.getModalIndividualList()).toEqual([individual2])
    expect(submissionCaseList.getPhenotypeDisplay(individual1)).toEqual(
      '(HP:123456) some name, (HP:98235) another name'
    )
  })
})

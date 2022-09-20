import { createLocalVue, mount } from '@vue/test-utils'
import BootstrapVue from 'bootstrap-vue'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionCaseListEntry from '@/components/SubmissionCaseListEntry.vue'
import {
  actions,
  mutations,
  WizardState,
} from '@/store/modules/clinvarExport.js'

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
  secondSubmissionIndividual,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(BootstrapVue)
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionCaseListEntry.vue', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    const clinvarExport = {
      namespaced: true,
      actions,
      mutations,
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
  let submissionIndividual2
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
    submissionIndividual2 = copy({
      ...secondSubmissionIndividual,
      submission: submission1.sodar_uuid,
      sort_order: 1,
    })
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual2.sodar_uuid,
      submissionIndividual2
    )
    Vue.set(
      store.state.clinvarExport.currentSubmission,
      'submission_individuals',
      [submissionIndividual1.sodar_uuid, submissionIndividual2.sodar_uuid]
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

  const testSetup = async (siNo) => {
    await setupSimpleCase()

    const wrapper = mount(
      {
        data: () => {
          return {
            submissionIndividual:
              siNo === 2 ? submissionIndividual2 : submissionIndividual1,
          }
        },
        template:
          '<div><submission-case-list-entry ref="listEntry" v-model="submissionIndividual">' +
          '</submission-case-list-entry></div>',
        components: { SubmissionCaseListEntry },
      },
      {
        store,
        localVue,
      }
    )
    return wrapper.vm.$refs.listEntry
  }

  test('check computed properties', async () => {
    const submissionCaseListEntry = await testSetup(1)

    expect(submissionCaseListEntry.hpoTermsLoading).toBe(false)

    expect(submissionCaseListEntry.appContext).toEqual(
      store.state.clinvarExport.appContext
    )
    expect(submissionCaseListEntry.currentSubmission).toEqual(
      store.state.clinvarExport.currentSubmission
    )
    expect(submissionCaseListEntry.individuals).toEqual(
      store.state.clinvarExport.individuals
    )
    expect(submissionCaseListEntry.submissionIndividuals).toEqual(
      store.state.clinvarExport.submissionIndividuals
    )

    expect(submissionCaseListEntry.phenotypes).toEqual([
      { term_id: 'HP:1234567', term_name: 'Something' },
    ])
    expect(submissionCaseListEntry.citations).toEqual('PMID:12345')
    expect(submissionCaseListEntry.individual).toEqual(individual1)
  })

  test('check funcions', async () => {
    const submissionCaseListEntry = await testSetup(1)

    expect(
      submissionCaseListEntry.getHpoTermLabel({
        term_id: 'HP:xxx',
        term_name: 'short',
      })
    ).toEqual('HP:xxx - short')
    expect(
      submissionCaseListEntry.getHpoTermLabel({
        term_id: 'HP:xxx',
        term_name: 'longlonglonglonglong',
      })
    ).toEqual('HP:xxx - longlonglo...')
  })

  test('check isMoveDisabled()', async () => {
    const submissionCaseListEntry = await testSetup(1)

    expect(submissionCaseListEntry.isMoveDisabled(true)).toBe(true)
    expect(submissionCaseListEntry.isMoveDisabled(false)).toBe(false)
  })

  test('check isMoveDisabled()', async () => {
    const submissionCaseListEntry = await testSetup(2)

    expect(submissionCaseListEntry.isMoveDisabled(true)).toBe(false)
    expect(submissionCaseListEntry.isMoveDisabled(false)).toBe(true)
  })
})

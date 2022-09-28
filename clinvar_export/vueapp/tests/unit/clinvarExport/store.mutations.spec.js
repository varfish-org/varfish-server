import { createLocalVue } from '@vue/test-utils'
import Vue from 'vue'
import Vuex from 'vuex'

import { AppState, mutations, WizardState } from '@/store/modules/clinvarExport'

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
  firstSubmitter,
  firstSubmittingOrg,
  firstUserAnnotation,
  rawAppContext,
  secondFamily,
  secondIndividual,
  secondOrganisation,
  secondSubmission,
  secondSubmissionIndividual,
  secondSubmittingOrg,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

const MOCK_UUID_VALUE = 'xxxxxxxx-xxxx-4xxx-mock-mockmockmock'

// Mock out UUIDv4 generation
jest.mock('@/helpers', () => {
  const origHelpersModule = jest.requireActual('@/helpers')
  return {
    __esModule: true,
    ...origHelpersModule,
    uuidv4: jest.fn(() => {
      return MOCK_UUID_VALUE
    }),
  }
})

describe('mutations', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    const clinvarExport = {
      namespaced: true,
      state: () => copy(clinvarExportEmptyState),
    }
    store = new Vuex.Store({
      modules: {
        clinvarExport,
      },
    })
  })

  test('SET_APP_CONTEXT', () => {
    expect(store.state.clinvarExport.appContext).toBe(null)
    expect(store.state.clinvarExport.appContext).toBe(null)
    mutations.SET_APP_CONTEXT(store.state.clinvarExport, rawAppContext)
    expect(store.state.clinvarExport.appContext).toBe(rawAppContext)
  })

  test('SET_APP_STATE', () => {
    expect(store.state.clinvarExport.appState).toBe(AppState.initializing)
    mutations.SET_APP_STATE(store.state.clinvarExport, AppState.add)
    expect(store.state.clinvarExport.appState).toBe(AppState.add)
  })

  test('SET_APP_SERVER_INTERACTION', () => {
    expect(store.state.clinvarExport.serverInteraction).toBe(false)
    mutations.SET_APP_SERVER_INTERACTION(store.state.clinvarExport, true)
    expect(store.state.clinvarExport.serverInteraction).toBe(true)
  })

  test('SET_CURRENT_SUBMISSION_SET with NOT null', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    store.state.clinvarExport.submissionSetList.push(submissionSet1)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )

    expect(store.state.clinvarExport.currentSubmissionSet).toBe(null)
    mutations.SET_CURRENT_SUBMISSION_SET(
      store.state.clinvarExport,
      submissionSet1.sodar_uuid
    )
    expect(store.state.clinvarExport.currentSubmissionSet).toBe(submissionSet1)
  })

  test('SET_CURRENT_SUBMISSION_SET with null', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    store.state.clinvarExport.submissionSetList.push(submissionSet1)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)

    expect(store.state.clinvarExport.currentSubmissionSet).toBe(submissionSet1)
    mutations.SET_CURRENT_SUBMISSION_SET(store.state.clinvarExport, null)
    expect(store.state.clinvarExport.currentSubmissionSet).toBe(null)
  })

  test('INITIALIZE_SUBMISSION_SET_ORGANISATIONS', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)

    store.state.clinvarExport.submissionSetList.push(submissionSet1)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )

    expect(
      store.state.clinvarExport.submissionSets[submissionSet1.sodar_uuid]
        .organisations
    ).toBe(undefined)
    mutations.INITIALIZE_SUBMISSION_SET_ORGANISATIONS(store.state.clinvarExport)
    expect(
      store.state.clinvarExport.submissionSets[submissionSet1.sodar_uuid]
        .organisations
    ).toStrictEqual([submittingOrg1.organisation])
  })

  test('SAVE_OLD_MODEL', () => {
    // This really only is a smoke test at the moment
    expect(store.state.clinvarExport.oldModel).toBe(null)
    mutations.SAVE_OLD_MODEL(store.state.clinvarExport)
    expect(store.state.clinvarExport.oldModel).toStrictEqual({
      assertionMethods: {},
      families: {},
      individuals: {},
      organisations: {},
      submissionIndividuals: {},
      submissionSets: {},
      submissions: {},
      submitters: {},
      submittingOrgs: {},
    })
  })

  test('RESTORE_OLD_MODEL', () => {
    // This really only is a smoke test at the moment
    mutations.SAVE_OLD_MODEL(store.state.clinvarExport)
    mutations.RESTORE_OLD_MODEL(store.state.clinvarExport)
  })

  test('ADD_SUBMISSION_SET', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([])
    mutations.ADD_SUBMISSION_SET(store.state.clinvarExport, submissionSet1)
    expect(Object.keys(store.state.clinvarExport.submissionSets)).toStrictEqual(
      [submissionSet1.sodar_uuid]
    )
    expect(
      Object.values(store.state.clinvarExport.submissionSets)
    ).toStrictEqual([submissionSet1])
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([
      submissionSet1,
    ])
  })

  test('SET_ORGANISATIONS', () => {
    const organisation1 = copy(firstOrganisation)

    expect(store.state.clinvarExport.organisations).toStrictEqual({})
    mutations.SET_ORGANISATIONS(store.state.clinvarExport, [organisation1])
    expect(store.state.clinvarExport.organisations).toStrictEqual(
      Object.fromEntries([[organisation1.sodar_uuid, organisation1]])
    )
  })

  test('SET_SUBMITTERS', () => {
    const submitter1 = copy(firstSubmitter)

    expect(store.state.clinvarExport.submitters).toStrictEqual({})
    mutations.SET_SUBMITTERS(store.state.clinvarExport, [submitter1])
    expect(store.state.clinvarExport.submitters).toStrictEqual(
      Object.fromEntries([[submitter1.sodar_uuid, submitter1]])
    )
  })

  test('SET_ASSERTION_METHODS', () => {
    const assertionMethod1 = copy(firstAssertionMethod)

    expect(store.state.clinvarExport.assertionMethods).toStrictEqual({})
    mutations.SET_ASSERTION_METHODS(store.state.clinvarExport, [
      assertionMethod1,
    ])
    expect(store.state.clinvarExport.assertionMethods).toStrictEqual(
      Object.fromEntries([[assertionMethod1.sodar_uuid, assertionMethod1]])
    )
  })

  test('SET_SUBMISSION_SETS', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([])
    mutations.SET_SUBMISSION_SETS(store.state.clinvarExport, [submissionSet1])
    expect(store.state.clinvarExport.submissionSets).toStrictEqual(
      Object.fromEntries([[submissionSet1.sodar_uuid, submissionSet1]])
    )
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([
      submissionSet1,
    ])
  })

  test('SET_SUBMISSION_SET_LIST', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([])
    mutations.SET_SUBMISSION_SET_LIST(store.state.clinvarExport, [
      submissionSet1,
    ])
    expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
    expect(store.state.clinvarExport.submissionSetList).toStrictEqual([
      submissionSet1,
    ])
  })

  test('ADD_SUBMITTING_ORG', () => {
    const submittingOrg1 = copy(firstSubmittingOrg)

    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual({})
    mutations.ADD_SUBMITTING_ORG(store.state.clinvarExport, submittingOrg1)
    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual(
      Object.fromEntries([[submittingOrg1.sodar_uuid, submittingOrg1]])
    )
  })

  test('ADD_SUBMITTING_ORG_TO_SUBMISSION_SET', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const submittingOrg2 = copy(secondSubmittingOrg)

    expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual({})
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg2.sodar_uuid,
      submittingOrg2
    )
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    mutations.ADD_SUBMITTING_ORG_TO_SUBMISSION_SET(store.state.clinvarExport, {
      submissionSet: submissionSet1.sodar_uuid,
      submittingOrg: submittingOrg2.sodar_uuid,
    })
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
      submittingOrg2.sodar_uuid,
    ])
  })

  test('ADD_SUBMISSION', () => {
    const submission1 = copy(firstSubmission)

    expect(store.state.clinvarExport.submissions).toStrictEqual({})
    mutations.ADD_SUBMISSION(store.state.clinvarExport, submission1)
    expect(store.state.clinvarExport.submissions).toStrictEqual(
      Object.fromEntries([[submission1.sodar_uuid, submission1]])
    )
  })

  test('ADD_SUBMISSION_TO_SUBMISSION_SET', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)
    const submissionSet1 = copy(firstSubmissionSet)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    expect(submissionSet1.submissions).toStrictEqual([submission1.sodar_uuid])
    mutations.ADD_SUBMISSION_TO_SUBMISSION_SET(store.state.clinvarExport, {
      submissionSet: submissionSet1.sodar_uuid,
      submission: submission2.sodar_uuid,
    })
    expect(submissionSet1.submissions).toStrictEqual([
      submission1.sodar_uuid,
      submission2.sodar_uuid,
    ])
  })

  test('SET_SUBMISSIONS', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)

    expect(store.state.clinvarExport.submissions).toStrictEqual({})
    mutations.SET_SUBMISSIONS(store.state.clinvarExport, [
      submission1,
      submission2,
    ])
    expect(store.state.clinvarExport.submissions).toStrictEqual(
      Object.fromEntries([
        [submission1.sodar_uuid, submission1],
        [submission2.sodar_uuid, submission2],
      ])
    )
  })

  test('SET_INDIVIDUALS', () => {
    const individual1 = copy(firstIndividual)
    const individual2 = copy(secondIndividual)

    expect(store.state.clinvarExport.individuals).toStrictEqual({})
    mutations.SET_INDIVIDUALS(store.state.clinvarExport, [
      individual1,
      individual2,
    ])
    expect(store.state.clinvarExport.individuals).toStrictEqual(
      Object.fromEntries([
        [individual1.sodar_uuid, individual1],
        [individual2.sodar_uuid, individual2],
      ])
    )
  })

  test('SET_SUBMISSION_INDIVIDUALS', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const submissionIndividual2 = copy(secondSubmissionIndividual)

    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual({})
    mutations.SET_SUBMISSION_INDIVIDUALS(store.state.clinvarExport, [
      submissionIndividual1,
      submissionIndividual2,
    ])
    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual(
      Object.fromEntries([
        [submissionIndividual1.sodar_uuid, submissionIndividual1],
        [submissionIndividual2.sodar_uuid, submissionIndividual2],
      ])
    )
  })

  test('SET_FAMILIES', () => {
    const family1 = copy(firstFamily)
    const family2 = copy(secondFamily)

    expect(store.state.clinvarExport.families).toStrictEqual({})
    mutations.SET_FAMILIES(store.state.clinvarExport, [family1, family2])
    expect(store.state.clinvarExport.families).toStrictEqual(
      Object.fromEntries([
        [family1.sodar_uuid, family1],
        [family2.sodar_uuid, family2],
      ])
    )
  })

  test('SET_SUBMITTING_ORGS', () => {
    const submittingOrg1 = copy(firstSubmissionIndividual)
    const submittingOrg2 = copy(secondSubmissionIndividual)

    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual({})
    mutations.SET_SUBMITTING_ORGS(store.state.clinvarExport, [
      submittingOrg1,
      submittingOrg2,
    ])
    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual(
      Object.fromEntries([
        [submittingOrg1.sodar_uuid, submittingOrg1],
        [submittingOrg2.sodar_uuid, submittingOrg2],
      ])
    )
  })

  test('SET_WIZARD_STATE', () => {
    expect(store.state.clinvarExport.wizardState).toStrictEqual(
      WizardState.submissionSet
    )
    mutations.SET_WIZARD_STATE(
      store.state.clinvarExport,
      WizardState.submission
    )
    expect(store.state.clinvarExport.wizardState).toStrictEqual(
      WizardState.submission
    )
  })

  const casesSetCurrentSubmission = [
    ['null', null, null],
    ['current submission UUID', firstSubmission.sodar_uuid, null],
    ['other submission UUID', secondSubmission.sodar_uuid, secondSubmission],
  ]

  test.each(casesSetCurrentSubmission)(
    'SET_CURRENT_SUBMISSION with %p',
    (_desc, uuidToSet, currentSubmissionToExpect) => {
      const submission1 = copy(firstSubmission)
      const submission2 = copy(secondSubmission)

      Vue.set(
        store.state.clinvarExport.submissions,
        submission1.sodar_uuid,
        submission1
      )
      Vue.set(
        store.state.clinvarExport.submissions,
        submission2.sodar_uuid,
        submission2
      )
      Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
      mutations.SET_CURRENT_SUBMISSION(store.state.clinvarExport, uuidToSet)
      expect(store.state.clinvarExport.currentSubmission).toStrictEqual(
        currentSubmissionToExpect
      )
    }
  )

  test('UPDATE_CURRENT_SUBMISSION_SET', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)

    expect(submissionSet1).toStrictEqual(firstSubmissionSet)
    mutations.UPDATE_CURRENT_SUBMISSION_SET(store.state.clinvarExport, {
      key: 'title',
      value: 'A new title',
    })
    expect(submissionSet1).toStrictEqual({
      ...firstSubmissionSet,
      title: 'A new title',
    })
  })

  test('UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS noop', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(store.state.clinvarExport.organisations, org1.sodar_uuid, org1)
    mutations.INITIALIZE_SUBMISSION_SET_ORGANISATIONS(store.state.clinvarExport)
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    mutations.UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS(
      store.state.clinvarExport,
      [org1.sodar_uuid]
    )
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
  })

  test('UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS add', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)
    const org2 = copy(secondOrganisation)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(store.state.clinvarExport.organisations, org1.sodar_uuid, org1)
    Vue.set(store.state.clinvarExport.organisations, org2.sodar_uuid, org2)
    mutations.INITIALIZE_SUBMISSION_SET_ORGANISATIONS(store.state.clinvarExport)
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    mutations.UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS(
      store.state.clinvarExport,
      [org1.sodar_uuid, org2.sodar_uuid]
    )
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
      MOCK_UUID_VALUE,
    ])
  })

  test('UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS remove', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(store.state.clinvarExport.organisations, org1.sodar_uuid, org1)
    mutations.INITIALIZE_SUBMISSION_SET_ORGANISATIONS(store.state.clinvarExport)
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    mutations.UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS(
      store.state.clinvarExport,
      []
    )
    expect(submissionSet1.submitting_orgs).toStrictEqual([])
  })

  test('UPDATE_CURRENT_SUBMISSION', () => {
    const submission1 = copy(firstSubmission)

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)

    expect(submission1).toStrictEqual(firstSubmission)
    mutations.UPDATE_CURRENT_SUBMISSION(store.state.clinvarExport, {
      key: 'variant_chromosome',
      value: 'X',
    })
    expect(submission1).toStrictEqual({
      ...firstSubmission,
      variant_chromosome: 'X',
    })
  })

  test('UPDATE_SUBMISSION', () => {
    const submission1 = copy(firstSubmission)

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )

    expect(submission1).toStrictEqual(firstSubmission)
    mutations.UPDATE_SUBMISSION(store.state.clinvarExport, {
      submission: submission1,
      key: 'variant_chromosome',
      value: 'X',
    })
    expect(submission1).toStrictEqual({
      ...firstSubmission,
      variant_chromosome: 'X',
    })
  })

  test('APPLY_SUBMISSION_LIST_ORDER', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission2.sodar_uuid,
      submission2
    )

    expect(submission1).toStrictEqual(firstSubmission)
    expect(submission2).toStrictEqual(secondSubmission)
    mutations.APPLY_SUBMISSION_LIST_ORDER(
      store.state.clinvarExport,
      Object.fromEntries([
        [submission1.sodar_uuid, 101],
        [submission2.sodar_uuid, 102],
      ])
    )
    expect(submission1).toStrictEqual({
      ...firstSubmission,
      sort_order: 101,
    })
    expect(submission2).toStrictEqual({
      ...secondSubmission,
      sort_order: 102,
    })
  })

  test.each([[true], [false]])('DELETE_SUBMISSION current? %p', (isCurrent) => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    if (isCurrent) {
      Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    }
    mutations.DELETE_SUBMISSION(
      store.state.clinvarExport,
      submission1.sodar_uuid
    )
    expect(submissionSet1.submissions).toStrictEqual([])
    expect(store.state.clinvarExport.submissions).toStrictEqual({})
    expect(store.state.clinvarExport.currentSubmission).toStrictEqual(null)
  })

  test('DELETE_SUBMITTING_ORG', () => {
    const submittingOrg1 = copy(firstSubmittingOrg)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual(
      Object.fromEntries([[submittingOrg1.sodar_uuid, submittingOrg1]])
    )
    mutations.DELETE_SUBMITTING_ORG(
      store.state.clinvarExport,
      submittingOrg1.sodar_uuid
    )
    expect(store.state.clinvarExport.submittingOrgs).toStrictEqual({})
  })

  test.each([[true], [false]])(
    'DELETE_SUBMISSION_SET isCurrent?=%p',
    (isCurrent) => {
      const submissionSet1 = copy(firstSubmissionSet)

      Vue.set(
        store.state.clinvarExport.submissionSets,
        submissionSet1.sodar_uuid,
        submissionSet1
      )
      store.state.clinvarExport.submissionSetList.push(submissionSet1)
      if (isCurrent) {
        Vue.set(
          store.state.clinvarExport,
          'currentSubmissionSet',
          submissionSet1
        )
      }
      mutations.DELETE_SUBMISSION_SET(
        store.state.clinvarExport,
        submissionSet1.sodar_uuid
      )
      expect(store.state.clinvarExport.submissionSets).toStrictEqual({})
      expect(store.state.clinvarExport.submissionSetList).toStrictEqual([])
      expect(store.state.clinvarExport.currentSubmissionSet).toStrictEqual(null)
    }
  )

  test('CREATE_SUBMISSION_IN_CURRENT_SUBMISSION_SET', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission2 = copy(secondSubmission)
    const individual2 = copy(secondIndividual)
    const userAnnotation1 = copy(firstUserAnnotation)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.individuals,
      individual2.sodar_uuid,
      individual2
    )

    mutations.CREATE_SUBMISSION_IN_CURRENT_SUBMISSION_SET(
      store.state.clinvarExport,
      {
        smallVariant: userAnnotation1.small_variants[0],
        submission: submission2,
        individualUuids: [individual2.sodar_uuid],
      }
    )
    expect(store.state.clinvarExport.submissions).toStrictEqual({
      'xxxxxxxx-xxxx-4xxx-mock-mockmockmock': {
        _isInvalid: false,
        age_of_onset: 'Antenatal',
        assertion_method: '55555555-5555-5555-5555-555555555555',
        date_created: '2020-11-09 13:37',
        date_modified: '2020-11-09 13:37',
        diseases: [
          {
            term_id: '617638',
            term_name: 'IMMUNODEFICIENCY 11B WITH ATOPIC DERMATITIS',
          },
        ],
        inheritance: 'Other',
        record_status: 'novel',
        release_status: 'public',
        significance_description: 'Pathogenic',
        significance_last_evaluation: '2020-11-09',
        significance_status: 'criteria provided, single submitter',
        sodar_uuid: 'xxxxxxxx-xxxx-4xxx-mock-mockmockmock',
        sort_order: 0,
        submission_individuals: ['xxxxxxxx-xxxx-4xxx-mock-mockmockmock'],
        submission_set: '11111111-1111-1111-1111-111111111111',
        variant_alternative: 'G',
        variant_assembly: 'GRCh37',
        variant_chromosome: '17',
        variant_gene: ['BRCA1'],
        variant_hgvs: ['NM_007294.4:p.Asp1778Gly'],
        variant_reference: 'T',
        variant_start: 41201211,
        variant_stop: 41201211,
        variant_type: 'Variation',
      },
    })
    expect(store.state.clinvarExport.currentSubmission).toBe(
      store.state.clinvarExport.submissions[
        Object.keys(store.state.clinvarExport.submissions)[0]
      ]
    )
  })

  test('UPDATE_SUBMISSION_INDIVIDUAL', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )

    mutations.UPDATE_SUBMISSION_INDIVIDUAL(store.state.clinvarExport, {
      submissionIndividual: submissionIndividual1,
      key: 'sort_order',
      value: 101,
    })
    expect(submissionIndividual1).toStrictEqual({
      ...firstSubmissionIndividual,
      sort_order: 101,
    })
  })

  test('DELETE_SUBMISSION_INDIVIDUAL', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const submissionIndividual2 = copy(secondSubmissionIndividual)
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission2.sodar_uuid,
      submission2
    )
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual2.sodar_uuid,
      submissionIndividual2
    )

    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual(
      Object.fromEntries([
        [submissionIndividual1.sodar_uuid, submissionIndividual1],
        [submissionIndividual2.sodar_uuid, submissionIndividual2],
      ])
    )
    expect(submission1.submission_individuals).toStrictEqual([
      submissionIndividual1.sodar_uuid,
    ])
    expect(submission2.submission_individuals).toStrictEqual([
      submissionIndividual2.sodar_uuid,
    ])
    mutations.DELETE_SUBMISSION_INDIVIDUAL(
      store.state.clinvarExport,
      submissionIndividual1.sodar_uuid
    )
    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual(
      Object.fromEntries([
        [submissionIndividual2.sodar_uuid, submissionIndividual2],
      ])
    )
    expect(submission1.submission_individuals).toStrictEqual([])
    expect(submission2.submission_individuals).toStrictEqual([
      submissionIndividual2.sodar_uuid,
    ])
  })

  test('ADD_SUBMISSION_INDIVIDUAL', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual({})
    mutations.ADD_SUBMISSION_INDIVIDUAL(
      store.state.clinvarExport,
      submissionIndividual1
    )
    expect(store.state.clinvarExport.submissionIndividuals).toStrictEqual(
      Object.fromEntries([
        [submissionIndividual1.sodar_uuid, submissionIndividual1],
      ])
    )
  })

  test('ADD_SUBMISSION_INDIVIDUAL_TO_SUBMISSION', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const submissionIndividual2 = copy(secondSubmissionIndividual)
    const submission1 = copy(firstSubmission)

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    expect(submission1.submission_individuals).toStrictEqual([
      submissionIndividual1.sodar_uuid,
    ])
    mutations.ADD_SUBMISSION_INDIVIDUAL_TO_SUBMISSION(
      store.state.clinvarExport,
      {
        submissionIndividual: submissionIndividual2.sodar_uuid,
        submission: submission1.sodar_uuid,
      }
    )
    expect(submission1.submission_individuals).toStrictEqual([
      submissionIndividual1.sodar_uuid,
      submissionIndividual2.sodar_uuid,
    ])
  })
})

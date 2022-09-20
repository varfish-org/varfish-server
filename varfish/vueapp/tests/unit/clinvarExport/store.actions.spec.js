import { createLocalVue } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import {
  actions,
  AppState,
  MODEL_KEYS,
  WizardState,
} from '@/store/modules/clinvarExport'

import { copy } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstOrganisation,
  firstSubmission,
  firstSubmissionIndividual,
  firstSubmissionSet,
  firstSubmittingOrg,
  rawAppContext,
  secondSubmission,
  secondSubmissionIndividual,
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

// helper for testing action with expected mutations
const testAction = (action, payload, state, expectedMutations) => {
  let count = 0

  // mock commit
  const commit = (type, payload) => {
    const mutation = expectedMutations[count]

    expect(type).toBe(mutation.type)
    expect(payload).toStrictEqual(mutation.payload)

    count++
    if (count > expectedMutations.length) {
      const expectedLen = expectedMutations.length
      throw new Error(
        `too many mutations ${count} (of ${expectedLen}: ${type} / ${payload}`
      )
    }
  }

  // call the action with mocked store and arguments
  action({ commit, state }, payload)

  // check if no mutations should have been dispatched
  if (expectedMutations.length === 0) {
    expect(count).toBe(0)
  }
}

// helper for testing action with expected mutations
const testActionAsync = async (action, payload, state, expectedMutations) => {
  let count = 0

  // mock commit
  const commit = (type, payload) => {
    const mutation = expectedMutations[count]

    expect(type).toBe(mutation.type)
    expect(payload).toStrictEqual(mutation.payload)

    count++
    if (count > expectedMutations.length) {
      const expectedLen = expectedMutations.length
      throw new Error(
        `too many mutations ${count} (of ${expectedLen}: ${type} / ${payload}`
      )
    }
  }

  // call the action with mocked store and arguments
  await action({ commit, state }, payload).resolves

  await flushPromises()

  // check if no mutations should have been dispatched
  if (expectedMutations.length === 0) {
    expect(count).toBe(0)
  }
}

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('actions', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
    // Set reproducible time
    jest.useFakeTimers('modern')
    jest.setSystemTime(new Date(2020, 3, 1))
  })

  afterAll(() => {
    jest.useRealTimers()
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
    store.state.clinvarExport.appContext = copy(rawAppContext)
  })

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
  })

  test('initialize', () => {
    clinvarExportApi.getOrganisations.mockReturnValueOnce(
      Promise.resolve('res-SET_ORGANISATIONS')
    )
    clinvarExportApi.getSubmitters.mockReturnValueOnce(
      Promise.resolve('res-SET_SUBMITTERS')
    )
    clinvarExportApi.getAssertionMethods.mockReturnValueOnce(
      Promise.resolve('res-SET_ASSERTION_METHODS')
    )
    clinvarExportApi.getSubmissionSets.mockReturnValueOnce(
      Promise.resolve('res-SET_SUBMISSION_SETS')
    )
    clinvarExportApi.getSubmissions.mockReturnValueOnce(
      Promise.resolve('res-SET_SUBMISSIONS')
    )
    clinvarExportApi.getIndividuals.mockReturnValueOnce(
      Promise.resolve('res-SET_INDIVIDUALS')
    )
    clinvarExportApi.getSubmissionIndividuals.mockReturnValueOnce(
      Promise.resolve('res-SET_SUBMISSION_INDIVIDUALS')
    )
    clinvarExportApi.getFamilies.mockReturnValueOnce(
      Promise.resolve('res-SET_FAMILIES')
    )
    clinvarExportApi.getSubmittingOrgs.mockReturnValueOnce(
      Promise.resolve('res-SET_SUBMITTING_ORGS')
    )

    const payload = {
      appContext: rawAppContext,
    }

    testAction(actions.initialize, payload, store.state.clinvarExport, [
      // the first mutations are run in the same order
      {
        type: 'SET_APP_CONTEXT',
        payload: rawAppContext,
      },
      {
        type: 'SET_APP_STATE',
        payload: AppState.initializing,
      },
      // the next mutations are run when the async API calls return
      {
        type: 'SET_ORGANISATIONS',
        payload: 'res-SET_ORGANISATIONS',
      },
      {
        type: 'SET_SUBMITTERS',
        payload: 'res-SET_SUBMITTERS',
      },
      {
        type: 'SET_ASSERTION_METHODS',
        payload: 'res-SET_ASSERTION_METHODS',
      },
      {
        type: 'SET_SUBMISSION_SETS',
        payload: 'res-SET_SUBMISSION_SETS',
      },
      {
        type: 'SET_SUBMISSIONS',
        payload: 'res-SET_SUBMISSIONS',
      },
      {
        type: 'SET_INDIVIDUALS',
        payload: 'res-SET_INDIVIDUALS',
      },
      {
        type: 'SET_SUBMISSION_INDIVIDUALS',
        payload: 'res-SET_SUBMISSION_INDIVIDUALS',
      },
      {
        type: 'SET_FAMILIES',
        payload: 'res-SET_FAMILIES',
      },
      {
        type: 'SET_SUBMITTING_ORGS',
        payload: 'res-SET_SUBMITTING_ORGS',
      },
      // the last mutations will appear in THIS order
      {
        type: 'INITIALIZE_SUBMISSION_SET_ORGANISATIONS',
      },
      {
        type: 'SAVE_OLD_MODEL',
      },
      {
        type: 'SET_APP_STATE',
        payload: AppState.list,
      },
    ])
  })

  test('editSubmissionSet', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    testAction(
      actions.editSubmissionSet,
      submissionSet1.sodar_uuid,
      store.state.clinvarExport,
      [
        {
          type: 'SET_CURRENT_SUBMISSION_SET',
          payload: submissionSet1.sodar_uuid,
        },
        {
          type: 'SET_APP_STATE',
          payload: AppState.edit,
        },
      ]
    )
  })

  test('wizardSave with new submission set', async () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const organisation1 = copy(firstOrganisation)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const apiSubmissionSet1 = copy({
      ...submissionSet1,
      sodar_uuid: 'submission-set-1-uuid-from-api',
    })
    const apiSubmittingOrg1 = copy({
      ...submittingOrg1,
      sodar_uuid: 'submitting-org-1-uuid-from-api',
    })
    const apiSubmission1 = copy({
      ...submission1,
      sodar_uuid: 'submission-1-uuid-from-api',
    })
    const apiSubmissionIndividual1 = copy({
      ...submissionIndividual1,
      sodar_uuid: 'submission-individual-1-uuid-from-api',
    })

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    // NOT saving current state as old model to trigger the "create" code path.
    Vue.set(
      store.state.clinvarExport,
      'oldModel',
      copy(clinvarExportEmptyState)
    )

    clinvarExportApi.createSubmissionSet.mockReturnValueOnce(
      Promise.resolve(apiSubmissionSet1)
    )
    clinvarExportApi.createSubmittingOrg.mockReturnValueOnce(
      Promise.resolve(apiSubmittingOrg1)
    )
    clinvarExportApi.createSubmission.mockReturnValueOnce(
      Promise.resolve(apiSubmission1)
    )
    clinvarExportApi.createSubmissionIndividual.mockReturnValueOnce(
      Promise.resolve(apiSubmissionIndividual1)
    )

    await testActionAsync(actions.wizardSave, null, store.state.clinvarExport, [
      // preamble
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: true,
      },
      // actual actions
      {
        type: 'ADD_SUBMISSION_SET',
        payload: apiSubmissionSet1,
      },
      {
        type: 'SET_SUBMISSION_SET_LIST',
        payload: [apiSubmissionSet1],
      },
      {
        type: 'ADD_SUBMITTING_ORG',
        payload: apiSubmittingOrg1,
      },
      {
        type: 'ADD_SUBMITTING_ORG_TO_SUBMISSION_SET',
        payload: {
          submissionSet: apiSubmissionSet1.sodar_uuid,
          submittingOrg: apiSubmittingOrg1.sodar_uuid,
        },
      },
      {
        type: 'DELETE_SUBMITTING_ORG',
        payload: submittingOrg1.sodar_uuid,
      },
      {
        type: 'ADD_SUBMISSION',
        payload: apiSubmission1,
      },
      {
        type: 'ADD_SUBMISSION_TO_SUBMISSION_SET',
        payload: {
          submissionSet: apiSubmissionSet1.sodar_uuid,
          submission: apiSubmission1.sodar_uuid,
        },
      },
      {
        type: 'ADD_SUBMISSION_INDIVIDUAL',
        payload: apiSubmissionIndividual1,
      },
      {
        type: 'ADD_SUBMISSION_INDIVIDUAL_TO_SUBMISSION',
        payload: {
          submission: apiSubmission1.sodar_uuid,
          submissionIndividual: apiSubmissionIndividual1.sodar_uuid,
        },
      },
      {
        type: 'DELETE_SUBMISSION_INDIVIDUAL',
        payload: submissionIndividual1.sodar_uuid,
      },
      {
        type: 'DELETE_SUBMISSION',
        payload: submission1.sodar_uuid,
      },
      {
        type: 'DELETE_SUBMISSION_SET',
        payload: submissionSet1.sodar_uuid,
      },
      // appendix
      {
        type: 'SET_CURRENT_SUBMISSION_SET',
        payload: null,
      },
      {
        type: 'SET_CURRENT_SUBMISSION',
        payload: null,
      },
      {
        type: 'SAVE_OLD_MODEL',
      },
      {
        type: 'SET_APP_STATE',
        payload: AppState.list,
      },
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: false,
      },
    ])

    expect(clinvarExportApi.createSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.createSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
        submission_set: 'submission-set-1-uuid-from-api',
      },
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.createSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmission.mock.calls[0]).toEqual([
      {
        ...submission1,
        sort_order: 0,
        submission_set: 'submission-set-1-uuid-from-api',
      },
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.createSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.createSubmissionIndividual.mock.calls[0]).toEqual([
      {
        ...submissionIndividual1,
        sort_order: 0,
        submission: 'submission-1-uuid-from-api',
      },
      store.state.clinvarExport.appContext,
    ])
  })

  test('wizardSave with existing submission set and no "inner" changes', async () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const organisation1 = copy(firstOrganisation)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const apiSubmissionSet1 = copy({
      ...submissionSet1,
      sodar_uuid: 'submission-set-1-uuid-from-api',
    })
    const apiSubmittingOrg1 = copy({
      ...submittingOrg1,
      sodar_uuid: 'submitting-org-1-uuid-from-api',
    })
    const apiSubmission1 = copy({
      ...submission1,
      sodar_uuid: 'submission-1-uuid-from-api',
    })
    const apiSubmissionIndividual1 = copy({
      ...submissionIndividual1,
      sodar_uuid: 'submission-individual-1-uuid-from-api',
    })

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    // Save current state as old model to trigger the "update" code path.
    Vue.set(
      store.state.clinvarExport,
      'oldModel',
      copy(
        Object.fromEntries(
          MODEL_KEYS.map((k) => [k, store.state.clinvarExport[k]])
        )
      )
    )

    clinvarExportApi.updateSubmissionSet.mockReturnValueOnce(
      Promise.resolve(apiSubmissionSet1)
    )
    clinvarExportApi.updateSubmittingOrg.mockReturnValueOnce(
      Promise.resolve(apiSubmittingOrg1)
    )
    clinvarExportApi.updateSubmission.mockReturnValueOnce(
      Promise.resolve(apiSubmission1)
    )
    clinvarExportApi.updateSubmissionIndividual.mockReturnValueOnce(
      Promise.resolve(apiSubmissionIndividual1)
    )

    await testActionAsync(actions.wizardSave, null, store.state.clinvarExport, [
      // preamble
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: true,
      },
      // actual actions (none as no new individuals are added)
      // appendix
      {
        type: 'SET_CURRENT_SUBMISSION_SET',
        payload: null,
      },
      {
        type: 'SET_CURRENT_SUBMISSION',
        payload: null,
      },
      {
        type: 'SAVE_OLD_MODEL',
      },
      {
        type: 'SET_APP_STATE',
        payload: AppState.list,
      },
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: false,
      },
    ])

    expect(clinvarExportApi.updateSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
      },
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.updateSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmission.mock.calls[0]).toEqual([
      {
        ...submission1,
        sort_order: 0,
      },
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.updateSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.updateSubmissionIndividual.mock.calls[0]).toEqual([
      {
        ...submissionIndividual1,
        sort_order: 0,
      },
      store.state.clinvarExport.appContext,
    ])
  })

  test('wizardSave with existing submission set that removes submission', async () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const organisation1 = copy(firstOrganisation)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const apiSubmissionSet1 = copy(submissionSet1)
    const apiSubmittingOrg1 = copy(submittingOrg1)

    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    // Save current state as old model to trigger the "update" code path when removing things below
    Vue.set(
      store.state.clinvarExport,
      'oldModel',
      copy(
        Object.fromEntries(
          MODEL_KEYS.map((k) => [k, store.state.clinvarExport[k]])
        )
      )
    )
    // Now remove submission to trigger the deletions in the "update" code path
    Vue.set(store.state.clinvarExport, 'currentSubmission', null)
    Vue.delete(store.state.clinvarExport.submissions, submission1.sodar_uuid)
    Vue.set(submissionSet1, 'submissions', [])

    clinvarExportApi.updateSubmissionSet.mockReturnValueOnce(
      Promise.resolve(apiSubmissionSet1)
    )
    clinvarExportApi.updateSubmittingOrg.mockReturnValueOnce(
      Promise.resolve(apiSubmittingOrg1)
    )
    clinvarExportApi.deleteSubmissionIndividual.mockReturnValueOnce(
      Promise.resolve()
    )
    clinvarExportApi.deleteSubmission.mockReturnValueOnce(Promise.resolve())

    await testActionAsync(actions.wizardSave, null, store.state.clinvarExport, [
      // preamble
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: true,
      },
      // actual actions (none as no new individuals are added)
      {
        type: 'DELETE_SUBMISSION_INDIVIDUAL',
        payload: submissionIndividual1.sodar_uuid,
      },
      {
        type: 'DELETE_SUBMISSION',
        payload: submission1.sodar_uuid,
      },
      // appendix
      {
        type: 'SET_CURRENT_SUBMISSION_SET',
        payload: null,
      },
      {
        type: 'SET_CURRENT_SUBMISSION',
        payload: null,
      },
      {
        type: 'SAVE_OLD_MODEL',
      },
      {
        type: 'SET_APP_STATE',
        payload: AppState.list,
      },
      {
        type: 'SET_APP_SERVER_INTERACTION',
        payload: false,
      },
    ])

    expect(clinvarExportApi.updateSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
      },
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.deleteSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmission.mock.calls[0]).toEqual([
      submission1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls[0]).toEqual([
      submissionIndividual1,
      store.state.clinvarExport.appContext,
    ])
  })

  test.each([[true], [false]])(
    'createNewSubmissionSet existingSubmissionSet=%p',
    (existingSubmissionSet) => {
      if (existingSubmissionSet) {
        const oldSubmissionSet = {
          sodar_uuid: 'fakeUuid',
          date: '4/1/2020, 12:00:00 AM',
          title: 'New Submission Set',
          state: 'draft',
          sort_order: 0,
          submitter: null,
          organisations: [],
          submitting_orgs: [],
          submissions: [],
        }
        Vue.set(
          store.state.clinvarExport.submissionSets,
          oldSubmissionSet.sodar_uuid,
          oldSubmissionSet
        )
      }

      const expectedSubmissionSet = {
        sodar_uuid: MOCK_UUID_VALUE,
        date_modified: '4/1/2020, 12:00:00 AM',
        title: existingSubmissionSet
          ? 'New Submission Set #2'
          : 'New Submission Set',
        state: 'draft',
        sort_order: existingSubmissionSet ? 1 : 0,
        submitter: null,
        organisations: [],
        submitting_orgs: [],
        submissions: [],
      }

      testAction(
        actions.createNewSubmissionSet,
        null,
        store.state.clinvarExport,
        [
          {
            type: 'ADD_SUBMISSION_SET',
            payload: expectedSubmissionSet,
          },
          {
            type: 'SET_CURRENT_SUBMISSION_SET',
            payload: expectedSubmissionSet.sodar_uuid,
          },
          {
            type: 'SET_WIZARD_STATE',
            payload: WizardState.submissionSet,
          },
          {
            type: 'SET_APP_STATE',
            payload: AppState.add,
          },
        ]
      )
    }
  )

  test('setWizardState', () => {
    testAction(
      actions.setWizardState,
      WizardState.submissionSet,
      store.state.clinvarExport,
      [
        {
          type: 'SET_WIZARD_STATE',
          payload: WizardState.submissionSet,
        },
      ]
    )
  })

  test('wizardRemove', async () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const organisation1 = copy(firstOrganisation)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    Vue.set(
      store.state.clinvarExport,
      'oldModel',
      copy(clinvarExportEmptyState)
    )
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport.submittingOrgs,
      submittingOrg1.sodar_uuid,
      submittingOrg1
    )
    Vue.set(
      store.state.clinvarExport.organisations,
      organisation1.sodar_uuid,
      organisation1
    )
    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    Vue.set(
      store.state.clinvarExport,
      'oldModel',
      copy(
        Object.fromEntries(
          MODEL_KEYS.map((k) => [k, store.state.clinvarExport[k]])
        )
      )
    )

    clinvarExportApi.deleteSubmittingOrg.mockReturnValueOnce(Promise.resolve())
    clinvarExportApi.deleteSubmissionIndividual.mockReturnValueOnce(
      Promise.resolve()
    )
    clinvarExportApi.deleteSubmission.mockReturnValueOnce(Promise.resolve())
    clinvarExportApi.deleteSubmissionSet.mockReturnValueOnce(Promise.resolve())

    await testActionAsync(
      actions.wizardRemove,
      WizardState.submissionSet,
      store.state.clinvarExport,
      [
        // preamble
        {
          type: 'SET_APP_SERVER_INTERACTION',
          payload: true,
        },
        {
          type: 'SET_APP_STATE',
          payload: AppState.list,
        },
        // actual actions
        {
          type: 'DELETE_SUBMITTING_ORG',
          payload: submittingOrg1.sodar_uuid,
        },
        {
          type: 'DELETE_SUBMISSION_INDIVIDUAL',
          payload: submissionIndividual1.sodar_uuid,
        },
        {
          type: 'DELETE_SUBMISSION',
          payload: submission1.sodar_uuid,
        },
        // appendix
        {
          type: 'DELETE_SUBMISSION_SET',
          payload: submissionSet1.sodar_uuid,
        },
        {
          type: 'SET_CURRENT_SUBMISSION_SET',
          payload: null,
        },
        {
          type: 'SET_CURRENT_SUBMISSION',
          payload: null,
        },
        {
          type: 'SAVE_OLD_MODEL',
        },
        {
          type: 'SET_APP_SERVER_INTERACTION',
          payload: false,
        },
      ]
    )

    expect(clinvarExportApi.deleteSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmittingOrg.mock.calls[0]).toEqual([
      submittingOrg1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls[0]).toEqual([
      submissionIndividual1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.deleteSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmission.mock.calls[0]).toEqual([
      submission1,
      store.state.clinvarExport.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.state.clinvarExport.appContext,
    ])
  })

  test('wizardCancel', () => {
    testAction(actions.wizardCancel, null, store.state.clinvarExport, [
      {
        type: 'SET_APP_STATE',
        payload: AppState.list,
      },
      {
        type: 'SET_CURRENT_SUBMISSION',
        payload: null,
      },
      {
        type: 'SET_CURRENT_SUBMISSION_SET',
        payload: null,
      },
      {
        type: 'RESTORE_OLD_MODEL',
      },
    ])
  })

  test('updateCurrentSubmissionSet', () => {
    const payload = {
      key: 'sort_order',
      value: 1,
    }
    testAction(
      actions.updateCurrentSubmissionSet,
      payload,
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_CURRENT_SUBMISSION_SET',
          payload,
        },
      ]
    )
  })

  test('updateCurrentSubmissionSetOrganisations', () => {
    const payload = 'fakePayload'
    testAction(
      actions.updateCurrentSubmissionSetOrganisations,
      payload,
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS',
          payload,
        },
      ]
    )
  })

  test('selectCurrentSubmission', () => {
    const payload = 'fakeUuid'
    testAction(
      actions.selectCurrentSubmission,
      payload,
      store.state.clinvarExport,
      [
        {
          type: 'SET_CURRENT_SUBMISSION',
          payload,
        },
      ]
    )
  })

  test('updateCurrentSubmission', () => {
    const payload = {
      key: 'sort_order',
      value: 1,
    }
    testAction(
      actions.updateCurrentSubmission,
      payload,
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_CURRENT_SUBMISSION',
          payload,
        },
      ]
    )
  })

  test('createSubmissionInCurrentSubmissionSet', () => {
    const payload = {
      smallVariant: null,
      submission: null,
      individualUuids: [],
    }
    testAction(
      actions.createSubmissionInCurrentSubmissionSet,
      payload,
      store.state.clinvarExport,
      [
        {
          type: 'CREATE_SUBMISSION_IN_CURRENT_SUBMISSION_SET',
          payload,
        },
      ]
    )
  })

  test.each([[true], [false]])('moveCurrentSubmission up = %p', (up) => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy({
      ...secondSubmission,
      sort_order: 1,
      submission_set: submissionSet1.sodar_uuid,
    })
    const submission2 = copy({
      ...firstSubmission,
      sort_order: 2,
      submission_set: submissionSet1.sodar_uuid,
    })
    submissionSet1.submissions = [
      submission1.sodar_uuid,
      submission2.sodar_uuid,
    ]

    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(
      store.state.clinvarExport,
      'currentSubmission',
      up ? submission2 : submission1
    )
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

    testAction(actions.moveCurrentSubmission, up, store.state.clinvarExport, [
      {
        type: 'UPDATE_CURRENT_SUBMISSION',
        payload: {
          key: 'sort_order',
          value: up ? 1 : 2,
        },
      },
      {
        type: 'UPDATE_SUBMISSION',
        payload: {
          submission: up ? submission1 : submission2,
          key: 'sort_order',
          value: up ? 2 : 1,
        },
      },
    ])
  })

  test('applySubmissionListSortOrder', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)

    testAction(
      actions.applySubmissionListSortOrder,
      [submission1, submission2],
      store.state.clinvarExport,
      [
        {
          type: 'APPLY_SUBMISSION_LIST_ORDER',
          payload: Object.fromEntries([
            [submission2.sodar_uuid, 1],
            [submission1.sodar_uuid, 0],
          ]),
        },
      ]
    )
  })

  test('deleteCurrentSubmission', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

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
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)

    testAction(actions.deleteCurrentSubmission, {}, store.state.clinvarExport, [
      {
        type: 'DELETE_SUBMISSION_INDIVIDUAL',
        payload: submissionIndividual1.sodar_uuid,
      },
      {
        type: 'DELETE_SUBMISSION',
        payload: submission1.sodar_uuid,
      },
      {
        type: 'SET_CURRENT_SUBMISSION',
        payload: null,
      },
    ])
  })

  test('updateSubmissionIndividual', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    testAction(
      actions.updateSubmissionIndividual,
      {
        submissionIndividual: submissionIndividual1,
        key: 'sort_order',
        value: 1,
      },
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_SUBMISSION_INDIVIDUAL',
          payload: {
            submissionIndividual: submissionIndividual1,
            key: 'sort_order',
            value: 1,
          },
        },
      ]
    )
  })

  test.each([[true], [false]])('moveSubmissionIndividual up? %p', (up) => {
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy({
      ...firstSubmissionIndividual,
      sort_order: 1,
    })
    const submissionIndividual2 = copy({
      ...secondSubmissionIndividual,
      sort_order: 2,
    })

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)
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
    Vue.set(submission1, 'submission_individuals', [
      submissionIndividual1.sodar_uuid,
      submissionIndividual2.sodar_uuid,
    ])
    Vue.set(submissionIndividual1, 'submission', submission1.sodar_uuid)
    Vue.set(submissionIndividual2, 'submission', submission1.sodar_uuid)

    testAction(
      actions.moveSubmissionIndividual,
      {
        submissionIndividual: up
          ? submissionIndividual2
          : submissionIndividual1,
        up,
      },
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_CURRENT_SUBMISSION',
          payload: {
            key: 'sort_order',
            value: up ? 1 : 2,
          },
        },
        {
          type: 'UPDATE_SUBMISSION',
          payload: {
            submission: up ? submissionIndividual1 : submissionIndividual2,
            key: 'sort_order',
            value: up ? 2 : 1,
          },
        },
      ]
    )
  })

  test('removeSubmissionIndividualFromCurrentSubmission', () => {
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    Vue.set(
      store.state.clinvarExport.submissions,
      submission1.sodar_uuid,
      submission1
    )
    Vue.set(
      store.state.clinvarExport.submissionIndividuals,
      submissionIndividual1.sodar_uuid,
      submissionIndividual1
    )
    Vue.set(store.state.clinvarExport, 'currentSubmission', submission1)

    testAction(
      actions.removeSubmissionIndividualFromCurrentSubmission,
      submissionIndividual1,
      store.state.clinvarExport,
      [
        {
          type: 'UPDATE_CURRENT_SUBMISSION',
          payload: {
            key: 'submission_individuals',
            value: [],
          },
        },
      ]
    )
  })
})

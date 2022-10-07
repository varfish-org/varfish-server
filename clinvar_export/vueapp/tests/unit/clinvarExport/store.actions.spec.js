import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import {
  AppState,
  MODEL_KEYS,
  useClinvarExportStore,
  WizardState,
} from '@clinvarexport/stores/clinvar-export'
import flushPromises from 'flush-promises'
import { createPinia, setActivePinia } from 'pinia'
import {
  afterAll,
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

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
  secondIndividual,
  secondOrganisation,
  secondSubmission,
  secondSubmissionIndividual,
} from '../fixtures.js'

const MOCK_UUID_VALUE = 'xxxxxxxx-xxxx-4xxx-mock-mockmockmock'

// Mock out UUIDv4 generation
vi.mock('@clinvarexport/helpers', () => {
  const origHelpersModule = vi.importActual('@clinvarexport/helpers')
  return {
    __esModule: true,
    ...origHelpersModule,
    uuidv4: vi.fn(() => {
      return MOCK_UUID_VALUE
    }),
  }
})

// Mock out the clinvarExport API
vi.mock('@clinvarexport/api/clinvarExport')

describe('actions', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Set reproducible time
    vi.useFakeTimers('modern')
    vi.setSystemTime(new Date(2020, 3, 1))
  })

  afterAll(() => {
    vi.useRealTimers()
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useClinvarExportStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('setCurrentSubmissionSet with NOT null', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    store.submissionSetList.push(submissionSet1)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1

    expect(store.currentSubmissionSet).toBe(null)
    store.setCurrentSubmissionSet(submissionSet1.sodar_uuid)
    expect(store.currentSubmissionSet).toEqual(submissionSet1)
  })

  test('setCurrentSubmissionSet with null', () => {
    const submissionSet1 = copy(firstSubmissionSet)

    store.submissionSetList.push(submissionSet1)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1

    expect(store.currentSubmissionSet).toEqual(submissionSet1)
    store.setCurrentSubmissionSet(null)
    expect(store.currentSubmissionSet).toBe(null)
  })

  test('SAVE_OLD_MODEL', () => {
    // This really only is a smoke test at the moment
    expect(store.oldModel).toBe(null)
    store.saveOldModel()
    expect(store.oldModel).toStrictEqual({
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

  test('restoreOldModel', () => {
    // This really only is a smoke test at the moment
    store.saveOldModel()
    store.restoreOldModel()
  })

  test('addSubmissionSet', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    expect(store.submissionSets).toStrictEqual({})
    expect(store.submissionSetList).toStrictEqual([])
    store.addSubmissionSet(submissionSet1)
    expect(Object.keys(store.submissionSets)).toStrictEqual([
      submissionSet1.sodar_uuid,
    ])
    expect(Object.values(store.submissionSets)).toStrictEqual([submissionSet1])
    expect(store.submissionSetList).toStrictEqual([submissionSet1])
  })

  test('SET_SUBMISSION_SETS', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    expect(store.submissionSets).toStrictEqual({})
    expect(store.submissionSetList).toStrictEqual([])
    store.setSubmissionSets([submissionSet1])
    expect(store.submissionSets).toStrictEqual(
      Object.fromEntries([[submissionSet1.sodar_uuid, submissionSet1]])
    )
    expect(store.submissionSetList).toStrictEqual([submissionSet1])
  })

  test('setWizardState', () => {
    expect(store.wizardState).toStrictEqual(WizardState.submissionSet)
    store.setWizardState(WizardState.submission)
    expect(store.wizardState).toStrictEqual(WizardState.submission)
  })

  test('updateCurrentSubmissionSetOrganisations noop', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[org1.sodar_uuid] = org1
    submissionSet1.organisations = [org1.sodar_uuid]
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    store.updateCurrentSubmissionSetOrganisations([org1.sodar_uuid])
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
  })

  test('updateCurrentSubmissionSetOrganisations add', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)
    const org2 = copy(secondOrganisation)

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[org1.sodar_uuid] = org1
    store.organisations[org2.sodar_uuid] = org2
    submissionSet1.organisations = [org1.sodar_uuid]
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    store.updateCurrentSubmissionSetOrganisations([
      org1.sodar_uuid,
      org2.sodar_uuid,
    ])
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
      MOCK_UUID_VALUE,
    ])
  })

  test('updateCurrentSubmissionSetOrganisations remove', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const org1 = copy(firstOrganisation)

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[org1.sodar_uuid] = org1
    submissionSet1.organisations = [org1.sodar_uuid]
    expect(submissionSet1.submitting_orgs).toStrictEqual([
      submittingOrg1.sodar_uuid,
    ])
    expect(submissionSet1.organisations).toStrictEqual([org1.sodar_uuid])
    store.updateCurrentSubmissionSetOrganisations([])
    expect(submissionSet1.submitting_orgs).toStrictEqual([])
  })

  test('updateCurrentSubmission', () => {
    const submission1 = copy(firstSubmission)

    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1

    expect(submission1).toStrictEqual(firstSubmission)
    store.updateCurrentSubmission({
      key: 'variant_chromosome',
      value: 'X',
    })
    expect(submission1).toStrictEqual({
      ...firstSubmission,
      variant_chromosome: 'X',
    })
  })

  test.each([[true], [false]])('deleteSubmission current? %s', (isCurrent) => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissions[submission1.sodar_uuid] = submission1
    if (isCurrent) {
      store.currentSubmission = submission1
    }
    store.deleteSubmission(submission1.sodar_uuid)
    expect(submissionSet1.submissions).toStrictEqual([])
    expect(store.submissions).toStrictEqual({})
    expect(store.currentSubmission).toStrictEqual(null)
  })

  test.each([[true], [false]])(
    'deleteSubmissionSet isCurrent?=%s',
    (isCurrent) => {
      const submissionSet1 = copy(firstSubmissionSet)

      store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
      store.submissionSetList.push(submissionSet1)
      if (isCurrent) {
        store['currentSubmissionSet'] = submissionSet1
      }
      store.deleteSubmissionSet(submissionSet1.sodar_uuid)
      expect(store.submissionSets).toStrictEqual({})
      expect(store.submissionSetList).toStrictEqual([])
      expect(store.currentSubmissionSet).toStrictEqual(null)
    }
  )

  test('createSubmissionInCurrentSubmissionSet', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission2 = copy(secondSubmission)
    const individual2 = copy(secondIndividual)
    const userAnnotation1 = copy(firstUserAnnotation)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.individuals[individual2.sodar_uuid] = individual2

    store.createSubmissionInCurrentSubmissionSet({
      smallVariant: userAnnotation1.small_variants[0],
      submission: submission2,
      individualUuids: [individual2.sodar_uuid],
    })
    expect(store.submissions).toStrictEqual({
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
        variant_start: '41201211',
        variant_stop: '41201211',
        variant_type: 'Variation',
      },
    })
    expect(store.currentSubmission).toBe(
      store.submissions[Object.keys(store.submissions)[0]]
    )
  })

  test('updateSubmissionIndividual', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1

    store.updateSubmissionIndividual({
      submissionIndividual: submissionIndividual1,
      key: 'sort_order',
      value: 101,
    })
    expect(submissionIndividual1).toStrictEqual({
      ...firstSubmissionIndividual,
      sort_order: 101,
    })
  })

  test('deleteSubmissionIndividual', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const submissionIndividual2 = copy(secondSubmissionIndividual)
    store.submissions[submission1.sodar_uuid] = submission1
    store.submissions[submission2.sodar_uuid] = submission2
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    store.submissionIndividuals[submissionIndividual2.sodar_uuid] =
      submissionIndividual2

    expect(store.submissionIndividuals).toStrictEqual(
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
    store.deleteSubmissionIndividual(submissionIndividual1.sodar_uuid)
    expect(store.submissionIndividuals).toStrictEqual(
      Object.fromEntries([
        [submissionIndividual2.sodar_uuid, submissionIndividual2],
      ])
    )
    expect(submission1.submission_individuals).toStrictEqual([])
    expect(submission2.submission_individuals).toStrictEqual([
      submissionIndividual2.sodar_uuid,
    ])
  })

  test('initialize', async () => {
    const organisation1 = copy(firstOrganisation)
    const submitter1 = copy(firstSubmitter)
    const assertionMethod1 = copy(firstAssertionMethod)
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)
    const individual1 = copy(firstIndividual)
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    const family1 = copy(firstFamily)
    const submittingOrg1 = copy(firstSubmittingOrg)

    clinvarExportApi.getOrganisations.mockReturnValueOnce(
      Promise.resolve([organisation1])
    )
    clinvarExportApi.getSubmitters.mockReturnValueOnce(
      Promise.resolve([submitter1])
    )
    clinvarExportApi.getAssertionMethods.mockReturnValueOnce(
      Promise.resolve([assertionMethod1])
    )
    clinvarExportApi.getSubmissionSets.mockReturnValueOnce(
      Promise.resolve([submissionSet1])
    )
    clinvarExportApi.getSubmissions.mockReturnValueOnce(
      Promise.resolve([submission1])
    )
    clinvarExportApi.getIndividuals.mockReturnValueOnce(
      Promise.resolve([individual1])
    )
    clinvarExportApi.getSubmissionIndividuals.mockReturnValueOnce(
      Promise.resolve([submissionIndividual1])
    )
    clinvarExportApi.getFamilies.mockReturnValueOnce(Promise.resolve([family1]))
    clinvarExportApi.getSubmittingOrgs.mockReturnValueOnce(
      Promise.resolve([submittingOrg1])
    )

    await store.initialize(rawAppContext)

    flushPromises()

    expect(store.appContext).toEqual(rawAppContext)
    expect(store.organisations).toEqual(
      Object.fromEntries([[organisation1.sodar_uuid, organisation1]])
    )
  })

  test('editSubmissionSet', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = null

    store.editSubmissionSet(submissionSet1.sodar_uuid)

    expect(store.currentSubmissionSet).toEqual(submissionSet1)
    expect(store.appState).toBe(AppState.edit)
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

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[organisation1.sodar_uuid] = organisation1
    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    // NOT saving current state as old model to trigger the "create" code path.
    store['oldModel'] = copy(clinvarExportEmptyState)

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

    await store.wizardSave()

    expect(store.submissionSets).toEqual(
      Object.fromEntries([[apiSubmissionSet1.sodar_uuid, apiSubmissionSet1]])
    )
    expect(store.currentSubmissionSet).toEqual(null)
    expect(store.submissionSetList).toEqual([apiSubmissionSet1])
    expect(store.submittingOrgs).toEqual(
      Object.fromEntries([[apiSubmittingOrg1.sodar_uuid, apiSubmittingOrg1]])
    )
    expect(store.submissions).toEqual(
      Object.fromEntries([[apiSubmission1.sodar_uuid, apiSubmission1]])
    )
    expect(store.submissionIndividuals).toEqual(
      Object.fromEntries([
        [apiSubmissionIndividual1.sodar_uuid, apiSubmissionIndividual1],
      ])
    )

    expect(clinvarExportApi.createSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.appContext,
    ])
    expect(clinvarExportApi.createSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
        submission_set: 'submission-set-1-uuid-from-api',
      },
      store.appContext,
    ])
    expect(clinvarExportApi.createSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.createSubmission.mock.calls[0]).toEqual([
      {
        ...submission1,
        sort_order: 0,
        submission_set: 'submission-set-1-uuid-from-api',
        submission_individuals: [submissionIndividual1.sodar_uuid],
      },
      store.appContext,
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
      store.appContext,
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

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[organisation1.sodar_uuid] = organisation1
    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    // Save current state as old model to trigger the "update" code path.
    store.oldModel = copy(
      Object.fromEntries(MODEL_KEYS.map((k) => [k, store[k]]))
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

    await store.wizardSave()

    expect(store.currentSubmissionSet).toBe(null)
    expect(store.currentSubmission).toBe(null)
    expect(store.oldModel).toEqual(
      copy(Object.fromEntries(MODEL_KEYS.map((k) => [k, store[k]])))
    )
    expect(store.appState).toEqual(AppState.list)

    expect(clinvarExportApi.updateSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.appContext,
    ])
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
      },
      store.appContext,
    ])
    expect(clinvarExportApi.updateSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmission.mock.calls[0]).toEqual([
      {
        ...submission1,
        sort_order: 0,
      },
      store.appContext,
    ])
    expect(clinvarExportApi.updateSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.updateSubmissionIndividual.mock.calls[0]).toEqual([
      {
        ...submissionIndividual1,
        sort_order: 0,
      },
      store.appContext,
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

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[organisation1.sodar_uuid] = organisation1
    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    // Save current state as old model to trigger the "update" code path when removing things below
    store.oldModel = copy(
      Object.fromEntries(MODEL_KEYS.map((k) => [k, store[k]]))
    )
    // Now remove submission to trigger the deletions in the "update" code path
    store.currentSubmission = null
    delete store.submissions[submission1.sodar_uuid]
    submissionSet1.submissions = []

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

    await store.wizardSave()

    expect(
      store.submissionIndividuals[submissionIndividual1.sodar_uuid]
    ).toBeUndefined()
    expect(store.submissions[submission1.sodar_uuid]).toBeUndefined()
    expect(store.currentSubmissionSet).toBe(null)
    expect(store.currentSubmission).toBe(null)
    expect(store.oldModel).toEqual(
      copy(Object.fromEntries(MODEL_KEYS.map((k) => [k, store[k]])))
    )
    expect(store.appState).toEqual(AppState.list)

    expect(clinvarExportApi.updateSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.appContext,
    ])
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.updateSubmittingOrg.mock.calls[0]).toEqual([
      {
        ...submittingOrg1,
        sort_order: 0,
      },
      store.appContext,
    ])
    expect(clinvarExportApi.deleteSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmission.mock.calls[0]).toEqual([
      submission1,
      store.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls[0]).toEqual([
      submissionIndividual1,
      store.appContext,
    ])
  })

  test.each([[true], [false]])(
    'createNewSubmissionSet existingSubmissionSet=%s',
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
        store.submissionSets[oldSubmissionSet.sodar_uuid] = oldSubmissionSet
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

      store.createNewSubmissionSet()

      expect(store.submissionSets[MOCK_UUID_VALUE]).toEqual(
        expectedSubmissionSet
      )
      expect(store.currentSubmissionSet).toBe(
        store.submissionSets[MOCK_UUID_VALUE]
      )
      expect(store.wizardState).toEqual(WizardState.submissionSet)
      expect(store.appState).toEqual(AppState.add)
    }
  )

  test('setWizardState', () => {
    store.setWizardState(WizardState.submissionSet)

    expect(store.wizardState).toEqual(WizardState.submissionSet)
  })

  test('wizardRemove', async () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submittingOrg1 = copy(firstSubmittingOrg)
    const organisation1 = copy(firstOrganisation)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    store['oldModel'] = copy(clinvarExportEmptyState)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
    store.currentSubmissionSet = submissionSet1
    store.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    store.organisations[organisation1.sodar_uuid] = organisation1
    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    store.oldModel = copy(
      Object.fromEntries(MODEL_KEYS.map((k) => [k, store[k]]))
    )

    clinvarExportApi.deleteSubmittingOrg.mockReturnValueOnce(Promise.resolve())
    clinvarExportApi.deleteSubmissionIndividual.mockReturnValueOnce(
      Promise.resolve()
    )
    clinvarExportApi.deleteSubmission.mockReturnValueOnce(Promise.resolve())
    clinvarExportApi.deleteSubmissionSet.mockReturnValueOnce(Promise.resolve())

    await store.wizardRemove()

    expect(store.appState).toEqual(AppState.list)
    expect(store.submittingOrgs).toEqual({})
    expect(store.submissionIndividuals).toEqual({})
    expect(store.submissions).toEqual({})
    expect(store.submissionSets).toEqual({})
    expect(store.currentSubmissionSet).toEqual(null)
    expect(store.currentSubmission).toEqual(null)

    expect(clinvarExportApi.deleteSubmittingOrg.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmittingOrg.mock.calls[0]).toEqual([
      submittingOrg1,
      store.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls.length).toBe(
      1
    )
    expect(clinvarExportApi.deleteSubmissionIndividual.mock.calls[0]).toEqual([
      submissionIndividual1,
      store.appContext,
    ])
    expect(clinvarExportApi.deleteSubmission.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmission.mock.calls[0]).toEqual([
      submission1,
      store.appContext,
    ])
    expect(clinvarExportApi.deleteSubmissionSet.mock.calls.length).toBe(1)
    expect(clinvarExportApi.deleteSubmissionSet.mock.calls[0]).toEqual([
      submissionSet1,
      store.appContext,
    ])
  })

  test('wizardCancel', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)
    store.oldModel = copy(clinvarExportEmptyState)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1

    store.wizardCancel()

    expect(store.submissionSets).toEqual({})
    expect(store.submissions).toEqual({})
    expect(store.currentSubmissionSet).toEqual(null)
    expect(store.currentSubmission).toEqual(null)
  })

  test('createSubmissionInCurrentSubmissionSet', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission2 = copy(secondSubmission)
    const individual2 = copy(secondIndividual)
    const userAnnotation1 = copy(firstUserAnnotation)
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.currentSubmissionSet = submissionSet1
    store.individuals[individual2.sodar_uuid] = individual2

    store.createSubmissionInCurrentSubmissionSet({
      smallVariant: userAnnotation1.small_variants[0],
      submission: submission2,
      individualUuids: [individual2.sodar_uuid],
    })

    expect(store.submissions).toStrictEqual({
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
        variant_start: '41201211',
        variant_stop: '41201211',
        variant_type: 'Variation',
      },
    })
    expect(store.currentSubmission).toBe(
      store.submissions[Object.keys(store.submissions)[0]]
    )
  })

  test.each([[true], [false]])('moveCurrentSubmission up = %s', (up) => {
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

    store.currentSubmissionSet = submissionSet1
    store.currentSubmission = up ? submission2 : submission1
    store.submissions[submission1.sodar_uuid] = submission1
    store.submissions[submission2.sodar_uuid] = submission2

    store.moveCurrentSubmission(up)

    expect(submission1.sort_order).toBe(2)
    expect(submission2.sort_order).toBe(1)
  })

  test('applySubmissionListSortOrder', () => {
    const submission1 = copy(firstSubmission)
    const submission2 = copy(secondSubmission)
    store.submissions[submission1.sodar_uuid] = submission1
    store.submissions[submission2.sodar_uuid] = submission2

    store.applySubmissionListSortOrder([submission2, submission1])

    expect(submission1.sort_order).toBe(1)
    expect(submission2.sort_order).toBe(0)
  })

  test('deleteCurrentSubmission', () => {
    const submissionSet1 = copy(firstSubmissionSet)
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissions[submission1.sodar_uuid] = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    store.currentSubmissionSet = submissionSet1
    store.currentSubmission = submission1

    store.deleteCurrentSubmission()

    expect(store.submissionIndividuals).toEqual({})
    expect(store.submissions).toEqual({})
    expect(store.currentSubmission).toEqual(null)
  })

  test('updateSubmissionIndividual', () => {
    const submissionIndividual1 = copy(firstSubmissionIndividual)
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1

    store.updateSubmissionIndividual({
      submissionIndividual: submissionIndividual1,
      key: 'sort_order',
      value: 10,
    })

    expect(
      store.submissionIndividuals[submissionIndividual1.sodar_uuid].sort_order
    ).toBe(10)
  })

  test.each([[true], [false]])('moveSubmissionIndividual up? %s', (up) => {
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy({
      ...firstSubmissionIndividual,
      sort_order: 1,
    })
    const submissionIndividual2 = copy({
      ...secondSubmissionIndividual,
      sort_order: 2,
    })

    store.submissions[submission1.sodar_uuid] = submission1
    store.currentSubmission = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    store.submissionIndividuals[submissionIndividual2.sodar_uuid] =
      submissionIndividual2
    submission1.submission_individuals = [
      submissionIndividual1.sodar_uuid,
      submissionIndividual2.sodar_uuid,
    ]
    submissionIndividual1.submission = submission1.sodar_uuid
    submissionIndividual2.submission = submission1.sodar_uuid

    store.moveSubmissionIndividual({
      submissionIndividual: up ? submissionIndividual2 : submissionIndividual1,
      up,
    })
    expect(submissionIndividual1.sort_order).toBe(2)
    expect(submissionIndividual2.sort_order).toBe(1)
  })

  test('removeSubmissionIndividualFromCurrentSubmission', () => {
    const submission1 = copy(firstSubmission)
    const submissionIndividual1 = copy(firstSubmissionIndividual)

    store.submissions[submission1.sodar_uuid] = submission1
    store.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    store.currentSubmission = submission1

    store.removeSubmissionIndividualFromCurrentSubmission(submissionIndividual1)

    expect(store.currentSubmission.submission_individuals).toEqual([])
  })
})

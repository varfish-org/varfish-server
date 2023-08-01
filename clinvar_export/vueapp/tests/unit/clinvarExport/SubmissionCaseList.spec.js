import SubmissionCaseList from '@clinvarexport/components/SubmissionCaseList.vue'
import { WizardState } from '@clinvarexport/stores/clinvar-export'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import {
  afterAll,
  afterEach,
  beforeAll,
  describe,
  expect,
  test,
  vi,
} from 'vitest'

import { copy } from '../../testUtils'
import {
  clinvarExportEmptyState,
  firstIndividual,
  firstOrganisation,
  firstSubmission,
  firstSubmissionIndividual,
  firstSubmissionSet,
  firstSubmitter,
  firstSubmittingOrg,
  secondIndividual,
} from '../fixtures'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState, extraArgs) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  if (!extraArgs) {
    extraArgs = {}
  }
  return shallowMount(SubmissionCaseList, {
    global: {
      plugins: [
        createTestingPinia({
          initialState: { clinvarExport: clinvarExportState },
          createSpy: vi.fn,
        }),
      ],
    },
    ...extraArgs,
  })
}
// Mock out the clinvarExport API
vi.mock('@clinvarexport/api/clinvarExport')

describe('SubmissionCaseList.vue', () => {
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
    const result = copy(clinvarExportEmptyState)
    organisation1 = copy(firstOrganisation)
    result.organisations[organisation1.sodar_uuid] = organisation1
    submitter1 = copy(firstSubmitter)
    result.submitters[submitter1.sodar_uuid] = submitter1
    submittingOrg1 = copy(firstSubmittingOrg)
    result.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    submission1 = copy(firstSubmission)
    result.submissions[submission1.sodar_uuid] = submission1
    result.currentSubmission = submission1
    submissionSet1 = copy(firstSubmissionSet)
    result.wizardState = WizardState.submissionSet
    result.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    submissionIndividual1 = copy(firstSubmissionIndividual)
    result.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    individual1 = copy(firstIndividual)
    result.individuals[individual1.sodar_uuid] = individual1
    individual2 = copy(secondIndividual)
    result.individuals[individual2.sodar_uuid] = individual2
    result.submissionSetList = [submissionSet1]
    result.currentSubmissionSet = submissionSet1
    result.wizardState = WizardState.submissions
    return result
  }

  test('check computed properties', async () => {
    const wrapper = makeWrapper(setupSimpleCase())

    expect(wrapper.vm.caseCount).toEqual(1)
    expect(wrapper.vm.caseSubmissionIndividuals).toEqual([
      { wrapped: submissionIndividual1 },
    ])
  })

  test('check functions', async () => {
    setupSimpleCase()

    const wrapper = makeWrapper(setupSimpleCase())

    expect(wrapper.vm.getModalIndividualList()).toEqual([individual2])
    expect(wrapper.vm.getPhenotypeDisplay(individual1)).toEqual(
      '(HP:123456) some name, (HP:98235) another name'
    )
  })
})

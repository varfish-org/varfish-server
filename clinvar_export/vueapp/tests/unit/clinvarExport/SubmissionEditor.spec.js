import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import SubmissionEditor from '@clinvarexport/components/SubmissionEditor.vue'
import { WizardState } from '@clinvarexport/stores/clinvar-export'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, test, vi } from 'vitest'

import { copy } from '../../testUtils'
import {
  clinvarExportEmptyState,
  firstAssertionMethod,
  firstIndividual,
  firstOrganisation,
  firstSubmission,
  firstSubmissionIndividual,
  firstSubmissionSet,
  firstSubmitter,
  firstSubmittingOrg,
} from '../fixtures'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  return shallowMount(SubmissionEditor, {
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

describe('SubmissionEditor.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
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
  let assertionMethod1
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
    individual1 = copy(firstIndividual)
    result.individuals[individual1.sodar_uuid] = individual1
    submissionIndividual1 = copy(firstSubmissionIndividual)
    result.submissionIndividuals[submissionIndividual1.sodar_uuid] =
      submissionIndividual1
    result.currentSubmission = submission1
    submissionSet1 = copy(firstSubmissionSet)
    assertionMethod1 = copy(firstAssertionMethod)
    result.assertionMethods[assertionMethod1.sodar_uuid] = assertionMethod1
    result.wizardState = WizardState.submissionSet
    result.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    result.submissionSetList = [submissionSet1]
    result.currentSubmissionSet = submissionSet1
    result.wizardState = WizardState.submissions
    return result
  }

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
  })

  test('check get{Submission,OmimDisease}Label', async () => {
    const wrapper = makeWrapper(setupSimpleCase())

    expect(wrapper.vm.getSubmissionLabel()).toEqual('new variant')
  })
})

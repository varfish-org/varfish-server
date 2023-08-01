import SubmissionSetEditor from '@clinvarexport/components/SubmissionSetEditor.vue'
import { WizardState } from '@clinvarexport/stores/clinvar-export'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, test, vi } from 'vitest'
import { nextTick } from 'vue'

import { copy } from '../../testUtils'
import {
  clinvarExportEmptyState,
  firstOrganisation,
  firstSubmissionSet,
  firstSubmitter,
  firstSubmittingOrg,
} from '../fixtures'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  return shallowMount(SubmissionSetEditor, {
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

describe('SubmissionSetEditor.vue', () => {
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
  const setupSimpleCase = () => {
    const result = copy(clinvarExportEmptyState)
    organisation1 = copy(firstOrganisation)
    result.organisations[organisation1.sodar_uuid] = organisation1
    submitter1 = copy(firstSubmitter)
    result.submitters[submitter1.sodar_uuid] = submitter1
    submittingOrg1 = copy(firstSubmittingOrg)
    result.submittingOrgs[submittingOrg1.sodar_uuid] = submittingOrg1
    submissionSet1 = copy(firstSubmissionSet)
    result.wizardState = WizardState.submissionSet
    result.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    result.submissionSetList = [submissionSet1]
    result.currentSubmissionSet = submissionSet1
    return result
  }

  test('check methods', async () => {
    const wrapper = makeWrapper(setupSimpleCase())
    await nextTick() // wait for changes to store to take effect

    expect(wrapper.vm.getOrgLabel(organisation1.sodar_uuid)).toEqual(
      organisation1.name
    )
    expect(wrapper.vm.isValid()).toBe(true)
  })
})

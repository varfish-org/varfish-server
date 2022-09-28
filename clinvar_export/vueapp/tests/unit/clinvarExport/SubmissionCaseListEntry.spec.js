import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, test, vi } from 'vitest'

import SubmissionCaseListEntry from '@/components/SubmissionCaseListEntry.vue'
import { useClinvarExportStore } from '@/stores/clinvar-export'
import { WizardState } from '@/stores/clinvar-export.js'

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
  secondIndividual,
  secondSubmissionIndividual,
} from '../fixtures.js'

// Mock out the clinvarExport API
vi.mock('@/api/clinvarExport')

describe('SubmissionCaseListEntry.vue', () => {
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
  let submissionIndividual2
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
    submissionIndividual2 = copy({
      ...secondSubmissionIndividual,
      submission: submission1.sodar_uuid,
      sort_order: 1,
    })
    result.submissionIndividuals[submissionIndividual2.sodar_uuid] =
      submissionIndividual2
    result.currentSubmission.submission_individuals = [
      submissionIndividual1.sodar_uuid,
      submissionIndividual2.sodar_uuid,
    ]
    individual1 = copy(firstIndividual)
    result.individuals[individual1.sodar_uuid] = individual1
    individual2 = copy(secondIndividual)
    result.individuals[individual2.sodar_uuid] = individual2
    result.submissionSetList = [submissionSet1]
    result.currentSubmissionSet = submissionSet1
    result.wizardState = WizardState.submissions
    return result
  }

  const testSetup = async (siNo) => {
    const component = {
      data: () => {
        return {
          submissionIndividual:
            siNo === 2 ? submissionIndividual2 : submissionIndividual1,
        }
      },
      template:
        '<div><submission-case-list-entry ref="listEntryRef" v-model="submissionIndividual">' +
        '</submission-case-list-entry></div>',
      components: { SubmissionCaseListEntry },
    }

    return mount(component, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: { clinvarExport: setupSimpleCase() },
            createSpy: vi.fn,
          }),
        ],
      },
    })
  }

  test('check computed properties', async () => {
    const wrapper = await testSetup(1)
    const submissionCaseListEntry = wrapper.vm.$refs.listEntryRef
    const store = useClinvarExportStore()

    expect(submissionCaseListEntry.hpoTermsLoading).toEqual(false)
    expect(submissionCaseListEntry.store.appContext).toEqual(store.appContext)
  })

  test('check funcions', async () => {
    const wrapper = await testSetup(1)
    const submissionCaseListEntry = wrapper.vm.$refs.listEntryRef

    expect(submissionCaseListEntry.isValid()).toBe(true)
  })

  test('check isMoveDisabled - first', async () => {
    const wrapper = await testSetup(1)
    const submissionCaseListEntry = wrapper.vm.$refs.listEntryRef

    expect(submissionCaseListEntry.isMoveDisabled(true)).toBe(true)
    expect(submissionCaseListEntry.isMoveDisabled(false)).toBe(false)
  })

  test('check isMoveDisabled - second', async () => {
    const wrapper = await testSetup(2)
    const submissionCaseListEntry = wrapper.vm.$refs.listEntryRef

    expect(submissionCaseListEntry.isMoveDisabled(true)).toBe(false)
    expect(submissionCaseListEntry.isMoveDisabled(false)).toBe(true)
  })
})

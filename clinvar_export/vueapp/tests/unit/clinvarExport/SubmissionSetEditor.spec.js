import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionSetEditor from '@/components/SubmissionSetEditor.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

import { copy } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstOrganisation,
  firstSubmissionSet,
  firstSubmitter,
  firstSubmittingOrg,
  rawAppContext,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionSetEditor.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      initialize: jest.fn(),
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
    submissionSet1 = copy(firstSubmissionSet)
    Vue.set(store.state.clinvarExport, 'wizardState', WizardState.submissionSet)
    Vue.set(
      store.state.clinvarExport.submissionSets,
      submissionSet1.sodar_uuid,
      submissionSet1
    )
    Vue.set(store.state.clinvarExport, 'submissionSetList', [submissionSet1])
    Vue.set(store.state.clinvarExport, 'currentSubmissionSet', submissionSet1)
  }

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
  })

  test('check computed state', async () => {
    setupSimpleCase()

    const wrapper = shallowMount(SubmissionSetEditor, {
      store,
      localVue,
    })
    const submissionSetEditor = wrapper.vm.$root.$children[0]

    expect(submissionSetEditor.stateChoices).toEqual([
      'draft',
      'discontinued',
      'pending',
      'submitted',
      'released',
      'rejected',
    ])
    expect(submissionSetEditor.submitterChoices).toEqual([
      {
        text: 'Submitter Name',
        value: '22222222-2222-2222-2222-222222222222',
      },
    ])
    expect(submissionSetEditor.orgUuids).toEqual([organisation1.sodar_uuid])
  })

  test('check methods', async () => {
    setupSimpleCase()

    const wrapper = shallowMount(SubmissionSetEditor, {
      store,
      localVue,
    })
    const submissionSetEditor = wrapper.vm.$root.$children[0]

    expect(submissionSetEditor.getOrgLabel(organisation1.sodar_uuid)).toEqual(
      organisation1.name
    )
    expect(submissionSetEditor.isValid()).toBe(true)
  })
})

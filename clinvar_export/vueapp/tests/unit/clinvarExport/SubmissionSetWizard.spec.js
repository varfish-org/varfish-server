import { createLocalVue, shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionSetWizard from '@/components/SubmissionSetWizard.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

import { copy } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstSubmissionSet,
  rawAppContext,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionSetWizard.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
    // Mock out global.alert() and global.confirm()
    global.alert = jest.fn()
    global.confirm = jest.fn()
  })

  afterAll(() => {
    global.alert.mockRestore()
    global.confirm.mockRestore()
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      wizardRemove: jest.fn(),
      wizardCancel: jest.fn(),
      wizardSave: jest.fn(),
      setWizardState: jest.fn(),
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
  let submissionSet1
  const setupSimpleCase = () => {
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

  const testPreamble = async () => {
    setupSimpleCase()

    const wrapper = shallowMount(SubmissionSetWizard, {
      store,
      localVue,
    })
    const submissionSetWizard = wrapper.vm.$root.$children[0]

    // Setup isValid as submissionSetList is a stub
    submissionSetWizard.$refs.submissionSetList.isValid = () => true

    return submissionSetWizard
  }

  test('check simple functions after initialization', async () => {
    const submissionSetWizard = await testPreamble()

    expect(await submissionSetWizard.isValid()).toBe(true)
    expect(await submissionSetWizard.getNotificationHtmlClass()).toBe(
      'badge badge-success'
    )
  })

  test('check onRemoveClick', async () => {
    const submissionSetWizard = await testPreamble()
    global.confirm.mockReturnValueOnce(true)

    await submissionSetWizard.onRemoveClicked()

    await flushPromises()

    expect(actions.wizardRemove).toHaveBeenCalledTimes(1)
    expect(actions.wizardRemove).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      undefined
    )
  })

  test('check onCancelClicked', async () => {
    const submissionSetWizard = await testPreamble()
    global.confirm.mockReturnValueOnce(true)

    await submissionSetWizard.onCancelClicked()

    await flushPromises()

    expect(actions.wizardCancel).toHaveBeenCalledTimes(1)
    expect(actions.wizardCancel).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      undefined
    )
  })

  test('check onSaveClicked', async () => {
    const submissionSetWizard = await testPreamble()

    await submissionSetWizard.onSaveClicked()

    await flushPromises()

    expect(actions.wizardSave).toHaveBeenCalledTimes(1)
    expect(actions.wizardSave).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      undefined
    )
  })

  test('check onGotoSubmissionsClicked', async () => {
    const submissionSetWizard = await testPreamble()

    await submissionSetWizard.onGotoSubmissionsClicked()

    await flushPromises()

    expect(actions.setWizardState).toHaveBeenCalledTimes(1)
    expect(actions.setWizardState).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      WizardState.submissions
    )
  })

  test('check onGotoSubmissionSetClicked', async () => {
    const submissionSetWizard = await testPreamble()

    await submissionSetWizard.onGotoSubmissionSetClicked()

    await flushPromises()

    expect(actions.setWizardState).toHaveBeenCalledTimes(1)
    expect(actions.setWizardState).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      WizardState.submissionSet
    )
  })
})

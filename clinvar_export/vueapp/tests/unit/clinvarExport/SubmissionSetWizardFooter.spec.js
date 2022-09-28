import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vuex from 'vuex'

import SubmissionSetWizardFooter from '@/components/SubmissionSetWizardFooter.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(Vuex)

describe('SubmissionSetWizardFooter.vue', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    const clinvarExport = {
      namespaced: true,
      state: () => ({
        wizardState: undefined,
      }),
    }
    store = new Vuex.Store({
      modules: {
        clinvarExport,
      },
    })
  })

  test('renders correct buttons for wizardState=submissionSet', () => {
    store.state.clinvarExport.wizardState = WizardState.submissionSet
    const wrapper = shallowMount(SubmissionSetWizardFooter, {
      store,
      localVue,
    })

    expect(wrapper.vm.$refs.buttonCancel).toBeDefined()
    expect(wrapper.vm.$refs.buttonSave).toBeDefined()
    expect(wrapper.vm.$refs.buttonVariants).toBeDefined()
    expect(wrapper.vm.$refs.buttonSubmission).toBeUndefined()
  })

  test('renders correct buttons for wizardState=submissions', () => {
    store.state.clinvarExport.wizardState = WizardState.submissions
    const wrapper = shallowMount(SubmissionSetWizardFooter, {
      store,
      localVue,
    })

    expect(wrapper.vm.$refs.buttonCancel).toBeDefined()
    expect(wrapper.vm.$refs.buttonSave).toBeDefined()
    expect(wrapper.vm.$refs.buttonVariants).toBeUndefined()
    expect(wrapper.vm.$refs.buttonSubmission).toBeDefined()
  })

  test('emits correct signals for wizardState=submissionSet', () => {
    store.state.clinvarExport.wizardState = WizardState.submissionSet
    const wrapper = shallowMount(SubmissionSetWizardFooter, {
      store,
      localVue,
    })

    wrapper.vm.$refs.buttonCancel.click()
    expect(wrapper.emitted()['cancel-clicked']).toBeTruthy()
    expect(wrapper.emitted()['cancel-clicked'].length).toBe(1)

    wrapper.vm.$refs.buttonSave.click()
    expect(wrapper.emitted()['save-clicked']).toBeTruthy()
    expect(wrapper.emitted()['save-clicked'].length).toBe(1)

    wrapper.vm.$refs.buttonVariants.click()
    expect(wrapper.emitted()['goto-submissions-clicked']).toBeTruthy()
    expect(wrapper.emitted()['goto-submissions-clicked'].length).toBe(1)
  })

  test('emits correct signals for wizardState=submissions', async () => {
    store.state.clinvarExport.wizardState = WizardState.submissions
    const wrapper = shallowMount(SubmissionSetWizardFooter, {
      store,
      localVue,
    })

    wrapper.vm.$refs.buttonCancel.click()
    expect(wrapper.emitted()['cancel-clicked']).toBeTruthy()
    expect(wrapper.emitted()['cancel-clicked'].length).toBe(1)

    wrapper.vm.$refs.buttonSave.click()
    expect(wrapper.emitted()['save-clicked']).toBeTruthy()
    expect(wrapper.emitted()['save-clicked'].length).toBe(1)

    wrapper.vm.$refs.buttonSubmission.click()
    expect(wrapper.emitted()['goto-submission-set-clicked']).toBeTruthy()
    expect(wrapper.emitted()['goto-submission-set-clicked'].length).toBe(1)
  })
})

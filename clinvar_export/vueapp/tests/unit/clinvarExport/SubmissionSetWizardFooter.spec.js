import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeAll, beforeEach, describe, expect, test, vi } from 'vitest'

import SubmissionSetWizardFooter from '@/components/SubmissionSetWizardFooter.vue'
import { WizardState } from '@/stores/clinvar-export'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  return shallowMount(SubmissionSetWizardFooter, {
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

describe('SubmissionSetWizardFooter.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Mock out global.alert() and global.confirm()
    global.alert = vi.fn()
    global.confirm = vi.fn()
  })

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  test('renders correct buttons for wizardState=submissionSet', () => {
    const wrapper = makeWrapper({ wizardState: WizardState.submissionSet })

    expect(wrapper.vm.$refs.buttonCancel).toBeDefined()
    expect(wrapper.vm.$refs.buttonSave).toBeDefined()
    expect(wrapper.vm.$refs.buttonVariants).toBeDefined()
    expect(wrapper.vm.$refs.buttonSubmission).toBeUndefined()
  })

  test('renders correct buttons for wizardState=submissions', () => {
    const wrapper = makeWrapper({ wizardState: WizardState.submissions })

    expect(wrapper.vm.$refs.buttonCancel).toBeDefined()
    expect(wrapper.vm.$refs.buttonSave).toBeDefined()
    expect(wrapper.vm.$refs.buttonVariants).toBeUndefined()
    expect(wrapper.vm.$refs.buttonSubmission).toBeDefined()
  })

  test('emits correct signals for wizardState=submissionSet', () => {
    const wrapper = makeWrapper({ wizardState: WizardState.submissionSet })

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
    const wrapper = makeWrapper({ wizardState: WizardState.submissions })

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

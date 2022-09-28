import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
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

import SubmissionSetWizard from '@/components/SubmissionSetWizard.vue'
import { useClinvarExportStore, WizardState } from '@/stores/clinvar-export.js'

import { copy } from '../../testUtils.js'
import { clinvarExportEmptyState } from '../fixtures.js'
import { firstSubmissionSet, rawAppContext } from '../fixtures.js'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  return shallowMount(SubmissionSetWizard, {
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

describe('SubmissionSetWizard.vue', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Mock out global.alert() and global.confirm()
    global.alert = vi.fn()
    global.confirm = vi.fn()
  })

  afterAll(() => {
    global.alert.mockRestore()
    global.confirm.mockRestore()
  })

  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // In these tests we consider the simple case of having one submission
  // set only and to initially be in the submission set state
  let submissionSet1
  const setupSimpleCase = () => {
    submissionSet1 = copy(firstSubmissionSet)
  }

  const testPreamble = async (extraClinvarExportState) => {
    extraClinvarExportState = extraClinvarExportState || {}
    setupSimpleCase()

    const wrapper = makeWrapper({
      ...clinvarExportEmptyState,
      appContext: copy(rawAppContext),
      ...extraClinvarExportState,
    })
    wrapper.vm.$refs.submissionSetEditorRef.isValid = vi.fn(() => true)

    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    store.wizardState = WizardState.submissionSet
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
    store.currentSubmissionSet = submissionSet1
    store.wizardRemove = vi.fn()
    store.wizardCancel = vi.fn()
    store.wizardSave = vi.fn()

    return wrapper
  }

  test('check simple functions after initialization', async () => {
    const wrapper = await testPreamble({})

    expect(await wrapper.vm.isValid()).toBe(true)
    expect(await wrapper.vm.getNotificationHtmlClass()).toBe(
      'badge badge-success'
    )
  })

  test('check onRemoveClick', async () => {
    const wrapper = await testPreamble()
    global.confirm.mockReturnValueOnce(true)

    await wrapper.vm.onRemoveClicked()

    await flushPromises()

    expect(store.wizardRemove).toHaveBeenCalledTimes(1)
    expect(store.wizardRemove).toHaveBeenNthCalledWith(1)
  })

  test('check onCancelClicked', async () => {
    const wrapper = await testPreamble()
    global.confirm.mockReturnValueOnce(true)

    await wrapper.vm.onCancelClicked()

    await flushPromises()

    expect(store.wizardCancel).toHaveBeenCalledTimes(1)
    expect(store.wizardCancel).toHaveBeenNthCalledWith(1)
  })

  test('check onSaveClicked', async () => {
    const wrapper = await testPreamble()

    await wrapper.vm.onSaveClicked()

    await flushPromises()

    expect(store.wizardSave).toHaveBeenCalledTimes(1)
    expect(store.wizardSave).toHaveBeenNthCalledWith(1)
  })

  test('check onGotoSubmissionsClicked', async () => {
    const wrapper = await testPreamble()

    await wrapper.vm.onGotoSubmissionsClicked()

    await flushPromises()

    expect(store.wizardState).toBe(WizardState.submissions)
  })

  test('check onGotoSubmissionSetClicked', async () => {
    const wrapper = await testPreamble()

    await wrapper.vm.onGotoSubmissionSetClicked()

    await flushPromises()

    expect(store.wizardState).toBe(WizardState.submissionSet)
  })
})

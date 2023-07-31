import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import SubmissionSetList from '@clinvarexport/components/SubmissionSetList.vue'
import {
  useClinvarExportStore,
  WizardState,
} from '@clinvarexport/stores/clinvar-export.js'
import { createTestingPinia } from '@pinia/testing'
import { shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import { Response } from 'node-fetch'
import {
  afterAll,
  afterEach,
  beforeAll,
  describe,
  expect,
  test,
  vi,
} from 'vitest'
import { nextTick } from 'vue'

import { copy, waitNT } from '../../testUtils.js'
import { firstSubmissionSet } from '../fixtures.js'

// Helper function for creating wrapper with `shallowMount()`.
const makeWrapper = (clinvarExportState) => {
  if (!clinvarExportState) {
    clinvarExportState = {}
  }
  return shallowMount(SubmissionSetList, {
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

describe('SubmissionSetList.vue', () => {
  let store

  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
    // Set reproducible time
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2020, 3, 1))
    // Mock out jquery dollar function for showing modals
    global.$ = vi.fn()
  })

  afterAll(() => {
    vi.useRealTimers()
    global.$.mockRestore()
  })

  afterEach(() => {
    vi.clearAllMocks()
    vi.clearAllTimers()
  })

  // In these tests we consider the simple case of having one submission
  // set only and to initially be in the submission set state
  let submissionSet1
  const setupSimpleCase = () => {
    submissionSet1 = copy(firstSubmissionSet)
    store.wizardState = WizardState.submissionSet
    store.submissionSets[submissionSet1.sodar_uuid] = submissionSet1
    store.submissionSetList = [submissionSet1]
  }

  const getButtons = (wrapper, rowNo) => {
    const colNo = 1
    const buttonCell =
      wrapper.findAll('tbody tr')[rowNo].wrapperElement.childNodes[colNo]
    const buttonGroup = buttonCell.children[0]
    return {
      editButton: buttonGroup.children[0],
      clinvarButton: buttonGroup.children[1],
    }
  }

  test('key elements are present', async () => {
    const wrapper = makeWrapper()
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    setupSimpleCase() // NB: this call must be after assigning store
    await nextTick() // wait for changes to store to take effect

    store.createNewSubmissionSet = vi.fn()
    store.editSubmissionSet = vi.fn()

    // Footer button to create new submission list
    expect(wrapper.vm.$refs.buttonCreateNew).toBeDefined()

    // Submission set table with entries and buttons
    const { editButton, clinvarButton } = getButtons(wrapper, 0)
    expect(editButton.textContent.trim()).toEqual('Edit')
    expect(clinvarButton.textContent.trim()).toEqual('ClinVar XML')
  })

  // Helper that sets up the test for showing ClinVar XML modal and then
  // shows it by clicking it.  This has been extracted so we can re-use
  // it for the cancel and download XML button tests
  const testClinvarXmlClick = async () => {
    clinvarExportApi.getSubmissionSetXml.mockResolvedValueOnce(
      new Response('<fake-xml/>', { status: 200 })
    )
    clinvarExportApi.getSubmissionSetValid.mockResolvedValueOnce(
      new Response(JSON.stringify({ valid: true, details: [] }), {
        status: 200,
      })
    )

    const wrapper = makeWrapper()
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    setupSimpleCase() // NB: this call must be after assigning store
    await nextTick() // wait for changes to store to take effect

    const { clinvarButton } = getButtons(wrapper, 0)

    store.createNewSubmissionSet = vi.fn()
    store.editSubmissionSet = vi.fn()
    global.$.mockReturnValue({
      modal: vi.fn((action) => {
        const classes = wrapper.vm.$refs.modalXmlPreview.classList
        if (action === 'show') {
          if (!classes.contains('show')) {
            classes.remove('fade')
            classes.add('show')
          }
        } else if (action === 'hide') {
          if (!classes.contains('fade')) {
            classes.add('fade')
            classes.remove('show')
          }
        }
      }),
    })

    expect(wrapper.vm.$refs.modalXmlPreview).toBeDefined()
    expect(
      Object.values(wrapper.vm.$refs.modalXmlPreview.classList)
    ).not.toContainEqual('show')
    clinvarButton.click()
    expect(wrapper.vm.$data.submissionSetUuid).toEqual(
      submissionSet1.sodar_uuid
    )
    expect(
      Object.values(wrapper.vm.$refs.modalXmlPreview.classList)
    ).toContainEqual('show')
    expect(wrapper.vm.$refs.buttonClose).toBeDefined()
    expect(wrapper.vm.$refs.buttonDownloadXml).toBeDefined()

    await flushPromises()

    expect(clinvarExportApi.getSubmissionSetXml.mock.calls.length).toBe(1)
    expect(clinvarExportApi.getSubmissionSetXml.mock.calls[0]).toEqual([
      store.appContext,
      submissionSet1.sodar_uuid,
    ])
    expect(clinvarExportApi.getSubmissionSetValid.mock.calls.length).toBe(1)
    expect(clinvarExportApi.getSubmissionSetValid.mock.calls[0]).toEqual([
      store.appContext,
      submissionSet1.sodar_uuid,
    ])

    expect(global.$).toHaveBeenCalledTimes(1)
    expect(global.$).toHaveBeenNthCalledWith(
      1,
      wrapper.vm.$refs.modalXmlPreview
    )

    return wrapper
  }

  test('clinvar xml preview click works', async () => {
    await testClinvarXmlClick()
  })

  test('clinvar xml preview click works with download', async () => {
    const wrapper = await testClinvarXmlClick()

    const makeAnchor = (target) => {
      return {
        target,
        setAttribute: vi.fn((key, value) => (target[key] = value)),
        click: vi.fn(),
        remove: vi.fn(),
      }
    }

    const anchor = makeAnchor({ href: '#', download: '' })
    const createElementMock = vi
      .spyOn(document, 'createElement')
      .mockReturnValue(anchor)
    const setAttributeSpy = vi.spyOn(anchor, 'setAttribute')
    const clickSpy = vi.spyOn(anchor, 'click')
    const removeSpy = vi.spyOn(anchor, 'remove')

    vi.clearAllMocks() // start with clean mocks/spies before call is made

    URL.createObjectURL = vi.fn()
    URL.createObjectURL.mockReturnValueOnce('fake://result')

    wrapper.vm.$refs.buttonDownloadXml.click()
    await waitNT(wrapper.vm)

    expect(document.createElement).toHaveBeenCalledTimes(1)
    expect(document.createElement).toHaveBeenCalledWith('a')
    expect(setAttributeSpy).toHaveBeenCalledTimes(2)
    expect(setAttributeSpy).toHaveBeenNthCalledWith(1, 'href', 'fake://result')
    expect(setAttributeSpy).toHaveBeenNthCalledWith(
      2,
      'download',
      `clinvar-${submissionSet1.sodar_uuid}.xml`
    )

    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(removeSpy).toHaveBeenCalledTimes(1)

    URL.createObjectURL.mockRestore()
    createElementMock.mockRestore()
  })

  test('clinvar xml preview click works with close', async () => {
    const wrapper = await testClinvarXmlClick()

    wrapper.vm.$refs.buttonClose.click()
    expect(
      Object.values(wrapper.vm.$refs.modalXmlPreview.classList)
    ).not.toContainEqual('show')

    expect(global.$).toHaveBeenCalledTimes(2)
    expect(global.$).toHaveBeenNthCalledWith(
      2,
      wrapper.vm.$refs.modalXmlPreview
    )
  })

  test('edit submission set button click works', async () => {
    const wrapper = makeWrapper()
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    setupSimpleCase() // NB: this call must be after assigning store
    await nextTick() // wait for changes to store to take effect

    store.createNewSubmissionSet = vi.fn()
    store.editSubmissionSet = vi.fn()

    const { editButton } = getButtons(wrapper, 0)

    editButton.click()

    expect(store.editSubmissionSet).toHaveBeenCalledTimes(1)
    expect(store.editSubmissionSet).toHaveBeenNthCalledWith(
      1,
      submissionSet1.sodar_uuid
    )
  })

  test('create new submission set works', async () => {
    const wrapper = makeWrapper()
    store = useClinvarExportStore() // NB: this call must be **after** creating wrapper
    setupSimpleCase() // NB: this call must be after assigning store
    await nextTick() // wait for changes to store to take effect

    store.createNewSubmissionSet = vi.fn()
    store.editSubmissionSet = vi.fn()

    wrapper.vm.$refs.buttonCreateNew.click()

    expect(store.createNewSubmissionSet).toHaveBeenCalledTimes(1)
  })
})

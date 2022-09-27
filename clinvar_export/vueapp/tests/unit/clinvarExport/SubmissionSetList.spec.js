import { createLocalVue, mount } from '@vue/test-utils'
import BootstrapVue from 'bootstrap-vue'
import flushPromises from 'flush-promises'
import { Response } from 'node-fetch'
import Vue from 'vue'
import Vuex from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import SubmissionSetList from '@/components/SubmissionSetList.vue'
import { WizardState } from '@/store/modules/clinvarExport.js'

import { copy, waitNT } from '../../testUtils.js'
import {
  clinvarExportEmptyState,
  firstSubmissionSet,
  rawAppContext,
} from '../fixtures.js'

// Set up extended Vue constructor
const localVue = createLocalVue()
localVue.use(BootstrapVue)
localVue.use(Vuex)

// Mock out the clinvarExport API
jest.mock('@/api/clinvarExport')

describe('SubmissionSetList.vue', () => {
  let store
  let actions

  beforeAll(() => {
    // Disable warnings
    jest.spyOn(console, 'warn').mockImplementation(jest.fn())
    // Set reproducible time
    jest.useFakeTimers('modern')
    jest.setSystemTime(new Date(2020, 3, 1))
  })

  afterAll(() => {
    jest.useRealTimers()
  })

  beforeEach(() => {
    // Setup relevant store/state fragment
    actions = {
      createNewSubmissionSet: jest.fn(),
      editSubmissionSet: jest.fn(),
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

  afterEach(() => {
    Object.keys(clinvarExportApi).forEach((method) =>
      clinvarExportApi[method].mockClear()
    )
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
  }

  const getButtons = (wrapper, rowNo) => {
    const colNo = 1
    const buttonCell =
      wrapper.vm.$refs.submissionSetTable.$refs['item-rows'][rowNo].$el.cells[
        colNo
      ]
    const buttonGroup = buttonCell.children[0]
    return {
      editButton: buttonGroup.children[0],
      clinvarButton: buttonGroup.children[1],
    }
  }

  test('key elements are present', async () => {
    setupSimpleCase()

    const wrapper = mount(SubmissionSetList, {
      store,
      localVue,
    })

    // Footer button to create new submission list
    expect(wrapper.vm.$refs.buttonCreateNew).toBeDefined()

    // Submission set table with entries and buttons
    expect(wrapper.vm.$refs.submissionSetTable.$refs['item-rows'].length).toBe(
      1
    )
    const { editButton, clinvarButton } = getButtons(wrapper, 0)
    expect(editButton.textContent.trim()).toEqual('Edit')
    expect(clinvarButton.textContent.trim()).toEqual('ClinVar XML')
  })

  // Helper that sets up the test for showing ClinVar XML modal and then
  // shows it by clicking it.  This has been extracted so we can re-use
  // it for the cancel and download XML button tests
  const testClinvarXmlClick = async () => {
    setupSimpleCase()

    clinvarExportApi.getSubmissionSetXml.mockResolvedValueOnce(
      new Response('<fake-xml/>', { status: 200 })
    )
    clinvarExportApi.getSubmissionSetValid.mockResolvedValueOnce(
      new Response(JSON.stringify({ valid: true, details: [] }), {
        status: 200,
      })
    )

    const wrapper = mount(SubmissionSetList, {
      store,
      localVue,
    })
    const { clinvarButton } = getButtons(wrapper, 0)
    expect(wrapper.vm.$refs.modalXmlPreview).toBeDefined()
    expect(wrapper.vm.$refs.modalXmlPreview.isVisible).toBe(false)
    clinvarButton.click()
    expect(wrapper.vm.$data.submissionSetUuid).toEqual(
      submissionSet1.sodar_uuid
    )
    await waitNT(wrapper.vm)
    expect(wrapper.vm.$refs.modalXmlPreview.isVisible).toBe(true)
    expect(wrapper.vm.$refs.buttonClose).toBeDefined()
    expect(wrapper.vm.$refs.buttonDownloadXml).toBeDefined()

    await flushPromises()

    expect(clinvarExportApi.getSubmissionSetXml.mock.calls.length).toBe(1)
    expect(clinvarExportApi.getSubmissionSetXml.mock.calls[0]).toEqual([
      store.state.clinvarExport.appContext,
      submissionSet1.sodar_uuid,
    ])
    expect(clinvarExportApi.getSubmissionSetValid.mock.calls.length).toBe(1)
    expect(clinvarExportApi.getSubmissionSetValid.mock.calls[0]).toEqual([
      store.state.clinvarExport.appContext,
      submissionSet1.sodar_uuid,
    ])

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
        setAttribute: jest.fn((key, value) => (target[key] = value)),
        click: jest.fn(),
        remove: jest.fn(),
      }
    }

    const anchor = makeAnchor({ href: '#', download: '' })
    const createElementMock = jest
      .spyOn(document, 'createElement')
      .mockReturnValue(anchor)
    const setAttributeSpy = jest.spyOn(anchor, 'setAttribute')
    const clickSpy = jest.spyOn(anchor, 'click')
    const removeSpy = jest.spyOn(anchor, 'remove')

    jest.clearAllMocks() // start with clean mocks/spies before call is made

    URL.createObjectURL = jest.fn()
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
    expect(wrapper.vm.$refs.modalXmlPreview.isVisible).toBe(false)
  })

  test('edit submission set button click works', () => {
    setupSimpleCase()

    const wrapper = mount(SubmissionSetList, {
      store,
      localVue,
    })
    const { editButton } = getButtons(wrapper, 0)

    editButton.click()

    expect(actions.editSubmissionSet).toHaveBeenCalledTimes(1)
    expect(actions.editSubmissionSet).toHaveBeenNthCalledWith(
      1,
      expect.anything(),
      submissionSet1.sodar_uuid
    )
  })

  test('create new submission set works', () => {
    setupSimpleCase()

    const wrapper = mount(SubmissionSetList, {
      store,
      localVue,
    })

    wrapper.vm.$refs.buttonCreateNew.click()

    expect(actions.createNewSubmissionSet).toHaveBeenCalledTimes(1)
  })
})

// Miscellaneous testing utilities
// import ClinvarExportApp from '@/components/ClinvarExportApp'
// import SubmissionCaseList from '@/components/SubmissionCaseList'
// import SubmissionCaseListEntry from '@/components/SubmissionCaseListEntry'
// import SubmissionEditor from '@/components/SubmissionEditor'
// import SubmissionList from '@/components/SubmissionList'
// import SubmissionSetEditor from '@/components/SubmissionSetEditor'
// import SubmissionSetList from '@/components/SubmissionSetList'
// import SubmissionSetWizard from '@/components/SubmissionSetWizard'
import rawAppContext from './unit/data/rawAppContext.json'
// import SubmissionSetWizardFooter from '@/components/SubmissionSetWizardFooter'

// Constants
export const projectUuid = '00000000-0000-0000-0000-000000000000'
export const submissionSetUuid = '11111111-1111-1111-1111-111111111111'
export const submitterUuid = '22222222-2222-2222-2222-222222222222'
export const organisationUuid = '33333333-3333-3333-3333-333333333333'
export const submittingOrgUuid = '44444444-4444-4444-4444-444444444444'
export const assertionMethodUuid = '55555555-5555-5555-5555-555555555555'
export const submissionUuid = '66666666-6666-6666-6666-666666666666'
export const familyUuid = '77777777-7777-7777-7777-777777777777'
export const individualUuid = '88888888-8888-8888-8888-888888888888'
export const submissionIndividualUuid = '99999999-9999-9999-9999-999999999999'
export const caseUuid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
export const userUuid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'

// App.vue stub to be provided as prop for callbacks and general data access
// TODO: Update to get full params
export function getAppStub(params = {}) {
  if (!params.rawAppContext) params.rawAppContext = copy(rawAppContext)
  return {
    template: '<div />',
    editContext: params.editContext || null,
    editMode: params.editMode || false,
    projectUuid,
    sodarContext: params.sodarContext,
    unsavedRow: params.unsavedRow || null,
    handleRowInsert: () => {},
    getGridOptionsByUuid: () => {},
    setDataUpdated: () => {},
    showNotification: () => {},
    $refs: params.$refs || {
      columnConfigModal: null,
      columnToggleModalRef: null,
      dirModalRef: null,
      ontologyEditModal: null,
    },
  }
}

// // Return app components for sheet table
// export function getSheetTableComponents () {
//   return {
//     DataCellRenderer,
//     HeaderEditRenderer,
//     StudyShortcutsRenderer,
//     IrodsButtonsRenderer,
//     RowEditRenderer,
//     DataCellEditor,
//     ObjectSelectEditor,
//     OntologyEditor
//   }
// }
//
// // Return params for buildColDef()
// export function getColDefParams (params = {}) {
//   const ret = Object.assign({
//     app: params.app || getAppStub(),
//     assayMode: false,
//     currentStudyUuid: studyUuid,
//     editContext: null,
//     editMode: false,
//     editStudyConfig: null,
//     gridUuid: null,
//     sampleColId: 'col7',
//     sampleIdx: 8,
//     sodarContext: null,
//     studyDisplayConfig: null,
//     studyNodeLen: 2,
//     table: null
//   }, params)
//
//   // Default grid UUID
//   // TODO: Use setGridUuid()
//   if (!ret.gridUuid) {
//     if (!ret.assayMode) ret.gridUuid = studyUuid
//     else ret.gridUuid = assayUuid
//   }
//
//   // Default configurations and table
//   if (!ret.editStudyConfig || !ret.studyDisplayConfig || !ret.table) {
//     let tableResp
//     if (ret.editMode) tableResp = copy(studyTablesEdit)
//     else tableResp = copy(studyTables)
//
//     if (!ret.editStudyConfig) ret.editStudyConfig = tableResp.study_config
//     if (!ret.studyDisplayConfig) ret.studyDisplayConfig = tableResp.display_config
//     if (!ret.table) {
//       if (!ret.assayMode) ret.table = tableResp.tables.study
//       else ret.table = tableResp.tables.assays[ret.gridUuid]
//     }
//   }
//
//   // Default SODAR context
//   if (!ret.sodarContext) ret.sodarContext = copy(sodarContext)
//
//   return ret
// }
//
// // Return params for buildRowData()
// export function getRowDataParams (params = {}) {
//   const ret = Object.assign({
//     assayMode: false,
//     editMode: false,
//     sodarContext: null,
//     table: null
//   }, params)
//
//   // Default table
//   if (!ret.table) {
//     let tableResp
//     if (ret.editMode) tableResp = copy(studyTablesEdit)
//     else tableResp = copy(studyTables)
//     if (!ret.assayMode) ret.table = tableResp.tables.study
//     else ret.table = tableResp.tables.assays[assayUuid]
//   }
//
//   // Default SODAR context
//   if (!ret.sodarContext) ret.sodarContext = copy(sodarContext)
//
//   return ret
// }
//
// export function getSheetTablePropsData (params = {}) {
//   if (!params.app) {
//     params.app = getAppStub({ editMode: params.editMode || false })
//   }
//   if (!params.gridUuid) {
//     if (!params.assayMode) params.gridUuid = studyUuid
//     else params.gridUuid = assayUuid
//   }
//   const ret = Object.assign({
//     app: params.app,
//     assayMode: false,
//     columnDefs: buildColDef(getColDefParams(params)),
//     editMode: params.editMode || false,
//     gridOptions: null,
//     gridUuid: params.gridUuid,
//     rowData: buildRowData(getRowDataParams(params))
//   }, params)
//   ret.gridOptions = params.gridOptions || initGridOptions(ret.app, ret.editMode)
//   return ret
// }
//
// // Set default gridUuid if not overridden in params
// export function setGridUuid (params) {
//   if (!params.gridUuid) {
//     if (!params.assayMode) params.gridUuid = studyUuid
//     else params.gridUuid = assayUuid
//   }
//   return params
// }
//
// // Wait for ag-grid to be ready
// // Adapted from: https://www.ag-grid.com/javascript-grid-testing-vue/
// // TODO: Handle reject
// // TODO: Improve
// export const waitAG = wrapper => new Promise(function (resolve, reject) {(
//   function waitForGridReady () {
//     if (wrapper.find('.ag-row')) return resolve()
//     setTimeout(waitForGridReady, 10)
//   })()
// })
//
// // Wait for at least n elements to be present by selector
// export const waitSelector = (wrapper, selector, count) =>
//   new Promise(function (resolve, reject) {(
//     function waitForSelectorCount () {
//       if (count === undefined) count = 1
//       if ((count > 0 && wrapper.findAll(selector).length >= count) ||
//           (count === 0 && wrapper.findAll(selector).length === count)) {
//         return resolve()
//       }
//       setTimeout(waitForSelectorCount, 10)
//     })()
//   })
//
// // Bootstrap-vue modal helpers
// // From: https://github.com/bootstrap-vue/bootstrap-vue/blob/dev/tests/utils.js
// export const createContainer = (tag = 'div') => {
//   const container = document.createElement(tag)
//   document.body.appendChild(container)
//   return container
// }
export const waitNT = (vm) => new Promise((resolve) => vm.$nextTick(resolve))
export const waitRAF = () =>
  new Promise((resolve) => requestAnimationFrame(resolve))

// Basic copy function for data objects
export function copy(obj) {
  return JSON.parse(JSON.stringify(obj))
}

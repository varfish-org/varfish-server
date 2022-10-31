import { apiFetch } from '@varfish/api-utils.js'

export default {
  async listCase(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case/list/${projectUuid}/`
    )
    return await response.json()
  },

  async updateCase(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case/update/${caseUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },

  async loadProjectQcValues(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/${projectUuid}/api-qc/`
    )
    return await response.json()
  },

  async fetchVarAnnos(_csrfToken, _projectUuid) {
    return Promise.resolve([])
  },

  async fetchVarComments(_csrfToken, _projectUuid) {
    return Promise.resolve([])
  },

  async fetchVarAcmgRatings(_csrfToken, _projectUuid) {
    return Promise.resolve([])
  },

  async fetchSvAnnos(_csrfToken, _projectUuid) {
    return Promise.resolve([])
  },

  async fetchSvComments(_csrfToken, _projectUuid) {
    return Promise.resolve([])
  },

  async fetchCaseComments(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/list/${caseUuid}/`
    )
    return await response.json()
  },

  async fetchCaseGeneAnnotation(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/case-gene-annotation/list/${caseUuid}/`
    )
    return await response.json()
  },

  async fetchPermissions(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/user-permissions/${projectUuid}`
    )
    return await response.json()
  },
}

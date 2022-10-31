import { apiFetch } from '@varfish/api-utils.js'

export default {
  async fetchQuickPresets(csrfToken) {
    const response = await apiFetch(
      csrfToken,
      '/variants/api/query-case/quick-presets/',
      'GET'
    )
    return await response.json()
  },
  async fetchInheritancePresets(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/api/query-case/inheritance-presets/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async fetchCategoryPresets(csrfToken, category) {
    const response = await apiFetch(
      csrfToken,
      `/variants/api/query-case/category-presets/${category}/`,
      'GET'
    )
    return await response.json()
  },
  async fetchQueryShortcuts(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/query-settings-shortcut/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async fetchCaseQueries(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/list/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveCase(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/case/retrieve/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveQueryDetails(csrfToken, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/retrieve/${queryUuid}`,
      'GET'
    )
    return await response.json()
  },
  async getQueryStatus(csrfToken, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/status/${queryUuid}`
    )
    return await response.json()
  },
  async submitQuery(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/create/${caseUuid}/`,
      'POST',
      payload
    )
    return await response.json()
  },
  async fetchResults(csrfToken, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/results-extended/${queryUuid}/`,
      'GET'
    )
    return await response.json()
  },
}

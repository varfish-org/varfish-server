import { apiFetch } from '@varfish/api-utils.js'

export default {
  async fetchQuickPresets(csrfToken) {
    const response = await apiFetch(
      csrfToken,
      '/svs/ajax/query-case/quick-presets/',
      'GET'
    )
    return await response.json()
  },
  async fetchInheritancePresets(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/query-case/inheritance-presets/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async fetchCategoryPresets(csrfToken, category) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/query-case/category-presets/${category}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveQuerySettingsShortcut(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/query-case/query-settings-shortcut/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listSvQuery(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/sv-query/list-create/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async createSvQuery(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/sv-query/list-create/${caseUuid}/`,
      'POST',
      payload
    )
    return await response.json()
  },
  async retrieveSvQuery(csrfToken, svQueryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/sv-query/retrieve-update-destroy/${svQueryUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listSvQueryResultSet(csrfToken, svQueryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/sv-query-result-set/list/${svQueryUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveSvQueryResultSet(csrfToken, svQueryResultUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/sv-query-result-set/retrieve/${svQueryResultUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listSvQueryResultRow(csrfToken, svQueryResultSetUuid, options = {}) {
    const pageNo = options.pageNo ?? 1
    const pageSize = options.pageSize ?? 50
    const orderByRaw = options.orderBy ?? 'chromosome_no,start'
    const orderBy = ['start', 'end'].includes(orderByRaw)
      ? `chromosome_no,${orderByRaw}`
      : orderByRaw
    const orderDir = options.orderDir ?? 'asc'

    const urlQuery = `?page=${pageNo}&page_size=${pageSize}&order_by=${orderBy}&order_dir=${orderDir}`
    const response = await apiFetch(
      csrfToken,
      `/svs/sv-query-result-row/list/${svQueryResultSetUuid}/${urlQuery}`,
      'GET'
    )
    return await response.json()
  },
  async listComment(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, sv_type, sv_sub_type }
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-comment/list-create/${caseUuid}/?${query}`,
      'GET'
    )
    return await response.json()
  },
  async createComment(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, sv_type, sv_sub_type },
    payload
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-comment/list-create/${caseUuid}/?${query}`,
      'POST',
      payload
    )
    return await response.json()
  },
  async updateComment(csrfToken, commentUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-comment/retrieve-update-destroy/${commentUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },
  async deleteComment(csrfToken, commentUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-comment/retrieve-update-destroy/${commentUuid}/`,
      'DELETE'
    )
    await response
  },
  async listFlags(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, sv_type, sv_sub_type }
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-flags/list-create/${caseUuid}/?${query}`,
      'GET'
    )
    return await response.json()
  },
  async createFlags(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, sv_type, sv_sub_type },
    payload
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&sv_type=${sv_type}&sv_sub_type=${sv_sub_type}`
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-flags/list-create/${caseUuid}/?${query}`,
      'POST',
      payload
    )
    return await response.json()
  },
  async updateFlags(csrfToken, flagsUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-flags/retrieve-update-destroy/${flagsUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },
  async deleteFlags(csrfToken, flagsUuid) {
    const response = await apiFetch(
      csrfToken,
      `/svs/ajax/structural-variant-flags/retrieve-update-destroy/${flagsUuid}/`,
      'DELETE'
    )
    await response
  },
}

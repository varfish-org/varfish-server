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
  async createQuery(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query/list-create/${caseUuid}/`,
      'POST',
      payload
    )
    return await response.json()
  },
  async retrieveQuery(csrfToken, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query/retrieve-update-destroy/${queryUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listQueryResultSet(csrfToken, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-result-set/list/${queryUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveQueryResultSet(csrfToken, queryResultUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-result-set/retrieve/${queryResultUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listQueryResultRow(csrfToken, queryResultSetUuid, options = {}) {
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
      `/variants/ajax/query-result-row/list/${queryResultSetUuid}/${urlQuery}`,
      'GET'
    )
    return await response.json()
  },
  async retrieveQueryResultRow(csrfToken, queryResultRowUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-result-row/retrieve/${queryResultRowUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async listCaseVariantsUserAnnotated(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/smallvariant/user-annotated-case/${caseUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async retrieveVariantDetails(
    csrfToken,
    database,
    {
      case_uuid,
      release,
      chromosome,
      start,
      end,
      reference,
      alternative,
      gene_id,
    }
  ) {
    const varDesc = `${release}-${chromosome}-${start}-${end}-${reference}-${alternative}`
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-details/${case_uuid}/${varDesc}/${database}/${gene_id}/`,
      'GET'
    )
    return await response.json()
  },
  async listComment(csrfToken, caseUuid, variant = null) {
    let query = ''
    if (variant) {
      const { release, chromosome, start, end, reference, alternative } =
        variant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/${query}`,
      'GET'
    )
    return await response.json()
  },
  async createComment(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, reference, alternative },
    payload
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-comment/list-create/${caseUuid}/?${query}`,
      'POST',
      payload
    )
    return await response.json()
  },
  async updateComment(csrfToken, commentUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-comment/update/${commentUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },
  async deleteComment(csrfToken, commentUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-comment/delete/${commentUuid}/`,
      'DELETE'
    )
    await response
  },
  async listFlags(csrfToken, caseUuid, variant = null) {
    let query = ''
    if (variant) {
      const { release, chromosome, start, end, reference, alternative } =
        variant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }

    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/${query}`,
      'GET'
    )
    return await response.json()
  },
  async createFlags(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, reference, alternative },
    payload
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-flags/list-create/${caseUuid}/?${query}`,
      'POST',
      payload
    )
    return await response.json()
  },
  async updateFlags(csrfToken, flagsUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-flags/update/${flagsUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },
  async deleteFlags(csrfToken, flagsUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/small-variant-flags/delete/${flagsUuid}/`,
      'DELETE'
    )
    await response
  },
  async listAcmgRating(csrfToken, caseUuid, variant = null) {
    let query = ''
    if (variant) {
      const { release, chromosome, start, end, reference, alternative } =
        variant
      query =
        `?release=${release}&chromosome=${chromosome}&start=${start}` +
        `&end=${end}&reference=${reference}&alternative=${alternative}`
    }

    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/${query}`,
      'GET'
    )
    return await response.json()
  },
  async createAcmgRating(
    csrfToken,
    caseUuid,
    { release, chromosome, start, end, reference, alternative },
    payload
  ) {
    const query =
      `release=${release}&chromosome=${chromosome}&start=${start}` +
      `&end=${end}&reference=${reference}&alternative=${alternative}`
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/acmg-criteria-rating/list-create/${caseUuid}/?${query}`,
      'POST',
      payload
    )
    return await response.json()
  },
  async updateAcmgRating(csrfToken, acmgRatingUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/acmg-criteria-rating/update/${acmgRatingUuid}/`,
      'PATCH',
      payload
    )
    return await response.json()
  },
  async deleteAcmgRating(csrfToken, acmgRatingUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/acmg-criteria-rating/delete/${acmgRatingUuid}/`,
      'DELETE'
    )
    await response
  },
  async generateDownloadResults(csrfToken, fileType, queryUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/download/generate/${fileType}/${queryUuid}`, // no trailing slash!!!
      'GET'
    )
    return await response.json()
  },
  async statusDownloadResults(csrfToken, jobUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/query-case/download/status/${jobUuid}/`,
      'GET'
    )
    return await response.json()
  },
  async fetchExtraAnnoFields(csrfToken) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/extra-anno-fields/`,
      'GET'
    )
    return await response.json()
  },
  async fetchHpoTerms(csrfToken, query) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/hpo-terms/?query=${query}`,
      'GET'
    )
    return await response.json()
  },
}

import { apiFetch } from '@varfish/api-utils.js'

export default {
  async listCase(
    csrfToken,
    projectUuid,
    { pageNo, pageSize, orderBy, orderDir, queryString },
  ) {
    let queryArr = []
    if (pageNo !== undefined) {
      queryArr.push(`page=${pageNo + 1}`)
    }
    if (pageSize !== undefined) {
      queryArr.push(`page_size=${pageSize}`)
    }
    if (orderBy !== undefined && orderBy !== null) {
      queryArr.push(`order_by=${orderBy}`)
    }
    if (orderDir !== undefined && orderDir !== null) {
      queryArr.push(`order_dir=${orderDir}`)
    }
    if (
      queryString !== undefined &&
      queryString !== null &&
      queryString.length > 0
    ) {
      queryArr.push(`q=${queryString}`)
    }
    const queryStr = queryArr.length ? '?' + queryArr.join('&') : ''
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case/list/${projectUuid}/${queryStr}`,
    )
    return await response.json()
  },

  async retrieveCase(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case/retrieve-update/${caseUuid}/`,
      'GET',
      payload,
    )
    return await response.json()
  },

  async updateCase(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case/retrieve-update/${caseUuid}/`,
      'PATCH',
      payload,
    )
    return await response.json()
  },

  async loadProjectQcValues(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/project/qc/${projectUuid}/`,
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

  async listCaseComment(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async createCaseComment(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
    return await response.json()
  },

  async retrieveCaseComment(csrfToken, caseCommentUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async updateCaseComment(csrfToken, caseCommentUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'PATCH',
      payload,
    )
    return await response.json()
  },

  async destroyCaseComment(csrfToken, caseCommentUuid) {
    await apiFetch(
      csrfToken,
      `/cases/ajax/case-comment/retrieve-update-destroy/${caseCommentUuid}/`,
      'DELETE',
    )
  },

  async listCasePhenotypeTerms(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async createCasePhenotypeTerms(csrfToken, caseUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-phenotype-terms/list-create/${caseUuid}/`,
      'POST',
      payload,
    )
    return await response.json()
  },

  async retrieveCasePhenotypeTerms(csrfToken, casePhenotypeTermsUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async updateCasePhenotypeTerms(csrfToken, casePhenotypeTermsUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'PATCH',
      payload,
    )
    return await response.json()
  },

  async destroyCasePhenotypeTerms(csrfToken, casePhenotypeTermsUuid) {
    await apiFetch(
      csrfToken,
      `/cases/ajax/case-phenotype-terms/retrieve-update-destroy/${casePhenotypeTermsUuid}/`,
      'DELETE',
    )
  },

  async fetchAnnotationReleaseInfos(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/annotation-release-info/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchSvAnnotationReleaseInfos(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/sv-annotation-release-info/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchCaseGeneAnnotation(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/case-gene-annotation/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchCaseAlignmentStats(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/case-alignment-stats/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchCaseVariantStats(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/case-variant-stats/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchCaseRelatedness(csrfToken, caseUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/api/case-relatedness/list/${caseUuid}/`,
    )
    return await response.json()
  },

  async fetchPermissions(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cases/ajax/user-permissions/${projectUuid}/`,
    )
    return await response.json()
  },
}

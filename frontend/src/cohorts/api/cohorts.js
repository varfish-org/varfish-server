import { apiFetch } from '@/varfish/apiUtils'

export default {
  async listCohort(
    csrfToken,
    projectUuid,
    { pageNo, pageSize, orderBy, orderDir, queryString },
  ) {
    const queryArr = []
    if (pageNo !== undefined) {
      queryArr.push(`page=${pageNo}`)
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
      `/cohorts/ajax/cohort/list-create/${projectUuid}/${queryStr}`,
    )
    return await response.json()
  },

  async createCohort(csrfToken, projectUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohort/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
    return await response.json()
  },

  async listAccessibleProjectsCases(projectUuid) {
    const response = await apiFetch(
      null,
      `/cohorts/ajax/accessible-projects-cases/list/${projectUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async updateCohort(csrfToken, cohortUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohort/retrieve-update-destroy/${cohortUuid}/`,
      'PUT',
      payload,
    )
    return await response.json()
  },

  async destroyCohort(csrfToken, cohortUuid) {
    await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohort/retrieve-update-destroy/${cohortUuid}/`,
      'DELETE',
    )
  },

  async createCohortCase(csrfToken, projectUuid, payload) {
    const response = await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohortcase/create/${projectUuid}/`,
      'POST',
      payload,
    )
    return await response.json()
  },

  async listCohortCase(csrfToken, cohortUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohortcase/list/${cohortUuid}/`,
      'GET',
    )
    return await response.json()
  },

  async destroyCohortCase(csrfToken, cohortCaseUuid) {
    await apiFetch(
      csrfToken,
      `/cohorts/ajax/cohortcase/destroy/${cohortCaseUuid}/`,
      'DELETE',
    )
  },

  async fetchPermissions(csrfToken, projectUuid) {
    const response = await apiFetch(
      csrfToken,
      `/cohorts/ajax/user-permissions/${projectUuid}/`,
    )
    return await response.json()
  },
}

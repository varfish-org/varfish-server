/**
 * Execute request to AJAX API.
 *
 * @param baseUrl Base URL from appContext
 * @param csrfToken CSRF context from appContext
 * @param entity Name of entity, e.g., 'submittingorg'
 * @param uuid (Optional) UUID of record to manipulate.
 * @param method (Optional) HTTP method to use, defaults to 'GET'
 * @param payload (Optional) payload to use
 * @returns {Promise<Response>}
 */
async function apiFetch(
  { baseUrl, csrfToken },
  { entity, uuid },
  method,
  payload
) {
  const url = `${baseUrl}/${entity}/${uuid ? uuid + '/' : ''}`
  const response = await fetch(url, {
    method: method || 'GET',
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: payload ? JSON.stringify(payload) : null,
  })
  return response
}

/**
 * Generic deletion through API.
 *
 * @param entity Name of entity to delete.
 * @param uuid The UUID of the entity to delete.
 * @param appContext The appContext to use for baseUrl and csrfToken.
 */
async function apiDelete(entity, uuid, appContext) {
  const entityToken = entity.replace('_', '')
  const response = await apiFetch(
    appContext,
    { entity: entityToken, uuid },
    'DELETE'
  )
  /* istanbul ignore next */
  if (!response.ok) {
    throw new Error(
      `Problem with request: ${response.status} ${response.statusText}`
    )
  }
  return await response.json()
}

/**
 * Generic update/create through API via HTTP PATCH/POST
 */
async function _apiCreateUpdate(create, entity, uuid, payload, appContext) {
  const entityToken = entity.replace('_', '')
  const method = create ? 'POST' : 'PATCH'
  const response = await apiFetch(
    appContext,
    { entity: entityToken, uuid: create ? undefined : uuid },
    method,
    payload
  )
  /* istanbul ignore next */
  if (!response.ok) {
    throw new Error(
      `Problem with request: ${response.status} ${response.statusText}`
    )
  } else {
    return await response.json()
  }
}

/**
 * Generic create through API via HTTP POST.
 *
 * @param entity Name of the entity to update.
 * @param payload The data to use for the update.
 * @param appContext The application context for baseUrl and csrfToken.
 */
async function apiCreate(entity, payload, appContext) {
  return await _apiCreateUpdate(true, entity, undefined, payload, appContext)
}

/**
 * Generic update through API via HTTP PATCH.
 *
 * @param entity Name of the entity to update.
 * @param uuid The UUID of the entity to delete.
 * @param payload The data to use for the update.
 * @param appContext The application context for baseUrl and csrfToken.
 */
async function apiUpdate(entity, uuid, payload, appContext) {
  return await _apiCreateUpdate(false, entity, uuid, payload, appContext)
}

/**
 * Generic retrieval of entities from API.
 *
 * @param entity Name of entity to retrieve.
 * @param appContext The appContext to use for baseUrl and csrfToken.
 */
async function getEntities(entity, appContext) {
  const response = await apiFetch(appContext, {
    entity: entity.replace('_', ''),
  })
  return await response.json()
}

async function genericTermQueryImpl(
  { baseUrl, csrfToken },
  name,
  label,
  termId
) {
  const response = await fetch(
    `${baseUrl}/query-${name}/?query=${encodeURIComponent(termId)}`,
    {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: null,
    }
  )
  return await response.json()
}

export default {
  async getSubmissionSetXml({ baseUrl, csrfToken }, submissionSetUuid) {
    const url = `${baseUrl}/clinvar-xml/${submissionSetUuid}/`
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: 'text/xml',
        'X-CSRFToken': csrfToken,
      },
    })
    return response
  },

  async getSubmissionSetValid({ baseUrl, csrfToken }, submissionSetUuid) {
    const url = `${baseUrl}/clinvar-validate/${submissionSetUuid}/`
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        'X-CSRFToken': csrfToken,
      },
    })
    return response
  },

  async getOrganisations(appContext) {
    return await getEntities('organisation', appContext)
  },

  async getFamilies(appContext) {
    return await getEntities('family', appContext)
  },

  async getSubmitters(appContext) {
    return await getEntities('submitter', appContext)
  },

  async getAssertionMethods(appContext) {
    return await getEntities('assertion_method', appContext)
  },

  async getSubmissionSets(appContext) {
    return await getEntities('submission_set', appContext)
  },

  async createSubmissionSet(submissionSet, appContext) {
    return await apiCreate('submission_set', submissionSet, appContext)
  },

  async updateSubmissionSet(submissionSet, appContext) {
    return await apiUpdate(
      'submission_set',
      submissionSet.sodar_uuid,
      submissionSet,
      appContext
    )
  },

  async deleteSubmissionSet(submissionSet, appContext) {
    return await apiDelete(
      'submission_set',
      submissionSet.sodar_uuid,
      appContext
    )
  },

  async getSubmissions(appContext) {
    return await getEntities('submission', appContext)
  },

  async createSubmission(submission, appContext) {
    return await apiCreate('submission', submission, appContext)
  },

  async updateSubmission(submission, appContext) {
    return await apiUpdate(
      'submission',
      submission.sodar_uuid,
      submission,
      appContext
    )
  },

  async deleteSubmission(submission, appContext) {
    return await apiDelete('submission', submission.sodar_uuid, appContext)
  },

  async getSubmissionIndividuals(appContext) {
    return await getEntities('submission_individual', appContext)
  },

  async getIndividuals(appContext) {
    return await getEntities('individual', appContext)
  },

  async createSubmissionIndividual(submissionIndividual, appContext) {
    return await apiCreate(
      'submission_individual',
      submissionIndividual,
      appContext
    )
  },

  async updateSubmissionIndividual(submissionIndividual, appContext) {
    return await apiUpdate(
      'submission_individual',
      submissionIndividual.sodar_uuid,
      submissionIndividual,
      appContext
    )
  },

  async deleteSubmissionIndividual(submissionIndividual, appContext) {
    return await apiDelete(
      'submission_individual',
      submissionIndividual.sodar_uuid,
      appContext
    )
  },

  async getSubmittingOrgs(appContext) {
    return await getEntities('submitting_org', appContext)
  },

  async createSubmittingOrg(submittingOrg, appContext) {
    return await apiCreate('submitting_org', submittingOrg, appContext)
  },

  async updateSubmittingOrg(submittingOrg, appContext) {
    return await apiUpdate(
      'submitting_org',
      submittingOrg.sodar_uuid,
      submittingOrg,
      appContext
    )
  },

  async deleteSubmittingOrg(submittingOrg, appContext) {
    return await apiDelete(
      'submitting_org',
      submittingOrg.sodar_uuid,
      appContext
    )
  },

  async getUserAnnotations(appContext, familyUuid) {
    const response = await fetch(
      `${appContext.baseUrl}/user-annotations/${familyUuid}`,
      {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': appContext.csrfToken,
        },
        body: null,
      }
    )
    return await response.json()
  },

  async genericTermQuery(appContext, name, label, termId) {
    return await genericTermQueryImpl(appContext, name, label, termId)
  },

  async queryOmim(appContext, termId) {
    return await genericTermQueryImpl(appContext, 'omim', 'OMIM', termId)
  },

  async queryHpo(appContext, termId) {
    return await genericTermQueryImpl(appContext, 'hpo', 'HPO', termId)
  },
}

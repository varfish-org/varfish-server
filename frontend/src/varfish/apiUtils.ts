/**
 * Execute request to AJAX API.
 *
 * @param url Base URL from appContext
 * @param csrfToken CSRF context from appContext
 * @param method (Optional) HTTP method to use, defaults to 'GET'
 * @param payload (Optional) payload to use
 * @returns {Promise<Response>}
 */
export async function apiFetch(
  csrfToken: string,
  url: string,
  method: string = 'GET',
  payload: any = null,
): Promise<Response> {
  const response = await fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/vnd.bihealth.varfish+json',
      // 'Content-Type': 'application/vnd.bihealth.varfish+json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: payload ? JSON.stringify(payload) : null,
  })
  if (response.ok) {
    return response
  } else {
    return Promise.reject(response)
  }
}

/**
 * Convert Array of objects with `sodar_uuid` member to mapping from UUID to object.
 *
 * @param lst Array with such objects.
 * @return Object with the mapping.
 */
export function sodarObjectListToObject(lst: any[]): any {
  return Object.fromEntries(lst.map((o) => [o.sodar_uuid, o]))
}

export interface FetchArgs {
  accept?: string
  contentType?: string
}

/**
 * Base class for API clients.
 *
 * The primary purpose is to store the CSRF token and provide the `fetchHelper` function.
 */
export class ClientBase {
  /** CSRF token to use. */
  csrfToken: string

  constructor(csrfToken: string) {
    this.csrfToken = csrfToken
  }

  protected async fetchHelper<Payload>(
    url: string,
    method: string,
    payload?: Payload,
    fetchArgs?: FetchArgs,
  ): Promise<any> {
    const accept = fetchArgs?.accept ?? 'application/vnd.bihealth.varfish+json'
    const contentType = fetchArgs?.contentType ?? 'application/json'
    const response = await fetch(url, {
      method,
      credentials: 'same-origin',
      headers: {
        Accept: accept,
        'Content-Type': contentType,
        'X-CSRFToken': this.csrfToken,
      },
      body: payload ? JSON.stringify(payload) : null,
    })
    // TODO: move to deleteHelper?
    if (method === 'DELETE') {
      return null
    } else {
      return await response.json()
    }
  }
}

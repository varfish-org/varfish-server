/**
 * Execute request to AJAX API.
 *
 * @param url Base URL from appContext
 * @param csrfToken CSRF context from appContext
 * @param method (Optional) HTTP method to use, defaults to 'GET'
 * @param payload (Optional) payload to use
 * @returns {Promise<Response>}
 */
export async function apiFetch(csrfToken, url, method = 'GET', payload) {
  const response = await fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/vnd.bihealth.varfish+json',
      'Content-Type': 'application/vnd.bihealth.varfish+json',
      'X-CSRFToken': csrfToken,
    },
    body: payload ? JSON.stringify(payload) : null,
  })
  return response
}

/**
 * Convert Array of objects with `sodar_uuid` member to mapping from UUID to object.
 *
 * @param lst Array with such objects.
 * @return Object with the mapping.
 */
export function sodarObjectListToObject(lst) {
  return Object.fromEntries(lst.map((o) => [o.sodar_uuid, o]))
}

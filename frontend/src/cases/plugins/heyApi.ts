/** Setup the Hey API client. */
import { client } from '@varfish-org/varfish-api/lib'
import { client as vigunoClient } from '@varfish-org/viguno-api/lib'

export { client, vigunoClient }

/**
 * Returns the value of a cookie.
 *
 * @param name The name of the cookie.
 * @returns The value of the cookie.
 */
const getCookie = (name: string): string | undefined => {
  const nameLenPlus = name.length + 1
  return (
    document.cookie
      .split(';')
      .map((c) => c.trim())
      .filter((cookie) => {
        return cookie.substring(0, nameLenPlus) === `${name}=`
      })
      .map((cookie) => {
        return decodeURIComponent(cookie.substring(nameLenPlus))
      })[0] || undefined
  )
}

// Ensure the CSRF token is set for all requests.
client.interceptors.request.use((request, _options) => {
  const csrfToken = getCookie('csrftoken') || ''
  request.headers.set('X-CSRFToken', csrfToken)
  return request
})

// Ensure the CSRF token is set for all requests.
vigunoClient.interceptors.request.use((request, _options) => {
  const csrfToken = getCookie('csrftoken') || ''
  request.headers.set('X-CSRFToken', csrfToken)
  return request
})

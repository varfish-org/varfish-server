/**
 * Update user settings via the REST API.
 *
 * @param csrfToken The CSRF token to use.
 * @param settingName The name of the setting.
 * @param value The new value of teh setting
 * @returns `Promise` with the `Response` of the `fetch` call.
 */
export async function updateUserSetting(
  csrfToken: string,
  settingName: string,
  value: any,
): Promise<Response> {
  const url = `/vueapp/ajax/user-setting/${settingName}/`
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ value }),
  })
  return response
}

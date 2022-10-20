export async function updateUserSetting(csrfToken, settingName, newValue) {
  const url = `/vueapp/ajax/user-setting/${settingName}/`
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ value: newValue }),
  })
  return response
}

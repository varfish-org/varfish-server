export function displayName(name) {
  if (name) {
    const re = /-N\d+-(DNA|RNA)\d+-(WES|WGS)\d+$/
    return name.replace(re, '')
  } else {
    return name
  }
}

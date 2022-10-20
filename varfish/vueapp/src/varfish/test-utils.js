// Basic copy function for data objects
export function copy(obj) {
  return JSON.parse(JSON.stringify(obj))
}

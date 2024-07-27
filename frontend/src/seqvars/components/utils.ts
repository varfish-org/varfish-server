export function toggleArrayElement(arr: string[] | undefined, element: string) {
  if (arr == undefined) {
    return
  }
  const index = arr.indexOf(element)
  if (index === -1) {
    arr.push(element)
  } else {
    arr.splice(index, 1)
  }
}

export function isKeyOfObject<T extends object>(
  key: string | number | symbol,
  obj: T,
): key is keyof T {
  return key in obj
}

export type AnyObject = { [key: string]: any }

export function deepCopyAndOmit<T>(obj: T, keysToOmit: string[]): T {
  function isObject(value: any): value is AnyObject {
    return value !== null && typeof value === 'object'
  }

  function deepCopy(obj: any): any {
    if (!isObject(obj)) {
      return obj
    }

    if (Array.isArray(obj)) {
      return obj.map((item) => deepCopy(item))
    }

    const result: AnyObject = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key) && !keysToOmit.includes(key)) {
        result[key] = deepCopy(obj[key])
      }
    }
    return result
  }

  return deepCopy(obj) as T
}

import {
  HpoOmim,
  HpoTerm,
  VigunoClient,
} from '@bihealth/reev-frontend-lib/api/viguno'

/**
 * Helper that adds/removes an element from a string array to invert its presence.
 *
 * @param arr Array to modify.
 * @param element Element to add/remove.
 * @returns Modified array or `undefined` if input was `undefined`.
 */
export const toggleArrayElement = <T>(
  arr: T[] | undefined,
  element: T,
): T[] | undefined => {
  if (arr === undefined) {
    return undefined
  }

  const result = [...arr]
  const index = result.indexOf(element)
  if (index === -1) {
    result.push(element)
  } else {
    result.splice(index, 1)
  }
  return result
}

export function isKeyOfObject<T extends object>(
  key: string | number | symbol,
  obj: T,
): key is keyof T {
  return key in obj
}

export async function queryHpoAndOmimTerms(query: string) {
  const vigunoClient = new VigunoClient('/proxy/varfish/viguno')
  const queryArg = encodeURIComponent(query)
  let results: (HpoTerm | HpoOmim)[]
  if (query.startsWith('HP:')) {
    results = (await vigunoClient.resolveHpoTermById(queryArg)).result
  } else if (query.startsWith('OMIM:')) {
    results = (await vigunoClient.resolveOmimTermById(queryArg)).result
  } else {
    let [{ result: hpoResults }, { result: omimResults }] = await Promise.all([
      vigunoClient.queryHpoTermsByName(queryArg),
      vigunoClient.queryOmimTermsByName(queryArg),
    ])
    if (hpoResults.length < 2 && omimResults.length > 2) {
      omimResults = omimResults.slice(0, 2 + hpoResults.length)
    } else if (omimResults.length < 2 && hpoResults.length > 2) {
      hpoResults = hpoResults.slice(0, 2 + omimResults.length)
    } else {
      hpoResults = hpoResults.slice(0, 2)
      omimResults = omimResults.slice(0, 2)
    }
    results = [...hpoResults, ...omimResults]
  }

  return results.map(({ name, ...item }) => {
    const id = 'termId' in item ? item.termId : item.omimId
    return { label: name, term_id: id }
  })
}

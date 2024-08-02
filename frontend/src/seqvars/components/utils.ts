import {
  HpoOmim,
  HpoTerm,
  VigunoClient,
} from '@bihealth/reev-frontend-lib/api/viguno'

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

export async function queryHPO_Terms(query: string) {
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

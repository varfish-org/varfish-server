import isEqual from 'fast-deep-equal'

import { LocalFields } from '@/seqvars/types'
import {
  HpoOmim,
  HpoTerm,
  VigunoClient,
} from '@bihealth/reev-frontend-lib/api/viguno'
import {
  SeqvarsQueryPresetsPhenotypePrio,
  SeqvarsQuerySettingsPhenotypePrio,
} from '@varfish-org/varfish-api/lib'

export function matchesPhenotypePrioPreset(
  value: LocalFields<SeqvarsQuerySettingsPhenotypePrio>,
  preset: SeqvarsQueryPresetsPhenotypePrio,
) {
  return isEqual(
    ...([value, preset].map((v) => [
      v.phenotype_prio_enabled,
      v.phenotype_prio_algorithm,
      v.terms,
    ]) as [unknown, unknown]),
  )
}

export async function fetchHPO(query: string) {
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

import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'

export function getQueryLabel({
  presetDetails,
  queries,
  index,
}: {
  presetDetails: SeqvarsQueryPresetsSetVersionDetails
  queries: Query[]
  index: number
}) {
  const query = queries.at(index)
  const presetLabel = presetDetails.seqvarspredefinedquery_set.find(
    (pq) => pq.sodar_uuid === query?.predefinedquery,
  )?.label
  const othersCount = queries
    .slice(0, index)
    .filter((q) => q.predefinedquery === query?.predefinedquery).length
  return `${presetLabel} ${othersCount > 0 ? `(${othersCount})` : ''}`
}

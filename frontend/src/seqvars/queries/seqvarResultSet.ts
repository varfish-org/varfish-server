/**
 * Queries for seqvars result sets and related powered by TanStack Query.
 */
import { useQueries, useQuery } from '@tanstack/vue-query'
import {
  seqvarsApiResultsetListOptions,
  seqvarsApiResultsetRetrieveOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, computed, toValue } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/**
 * Query for result set of one seqvar query.
 *
 * @param queryExecutionUuid UUID of the seqvar query to load executions for.
 * @returns Query result with pages of seqvar result sets.
 */
export const useSeqvarResultSetListQuery = ({
  queryExecutionUuid,
}: {
  queryExecutionUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiResultsetListOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        queryexecution: () => toValue(queryExecutionUuid)!,
      },
    }),
    enabled: () => !!toValue(queryExecutionUuid),
    staleTime: 1000 * 5,
  })
}

/**
 * Query for result set of a list of seqvar result sets.
 *
 * @param queryExecutionUuids UUID of the seqvar query execution to load executions for.
 * @returns Query result with pages of seqvar result sets.
 */
export const useSeqvarResultSetListQueries = ({
  queryExecutionUuids,
}: {
  queryExecutionUuids: MaybeRefOrGetter<string[] | undefined>
}) => {
  return useQueries({
    queries: computed(() =>
      (toValue(queryExecutionUuids) ?? []).map((queryExecutionUuid) => ({
        ...seqvarsApiResultsetListOptions({
          client,
          path: {
            queryexecution: queryExecutionUuid,
          },
        }),
        enabled: () => !!toValue(queryExecutionUuids)?.length,
        staleTime: 1000 * 5,
      })),
    ),
  })
}

/**
 * Query for a single seqvar result set details within a seqvar query execution.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param queryExecutionUuid UUID of the seqvar result set to load.
 * @param resultSetUuid UUID of the result set to load.
 */
export const useSeqvarResultSetRetrieveQuery = ({
  queryExecutionUuid,
  resultSetUuid,
}: {
  queryExecutionUuid: MaybeRefOrGetter<string | undefined>
  resultSetUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiResultsetRetrieveOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        queryexecution: () => toValue(queryExecutionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        resultset: () => toValue(resultSetUuid)!,
      },
    }),
    enabled: () => !!toValue(resultSetUuid) && !!toValue(queryExecutionUuid),
  })
}

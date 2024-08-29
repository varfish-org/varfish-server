/**
 * Queries for seqvars query executions and related powered by TanStack Query.
 */
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import {
  seqvarsApiQueryexecutionListInfiniteOptions,
  seqvarsApiQueryexecutionRetrieveOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, toValue } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/**
 * Query for a list of seqvar query executions within a seqvar query.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param queryUuid UUID of the seqvar query to load executions for.
 * @returns Query result with page of seqvar query executions.
 */
export const useSeqvarQueryExecutionListQuery = ({
  queryUuid,
}: {
  queryUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useInfiniteQuery({
    ...seqvarsApiQueryexecutionListInfiniteOptions({
      client,
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { query: () => toValue(queryUuid)! },
    }),
    enabled: () => !!toValue(queryUuid),
    getNextPageParam: (lastPage) => lastPage.next,
  })
}

/**
 * Query for a single seqvar query execution details within a seqvar query.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param queryUuid UUID of the seqvar query that contains the execution.
 * @param queryExecutionUuid UUID of the seqvar query execution to load.
 */
export const useSeqvarQueryExecutionRetrieveQuery = ({
  queryUuid,
  queryExecutionUuid,
}: {
  queryUuid: MaybeRefOrGetter<string | undefined>
  queryExecutionUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQueryexecutionRetrieveOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        query: () => toValue(queryUuid),
        queryexecution: toValue(queryExecutionUuid)!,
      },
    }),
    enabled: () => !!toValue(queryUuid) && !!toValue(queryExecutionUuid),
  })
}

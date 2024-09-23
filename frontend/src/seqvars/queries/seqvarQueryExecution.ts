/**
 * Queries for seqvars query executions and related powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQueries,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  seqvarsApiQueryexecutionListOptions,
  seqvarsApiQueryexecutionRetrieveOptions,
  seqvarsApiQueryexecutionStartCreateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, computed, toValue } from 'vue'

/**
 * Helper to invalidate execution keys for lists and retrieval for a single
 * execution.
 *
 * Will always invalidate the list execution results and optionally invalidate the
 * retrieval query results if `execution` is set.
 *
 * @param queryClient Query client to use.
 * @param query UUID of the query.
 * @param queryExecution UUID of the query execution, optional.
 * @param destroy Whether to destroy the query instead of invalidating it.
 */
const invalidateSeqvarQueryExecutionKeys = (
  queryClient: QueryClient,
  {
    query,
    queryexecution: queryExecution,
  }: {
    query: string
    queryexecution?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQueryexecutionListOptions({ path: { query } }).queryKey,
  })
  if (queryExecution !== undefined) {
    const arg = {
      queryKey: seqvarsApiQueryexecutionRetrieveOptions({
        path: {
          query,
          queryexecution: queryExecution,
        },
      }).queryKey,
    }
    if (destroy) {
      queryClient.removeQueries(arg)
    } else {
      queryClient.invalidateQueries(arg)
    }
  }
}

/**
 * Mutation for creating a new query execution by starting a query.
 *
 * @returns Mutation object.
 */
export const useSeqvarQueryExecutionStartMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQueryexecutionStartCreateMutation(),
    // Always refetch after error or success.
    onSettled: (data) => {
      if (!!data) {
        // Refetch after success or error.
        invalidateSeqvarQueryExecutionKeys(queryClient, {
          query: data.query,
        })
      }
    },
  })
}

/**
 * Query for query execution of a list of seqvar queries.
 *
 * @param seqvarQueryUuids UUID of the seqvar query to load executions for.
 * @returns Query result with pages of seqvar query executions.
 */
export const useSeqvarQueryExecutionListQueries = ({
  seqvarQueryUuids,
}: {
  seqvarQueryUuids: MaybeRefOrGetter<string[] | undefined>
}) => {
  return useQueries({
    queries: computed(() =>
      (toValue(seqvarQueryUuids) ?? []).map((seqvarQueryUuid) => ({
        ...seqvarsApiQueryexecutionListOptions({
          path: {
            query: seqvarQueryUuid,
          },
        }),
        enabled: () => !!toValue(seqvarQueryUuids)?.length,
        staleTime: 1000 * 5,
      })),
    ),
  })
}

// TODO: currently unused
//
// /**
//  * Query for a single seqvar query execution details within a seqvar query.
//  *
//  * The objects returned when retrieved are more nested and contain the actual
//  * data.
//  *
//  * @param queryUuid UUID of the seqvar query that contains the execution.
//  * @param queryExecutionUuid UUID of the seqvar query execution to load.
//  */
// export const useSeqvarQueryExecutionRetrieveQuery = (
//   {
//     queryUuid,
//     queryExecutionUuid,
//   }: {
//     queryUuid: MaybeRefOrGetter<string | undefined>
//     queryExecutionUuid: MaybeRefOrGetter<string | undefined>
//   },
// ) => {
//   return useQuery(
//     {
//       ...seqvarsApiQueryexecutionRetrieveOptions({
//         path: {
//           // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
//           query: () => toValue(queryUuid),
//           queryexecution: toValue(queryExecutionUuid)!,
//         },
//       }),
//       enabled: () => !!toValue(queryUuid) && !!toValue(queryExecutionUuid),
//     },
//   )
// }

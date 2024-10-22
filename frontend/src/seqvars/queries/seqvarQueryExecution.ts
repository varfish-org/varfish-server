/**
 * Queries for seqvars query executions and related powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQueries,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  seqvarsApiQueryexecutionListOptions,
  seqvarsApiQueryexecutionRetrieveOptions,
  seqvarsApiQueryexecutionStartCreateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, computed, toValue } from 'vue'

import { client } from '@/cases/plugins/heyApi'

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
    queryExecution,
  }: {
    query: string
    queryExecution?: string
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
 * Query for query execution of one seqvar query.
 *
 * @param seqvarQueryUuid UUID of the seqvar query to load executions for.
 * @returns Query result with pages of seqvar query executions.
 */
export const useSeqvarQueryExecutionListQuery = ({
  seqvarQueryUuid,
}: {
  seqvarQueryUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQueryexecutionListOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        query: () => toValue(seqvarQueryUuid)!,
      },
    }),
    enabled: () => !!toValue(seqvarQueryUuid),
    staleTime: 500,
  })
}

/**
 * Query for query execution of a list of seqvar queries.
 *
 * @param seqvarQueryUuids UUIDs of the seqvar queries to load executions for.
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
          client,
          path: {
            query: seqvarQueryUuid,
          },
        }),
        enabled: () => !!toValue(seqvarQueryUuids)?.length,
        staleTime: 500,
      })),
    ),
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
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        queryexecution: () => toValue(queryExecutionUuid)!,
      },
    }),
    enabled: () => !!toValue(queryUuid) && !!toValue(queryExecutionUuid),
  })
}

/**
 * Queries for seqvars queries and related powered by TanStack Query.
 */
import {
  QueryClient,
  useInfiniteQuery,
  useMutation,
  useQueries,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import { SeqvarsApiQueryUpdateData } from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQueryCreateFromCreateMutation,
  seqvarsApiQueryDestroyMutation,
  seqvarsApiQueryListInfiniteOptions,
  seqvarsApiQueryListOptions,
  seqvarsApiQueryRetrieveOptions,
  seqvarsApiQueryUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmergeCustom } from 'deepmerge-ts'
import { MaybeRefOrGetter, computed, toRaw, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query.
 *
 * Will always invalidate the list query results and optionally invalidate the
 * retrieval query results if `query` is set.
 *
 * @param queryClient Query client to use.
 * @param session UUID of the session.
 * @param query UUID of the query, optional.
 * @param destroy Whether to destroy the query instead of invalidating it.
 */
const invalidateSeqvarQueryKeys = (
  queryClient: QueryClient,
  {
    session,
    query,
  }: {
    session: string
    query?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQueryListInfiniteOptions({ path: { session } })
      .queryKey,
  })
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQueryListOptions({
      path: { session },
      query: {
        page: 1,
        page_size: 100,
      },
    }).queryKey,
  })
  if (query !== undefined) {
    const arg = {
      queryKey: seqvarsApiQueryRetrieveOptions({
        path: {
          session,
          query,
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
 * Query for a list of seqvar queries within a case analysis session.
 *
 * Uses the list API of TanStack Query and query for 100 items for now as the infinite
 * query API breaks the TanStack Query devtools plugin.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param sessionUuid UUID of the case analysis session to load queries for.
 * @returns Query result with page of seqvars queries.
 */
export const useSeqvarQueryListQuery = ({
  sessionUuid,
}: {
  sessionUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQueryListOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { session: () => toValue(sessionUuid)! },
      query: {
        page: 1,
        page_size: 100,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(sessionUuid),
  })
}

/**
 * Query for a list of seqvar queries within a case analysis session.
 *
 * Uses the infinite list API of TanStack Query.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param sessionUuid UUID of the case analysis session to load queries for.
 * @returns Query result with page of seqvars queries.
 */
export const useSeqvarQueryListInfiniteQuery = ({
  sessionUuid,
}: {
  sessionUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useInfiniteQuery({
    ...seqvarsApiQueryListInfiniteOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { session: () => toValue(sessionUuid)! },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(sessionUuid),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    getNextPageParam: (lastPage) => lastPage.next,
  })
}

/**
 * Query for a single seqvar query details within a case analysis session.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param sessionUuid
 *    UUID of the case analysis session that contains the seqvar query.
 * @param seqvarQueryUuid UUID of the seqvar query to load.
 */
export const useSeqvarQueryRetrieveQuery = ({
  sessionUuid,
  seqvarQueryUuid,
}: {
  sessionUuid: MaybeRefOrGetter<string | undefined>
  seqvarQueryUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQueryRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        session: () => toValue(sessionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        query: () => toValue(seqvarQueryUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(sessionUuid) && !!toValue(seqvarQueryUuid),
  })

/**
 * Query for a list of seqvar queries within a case analysis session.
 *
 * @param sessionUuid UUID of the case analysis session to load queries for.
 * @param seqvarQueryUUids UUIDs of the seqvar queries to load.
 * @returns Query result with page of seqvars queries.
 */
export const useSeqvarQueryRetrieveQueries = ({
  sessionUuid,
  seqvarQueryUuids,
}: {
  sessionUuid: MaybeRefOrGetter<string | undefined>
  seqvarQueryUuids: MaybeRefOrGetter<string[] | undefined>
}) =>
  useQueries({
    queries: computed(() =>
      (toValue(seqvarQueryUuids) ?? []).map((seqvarQueryUuid) => ({
        ...seqvarsApiQueryRetrieveOptions({
          path: {
            session: toValue(sessionUuid)!,
            query: seqvarQueryUuid,
          },
        }),
        enabled: () =>
          !!toValue(sessionUuid) && !!toValue(seqvarQueryUuids)?.length,
      })),
    ),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    combine: (results) => {
      return {
        data: results
          .map((result) => result.data)
          .filter((data) => data !== undefined),
        pending: results.some((result) => result.isPending),
      }
    },
  })

// TODO: currently unused
//
// /**
//  * Mutation for the creation of a `SeqvarsQuery` object.
//  *
//  * @returns Mutation object.
//  */
// export const useSeqvarQueryCreateMutation = () => {
//   const queryClient = useQueryClient()
//   return useMutation({
//     ...seqvarsApiQueryCreateMutation(),
//     onSettled: (data) => {
//       if (!!data) {
//         // Refetch after success or error.
//         invalidateSeqvarQueryKeys(queryClient, {
//           session: data.session,
//           query: data.sodar_uuid,
//         })
//       }
//     },
//   })
// }

/**
 * Mutation for the creation of a `SeqvarsQuery` object from presets.
 *
 * @returns Mutation object.
 */
export const useCopySeqvarQueryFromPresetCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQueryCreateFromCreateMutation(),
    onSettled: (data) => {
      if (!!data) {
        // Refetch after success or error.
        invalidateSeqvarQueryKeys(queryClient, {
          session: data.session,
          query: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQuery` object.
 *
 * For updates, we implement optimistic updates and rollback on error.
 *
 * @returns Mutation object.
 */
export const useSeqvarQueryUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQueryUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQueryUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQueryRetrieveOptions({
        path: data.path,
      }).queryKey
      await queryClient.cancelQueries({ queryKey })
      // Snapshot the previous value.
      const previousValue = queryClient.getQueryData(queryKey)
      // Optimistically update to the new value.
      const newValue =
        previousValue === undefined
          ? undefined
          : deepmergeCustom({ mergeArrays: false })(previousValue, data.body)
      if (
        newValue !== undefined &&
        data.body.settings.columns.column_settings !== undefined
      ) {
        // Need to manually clone the column settings as we disable merging of
        // arrays in `deepmergeCustom()` call.
        newValue.settings.columns.column_settings = structuredClone(
          toRaw(data.body.settings.columns.column_settings),
        )
      }
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQueryRetrieveOptions({ path: variables.path }).queryKey,
          context.previousValue,
        )
      }
    },
    // Always refetch after error or success.
    onSettled: (data) => {
      if (!!data) {
        // Refetch after success or error.
        invalidateSeqvarQueryKeys(queryClient, {
          session: data.session,
          query: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQuery` object.
 */
export const useSeqvarQueryDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQueryDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarQueryKeys(queryClient, context.path, { destroy: true })
    },
  })
}

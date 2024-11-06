/**
 * Queries for seqvars predefined query powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiPredefinedqueryUpdateData,
  SeqvarsPredefinedQuery,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiPredefinedqueryCreateMutation,
  seqvarsApiPredefinedqueryDestroyMutation,
  seqvarsApiPredefinedqueryListOptions,
  seqvarsApiPredefinedqueryRetrieveOptions,
  seqvarsApiPredefinedqueryUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single predefined query.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param predefinedquery UUID of the predefined query.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsPredefinedQueryKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    predefinedquery,
  }: {
    querypresetssetversion: string
    predefinedquery?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the columns prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiPredefinedqueryListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (predefinedquery !== undefined) {
    const arg = {
      queryKey: seqvarsApiPredefinedqueryRetrieveOptions({
        path: {
          querypresetssetversion,
          predefinedquery,
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
 * Query for a list of seqvar predefined query sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of columns presets.
 */
export const useSeqvarsPredefinedQueryListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiPredefinedqueryListOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { project: () => toValue(projectUuid)! },
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      query: () => ({
        page: 1,
        page_size: 100,
      }),
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(projectUuid),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    getNextPageParam: (lastPage) => lastPage.next,
  })
}

/**
 * Query for a single seqvar predefined query set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the columns preset.
 * @param presetsColumnsUuid UUID of the columns presets to load.
 */
export const useSeqvarsPredefinedQueryRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsColumnsUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsColumnsUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiPredefinedqueryRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        predefinedquery: () => toValue(presetsColumnsUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsColumnsUuid),
  })

/**
 * Mutation for creating a `SeqvarsPredefinedQuery` object.
 */
export const useSeqvarsPredefinedQueryCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiPredefinedqueryCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsPredefinedQueryKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsPredefinedQuery` object.
 */
export const useSeqvarsPredefinedQueryUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiPredefinedqueryUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiPredefinedqueryUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiPredefinedqueryRetrieveOptions({
        path: data.path,
      }).queryKey
      await queryClient.cancelQueries({ queryKey })
      // Snapshot the previous value.
      const previousValue = queryClient.getQueryData(queryKey)
      // Optimistically update to the new value.
      //
      // Note that the explicit case of `data.body` is necessary as we would lose the
      // server-maintained fields such as `date_created` and `date_modified` otherwise.
      const newValue =
        previousValue === undefined && data.body === undefined
          ? undefined
          : deepmerge(previousValue, data.body as SeqvarsPredefinedQuery)
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiPredefinedqueryRetrieveOptions({
            path: variables.path,
          }).queryKey,
          context.previousValue,
        )
      }
    },
    // Always refetch after error or success.
    onSettled: (data) => {
      if (!!data) {
        // Refetch after success or error.
        invalidateSeqvarsPredefinedQueryKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          predefinedquery: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsPredefinedQuery` object.
 */
export const useSeqvarsPredefinedQueryDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiPredefinedqueryDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsPredefinedQueryKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

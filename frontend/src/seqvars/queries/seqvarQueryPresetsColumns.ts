/**
 * Queries for seqvars query columns presets powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetscolumnsUpdateData,
  SeqvarsQueryPresetsColumns,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetscolumnsCreateMutation,
  seqvarsApiQuerypresetscolumnsDestroyMutation,
  seqvarsApiQuerypresetscolumnsListOptions,
  seqvarsApiQuerypresetscolumnsRetrieveOptions,
  seqvarsApiQuerypresetscolumnsUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query columns presets.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param querypresetscolumns UUID of the query columns presets.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsQueryPresetsColumnsKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    querypresetscolumns,
  }: {
    querypresetssetversion: string
    querypresetscolumns?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the columns prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetscolumnsListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (querypresetscolumns !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetscolumnsRetrieveOptions({
        path: {
          querypresetssetversion,
          querypresetscolumns,
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
 * Query for a list of seqvar query columns presets sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of columns presets.
 */
export const useSeqvarsQueryPresetsColumnsListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetscolumnsListOptions({
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
 * Query for a single seqvar query columns presets set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the columns preset.
 * @param presetsColumnsUuid UUID of the columns presets to load.
 */
export const useSeqvarsQueryPresetsColumnsRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsColumnsUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsColumnsUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetscolumnsRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetscolumns: () => toValue(presetsColumnsUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsColumnsUuid),
  })

/**
 * Mutation for creating a `SeqvarsQueryPresetsColumns` object.
 */
export const useSeqvarsQueryPresetsColumnsCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetscolumnsCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsColumnsKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetsColumns` object.
 */
export const useSeqvarsQueryPresetsColumnsUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetscolumnsUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetscolumnsUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetscolumnsRetrieveOptions({
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
          : deepmerge(previousValue, data.body as SeqvarsQueryPresetsColumns)
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetscolumnsRetrieveOptions({
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
        invalidateSeqvarsQueryPresetsColumnsKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          querypresetscolumns: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetsColumns` object.
 */
export const useSeqvarsQueryPresetsColumnsDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetscolumnsDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsColumnsKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

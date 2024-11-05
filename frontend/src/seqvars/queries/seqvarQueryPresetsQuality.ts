/**
 * Queries for seqvars query quality presets powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetsqualityUpdateData,
  SeqvarsQueryPresetsQuality,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetsqualityCreateMutation,
  seqvarsApiQuerypresetsqualityDestroyMutation,
  seqvarsApiQuerypresetsqualityListOptions,
  seqvarsApiQuerypresetsqualityRetrieveOptions,
  seqvarsApiQuerypresetsqualityUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query quality presets.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param querypresetsquality UUID of the query quality presets.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsQueryPresetsQualityKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    querypresetsquality,
  }: {
    querypresetssetversion: string
    querypresetsquality?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the quality prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetsqualityListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (querypresetsquality !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetsqualityRetrieveOptions({
        path: {
          querypresetssetversion,
          querypresetsquality,
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
 * Query for a list of seqvar query quality presets sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of quality presets.
 */
export const useSeqvarsQueryPresetsQualityListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetsqualityListOptions({
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
 * Query for a single seqvar query quality presets set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the quality preset.
 * @param seqvarQueryUuid UUID of the quality presets to load.
 */
export const useSeqvarsQueryPresetsQualityRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsSetQualityUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsSetQualityUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetsqualityRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        presetsset: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetsquality: () => toValue(presetsSetQualityUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsSetQualityUuid),
  })

/**
 * Mutation for creating a `SeqvarsQueryPresetsQuality` object.
 */
export const useSeqvarsQueryPresetsQualityCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsqualityCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsQualityKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetSetVersion` object.
 */
export const useSeqvarQueryPresetsSetVersionUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsqualityUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetsqualityUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetsqualityRetrieveOptions({
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
          : deepmerge(previousValue, data.body as SeqvarsQueryPresetsQuality)
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetsqualityRetrieveOptions({
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
        invalidateSeqvarsQueryPresetsQualityKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          querypresetsquality: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetsQuality` object.
 */
export const useSeqvarsQueryPresetsQualityDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsqualityDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsQualityKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

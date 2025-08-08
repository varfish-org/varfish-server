/**
 * Queries for seqvars query locus presets powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetslocusUpdateData,
  SeqvarsQueryPresetsLocus,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetslocusCreateMutation,
  seqvarsApiQuerypresetslocusDestroyMutation,
  seqvarsApiQuerypresetslocusListOptions,
  seqvarsApiQuerypresetslocusRetrieveOptions,
  seqvarsApiQuerypresetslocusUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query locus presets.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param querypresetslocus UUID of the query locus presets.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsQueryPresetsLocusKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    querypresetslocus,
  }: {
    querypresetssetversion: string
    querypresetslocus?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the locus prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetslocusListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (querypresetslocus !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetslocusRetrieveOptions({
        path: {
          querypresetssetversion,
          querypresetslocus,
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
 * Query for a list of seqvar query locus presets sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of locus presets.
 */
export const useSeqvarsQueryPresetsLocusListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetslocusListOptions({
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
 * Query for a single seqvar query locus presets set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the locus preset.
 * @param presetsLocusUuid UUID of the locus presets to load.
 */
export const useSeqvarsQueryPresetsLocusRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsLocusUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsLocusUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetslocusRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetslocus: () => toValue(presetsLocusUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsLocusUuid),
  })

/**
 * Mutation for creating a `SeqvarsQueryPresetsLocus` object.
 */
export const useSeqvarsQueryPresetsLocusCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetslocusCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsLocusKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetsLocus` object.
 */
export const useSeqvarsQueryPresetsLocusUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetslocusUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetslocusUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetslocusRetrieveOptions({
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
          : deepmerge(previousValue, data.body as SeqvarsQueryPresetsLocus)
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetslocusRetrieveOptions({
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
        invalidateSeqvarsQueryPresetsLocusKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          querypresetslocus: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetsLocus` object.
 */
export const useSeqvarsQueryPresetsLocusDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetslocusDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsLocusKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

/**
 * Queries for seqvars query frequency presets powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetsfrequencyUpdateData,
  SeqvarsQueryPresetsFrequency,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetsfrequencyCreateMutation,
  seqvarsApiQuerypresetsfrequencyDestroyMutation,
  seqvarsApiQuerypresetsfrequencyListOptions,
  seqvarsApiQuerypresetsfrequencyRetrieveOptions,
  seqvarsApiQuerypresetsfrequencyUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query frequency presets.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param querypresetsfrequency UUID of the query frequency presets.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsQueryPresetsFrequencyKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    querypresetsfrequency,
  }: {
    querypresetssetversion: string
    querypresetsfrequency?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the frequency prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetsfrequencyListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (querypresetsfrequency !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetsfrequencyRetrieveOptions({
        path: {
          querypresetssetversion,
          querypresetsfrequency,
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
 * Query for a list of seqvar query frequency presets sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of frequency presets.
 */
export const useSeqvarsQueryPresetsFrequencyListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetsfrequencyListOptions({
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
 * Query for a single seqvar query frequency presets set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the frequency preset.
 * @param presetsFrequencyUuid UUID of the frequency presets to load.
 */
export const useSeqvarsQueryPresetsFrequencyRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsFrequencyUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsFrequencyUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetsfrequencyRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetsfrequency: () => toValue(presetsFrequencyUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsFrequencyUuid),
  })

/**
 * Mutation for creating a `SeqvarsQueryPresetsFrequency` object.
 */
export const useSeqvarsQueryPresetsFrequencyCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsfrequencyCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsFrequencyKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetsFrequency` object.
 */
export const useSeqvarsQueryPresetsFrequencyUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsfrequencyUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetsfrequencyUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetsfrequencyRetrieveOptions({
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
          : deepmerge(previousValue, data.body as SeqvarsQueryPresetsFrequency)
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetsfrequencyRetrieveOptions({
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
        invalidateSeqvarsQueryPresetsFrequencyKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          querypresetsfrequency: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetsFrequency` object.
 */
export const useSeqvarsQueryPresetsFrequencyDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsfrequencyDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsFrequencyKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

/**
 * Queries for seqvars query phenotypeprio presets powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetsphenotypeprioUpdateData,
  SeqvarsQueryPresetsPhenotypePrio,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetsphenotypeprioCreateMutation,
  seqvarsApiQuerypresetsphenotypeprioDestroyMutation,
  seqvarsApiQuerypresetsphenotypeprioListOptions,
  seqvarsApiQuerypresetsphenotypeprioRetrieveOptions,
  seqvarsApiQuerypresetsphenotypeprioUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query phenotypeprio presets.
 *
 * @param queryClient Query client to use.
 * @param querypresetssetversion UUID of the query presets set version.
 * @param querypresetsphenotypeprio UUID of the query phenotypeprio presets.
 * @param destroy Whether to destroy the presets instead of invalidating it.
 */
const invalidateSeqvarsQueryPresetsPhenotypePrioKeys = (
  queryClient: QueryClient,
  {
    querypresetssetversion,
    querypresetsphenotypeprio,
  }: {
    querypresetssetversion: string
    querypresetsphenotypeprio?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  // Below, is the code for invalidating the phenotypeprio prests.
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetsphenotypeprioListOptions({
      path: { querypresetssetversion },
    }).queryKey,
  })
  if (querypresetsphenotypeprio !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetsphenotypeprioRetrieveOptions({
        path: {
          querypresetssetversion,
          querypresetsphenotypeprio,
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
 * Query for a list of seqvar query phenotypeprio presets sets within a presets set version.
 *
 * Uses the list API of TanStack Query.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param querypresetssetversion UUID of the presets set version.
 * @returns Query result with pages of phenotypeprio presets.
 */
export const useSeqvarsQueryPresetsPhenotypePrioListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetsphenotypeprioListOptions({
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
 * Query for a single seqvar query phenotypeprio presets set details within a presets set version.
 *
 * Note that the listed objects are identical to the ones returned for a single
 * retrieve (there is no `*Details` variant, only the slimmer `*Request` one).
 *
 * @param presetsSetVersionUuid
 *    UUID of the presets set version that contains the phenotypeprio preset.
 * @param presetsPhenotypePrioUuid UUID of the phenotypeprio presets to load.
 */
export const useSeqvarsQueryPresetsPhenotypePrioRetrieveQuery = ({
  presetsSetVersionUuid,
  presetsPhenotypePrioUuid,
}: {
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
  presetsPhenotypePrioUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetsphenotypeprioRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetsphenotypeprio: () => toValue(presetsPhenotypePrioUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetVersionUuid) && !!toValue(presetsPhenotypePrioUuid),
  })

/**
 * Mutation for creating a `SeqvarsQueryPresetsPhenotypePrio` object.
 */
export const useSeqvarsQueryPresetsPhenotypePrioCreateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsphenotypeprioCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsPhenotypePrioKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetsPhenotypePrio` object.
 */
export const useSeqvarsQueryPresetsPhenotypePrioUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsphenotypeprioUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetsphenotypeprioUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetsphenotypeprioRetrieveOptions({
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
          : deepmerge(
              previousValue,
              data.body as SeqvarsQueryPresetsPhenotypePrio,
            )
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetsphenotypeprioRetrieveOptions({
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
        invalidateSeqvarsQueryPresetsPhenotypePrioKeys(queryClient, {
          querypresetssetversion: data.presetssetversion,
          querypresetsphenotypeprio: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetsPhenotypePrio` object.
 */
export const useSeqvarsQueryPresetsPhenotypePrioDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetsphenotypeprioDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarsQueryPresetsPhenotypePrioKeys(
        queryClient,
        context.path,
        {
          destroy: true,
        },
      )
    },
  })
}

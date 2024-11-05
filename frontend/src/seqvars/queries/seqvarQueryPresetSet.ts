/**
 * Queries for seqvars query presets sets and related powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import { SeqvarsApiQuerypresetssetUpdateData } from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetssetCopyFromCreateMutation,
  seqvarsApiQuerypresetssetDestroyMutation,
  seqvarsApiQuerypresetssetListOptions,
  seqvarsApiQuerypresetssetRetrieveOptions,
  seqvarsApiQuerypresetssetUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmergeCustom } from 'deepmerge-ts'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Helper to invalidate query keys for lists and retrieval for a single query presets set
 *
 * @param queryClient Query client to use.
 * @param project UUID of the project.
 * @param querypresetsset UUID of the query presets set, optional.
 * @param destroy Whether to destroy the query instead of invalidating it.
 */
const invalidateSeqvarQueryPresetsSetKeys = (
  queryClient: QueryClient,
  {
    project,
    querypresetsset,
  }: {
    project: string
    querypresetsset?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetssetListOptions({ path: { project } })
      .queryKey,
  })
  if (querypresetsset !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetssetRetrieveOptions({
        path: {
          project,
          querypresetsset,
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

// NB: for some reason, the infinite query feature does not work here :(
/**
 * Query for a list of seqvar query presets sets within a project.
 *
 * Uses the list API of TanStack Query.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param projectUuid UUID of the project to load preset sets for.
 * @returns Query result with pages of presets sets.
 */
export const useSeqvarQueryPresetsSetListQuery = ({
  projectUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetssetListOptions({
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
 * Query for a single seqvar query presets set details within a project.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param projectUuid
 *    UUID of the project that contains the presets sets.
 * @param seqvarQueryUuid UUID of the seqvar presets sets to load.
 */
export const useSeqvarQueryPresetsSetRetrieveQuery = ({
  projectUuid,
  presetsSetUuid,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
  presetsSetUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetssetRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        project: () => toValue(projectUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetsset: () => toValue(presetsSetUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(projectUuid) && !!toValue(presetsSetUuid),
  })

// /**
//  * Query for a list of seqvar query presets sets within a project.
//  *
//  * @param projectUuid UUID of the project to load queries for.
//  * @param presetsSetsUuids UUIDs of the seqvar queries to load.
//  * @returns Query result with page of seqvars queries.
//  */
// export const useSeqvarQueryPresetsSetRetrieveQueries = ({
//   projectUuid,
//   presetsSetUuids,
// }: {
//   projectUuid: MaybeRefOrGetter<string | undefined>
//   presetsSetUuids: MaybeRefOrGetter<string[] | undefined>
// }) =>
//   useQueries({
//     queries: computed(() =>
//       (toValue(presetsSetUuids) ?? []).map((presetsSetUuid) => ({
//         ...seqvarsApiQuerypresetssetRetrieveOptions({
//           path: {
//             project: toValue(projectUuid)!,
//             querypresetsset: presetsSetUuid,
//           },
//         }),
//         enabled: () =>
//           !!toValue(projectUuid) && !!toValue(presetsSetUuid)?.length,
//       })),
//     ),
//     // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
//     combine: (results) => {
//       return {
//         data: results
//           .map((result) => result.data)
//           .filter((data) => data !== undefined),
//         pending: results.some((result) => result.isPending),
//       }
//     },
//   })

/**
 * Mutation for copying a `SeqvarsQueryPresetSet` object.
 */
export const useSeqvarQueryPresetsSetCopyFromMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetCopyFromCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarQueryPresetsSetKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetSet` object.
 */
export const useSeqvarQueryPresetsSetUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetssetUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetssetRetrieveOptions({
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
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetssetRetrieveOptions({ path: variables.path })
            .queryKey,
          context.previousValue,
        )
      }
    },
    // Always refetch after error or success.
    onSettled: (data) => {
      if (!!data) {
        // Refetch after success or error.
        invalidateSeqvarQueryPresetsSetKeys(queryClient, {
          project: data.project,
          querypresetsset: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetSet` object.
 */
export const useSeqvarQueryPresetsSetDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarQueryPresetsSetKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

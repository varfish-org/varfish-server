/**
 * Queries for seqvars query presets set versions and related powered by TanStack Query.
 */
import {
  QueryClient,
  useMutation,
  useQueries,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query'
import {
  SeqvarsApiQuerypresetssetversionUpdateData,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import {
  seqvarsApiQuerypresetssetversionCopyFromCreateMutation,
  seqvarsApiQuerypresetssetversionDestroyMutation,
  seqvarsApiQuerypresetssetversionListOptions,
  seqvarsApiQuerypresetssetversionRetrieveOptions,
  seqvarsApiQuerypresetssetversionUpdateMutation,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { deepmerge } from 'deepmerge-ts'
import { MaybeRefOrGetter, computed, toValue } from 'vue'

/**
 * Enumeration for preset set version states.
 */
export enum PresetSetVersionState {
  ACTIVE = 'active',
  DRAFT = 'draft',
  RETIRED = 'retired',
}

/**
 * Enumerations for representing that a presets version is editable or the reason
 * why it is not.
 */
export enum EditableState {
  EDITABLE,
  IS_ACTIVE,
  IS_RETIRED,
  IS_FACTORY_DEFAULT,
  IS_NOT_SET,
}

/**
 * Return user-readable string for the editable state.
 */
export const getEditableStateLabel = (state: EditableState): string => {
  let token = ''
  switch (state) {
    case EditableState.EDITABLE:
      return (
        'This preset set version is in draft state and thus editable. ' +
        'You will need to activate it to make it useable in queries.'
      )
    case EditableState.IS_FACTORY_DEFAULT:
      return (
        'This preset set version is a factory default.  You can clone ' +
        'the whole preset sets and make changes to the clone.'
      )
    case EditableState.IS_ACTIVE:
      token = 'active'
      break
    case EditableState.IS_RETIRED:
      token = 'retired'
      break
    case EditableState.IS_NOT_SET:
      return 'Preset set is currently unset.'
  }
  return (
    `This preset set version is ${token} and thus not editable. ` +
    'You need to create a new draft version, make changes there, ' +
    'and then activate it to make it useable in queries.'
  )
}

/** Helper for obtaining editable state from a presets set version. */
export const getEditableState = (
  version: SeqvarsQueryPresetsSetVersionDetails,
) => {
  if (version === undefined) {
    return EditableState.IS_NOT_SET
  } else if (version.presetsset.is_factory_default) {
    return EditableState.IS_FACTORY_DEFAULT
  } else if (version.status === PresetSetVersionState.ACTIVE) {
    return EditableState.IS_ACTIVE
  } else if (version.status === PresetSetVersionState.RETIRED) {
    return EditableState.IS_RETIRED
  } else {
    return EditableState.EDITABLE
  }
}

/**
 * Helper to invalidate query keys for lists and retrieval for a single query presets set version.
 *
 * @param queryClient Query client to use.
 * @param querypresetsset UUID of the query presets set.
 * @param querypresetssetversion UUID of the query presets set version, optional.
 * @param destroy Whether to destroy the query instead of invalidating it.
 */
export const invalidateSeqvarQueryPresetsSetVersionKeys = (
  queryClient: QueryClient,
  {
    querypresetsset,
    querypresetssetversion,
  }: {
    querypresetsset: string
    querypresetssetversion?: string
  },
  { destroy }: { destroy?: boolean } = { destroy: false },
) => {
  queryClient.invalidateQueries({
    queryKey: seqvarsApiQuerypresetssetversionListOptions({
      path: { querypresetsset },
    }).queryKey,
  })
  if (querypresetssetversion !== undefined) {
    const arg = {
      queryKey: seqvarsApiQuerypresetssetversionRetrieveOptions({
        path: {
          querypresetsset,
          querypresetssetversion,
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
 * Query for a list of seqvar query presets set versions within a presets set.
 *
 * Uses the list API of TanStack Query.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param presetsSetUuid UUID of the presets set to load presets set versions for.
 * @returns Query result with page of presets set versions.
 */
export const useSeqvarQueryPresetsSetVersionListQuery = ({
  presetsSetUuid,
}: {
  presetsSetUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiQuerypresetssetversionListOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { querypresetsset: () => toValue(presetsSetUuid)! },
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      query: () => ({
        page: 1,
        page_size: 100,
      }),
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(presetsSetUuid),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    getNextPageParam: (lastPage) => lastPage.next,
  })
}

/**
 * Query for a single seqvar query presets set details within a presets set.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param presetsSetUuid UUID of the presets set that contains the presets set version.
 * @param presetsSetVersionUuid UUID of the seqvar presets set version to load.
 */
export const useSeqvarQueryPresetsSetVersionRetrieveQuery = ({
  presetsSetUuid,
  presetsSetVersionUuid,
}: {
  presetsSetUuid: MaybeRefOrGetter<string | undefined>
  presetsSetVersionUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...seqvarsApiQuerypresetssetversionRetrieveOptions({
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetsset: () => toValue(presetsSetUuid)!,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        querypresetssetversion: () => toValue(presetsSetVersionUuid)!,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () =>
      !!toValue(presetsSetUuid) && !!toValue(presetsSetVersionUuid),
  })

/**
 * Query for a list of seqvar query presets set versions within a presets set.
 *
 * @param presetsSetUuid UUID of the presets set to load versions for.
 * @param presetsSetVersionUuids UUIDs of the seqvar querie version to load.
 * @returns Query result with page of presets set versions.
 */
export const useSeqvarQueryPresetsSetVersionRetrieveQueries = ({
  presetsSetUuid,
  presetsSetVersionUuids,
}: {
  presetsSetUuid: MaybeRefOrGetter<string | undefined>
  presetsSetVersionUuids: MaybeRefOrGetter<string[] | undefined>
}) =>
  useQueries({
    queries: computed(() =>
      (toValue(presetsSetVersionUuids) ?? []).map(
        (seqvarQueryPresetsSetUuid) => ({
          ...seqvarsApiQuerypresetssetversionRetrieveOptions({
            path: {
              querypresetsset: toValue(presetsSetUuid)!,
              querypresetssetversion: seqvarQueryPresetsSetUuid,
            },
          }),
          enabled: () =>
            !!toValue(presetsSetUuid) &&
            !!toValue(seqvarQueryPresetsSetUuid)?.length,
        }),
      ),
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

/**
 * Mutation for the copying a `SeqvarsQueryPresetSetVersion` object.
 */
export const useSeqvarQueryPresetsSetCopyFromMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetversionCopyFromCreateMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, context.path)
    },
  })
}

/**
 * Mutation for updating a `SeqvarsQueryPresetSetVersion` object.
 */
export const useSeqvarQueryPresetsSetVersionUpdateMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetversionUpdateMutation(),
    // Perform optimistic updates but prepare rollback by snapshotting the data.
    onMutate: async (data: SeqvarsApiQuerypresetssetversionUpdateData) => {
      // Cancel any outgoing refetches to prevent optimistic updates.
      const queryKey = seqvarsApiQuerypresetssetversionRetrieveOptions({
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
              data.body as SeqvarsQueryPresetsSetVersionDetails,
            )
      queryClient.setQueryData(queryKey, newValue)
      // Return a context with the previous and new data.
      return { previousValue, newValue }
    },
    // If the mutation fails, rollback with context we returned above.
    onError: (_err, variables, context) => {
      if (!!context?.previousValue) {
        queryClient.setQueryData(
          seqvarsApiQuerypresetssetversionRetrieveOptions({
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
        invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
          querypresetsset: data.presetsset,
          querypresetssetversion: data.sodar_uuid,
        })
      }
    },
  })
}

/**
 * Mutation for the deletion of a `SeqvarsQueryPresetSetVersion` object.
 */
export const useSeqvarQueryPresetsSetVersionDestroyMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    ...seqvarsApiQuerypresetssetversionDestroyMutation(),
    onSettled: (_data, _variables, context) => {
      // Refetch after success or error.
      invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, context.path, {
        destroy: true,
      })
    },
  })
}

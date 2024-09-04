/**
 * Queries for seqvars result sets and related powered by TanStack Query.
 */
import { useQueries, useQuery } from '@tanstack/vue-query'
import {
  seqvarsApiResultrowListOptions,
  seqvarsApiResultrowRetrieveOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, computed, toValue } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Type for ordering query results. */
export type OrderDir = 'asc' | 'desc'

/**
 * Query for a list of rows within a seqvar result set.
 *
 * @param resultSetUuid UUID of the result set to load rows for.
 * @param page page to use.
 * @param pageSize Number of rows to query per page.
 * @param orderBy Field to order by.
 * @param orderDir Direction to order by.
 * @returns Query result with page of cases.
 */
export const useResultRowListQuery = (
  options: MaybeRefOrGetter<{
    resultSetUuid: MaybeRefOrGetter<string | undefined>
    page: MaybeRefOrGetter<number | undefined>
    pageSize: MaybeRefOrGetter<number>
    orderBy: MaybeRefOrGetter<string | undefined>
    orderDir: MaybeRefOrGetter<OrderDir | undefined>
  }>,
) => {
  const { resultSetUuid, page, pageSize, orderBy, orderDir } = toValue(options)
  return useQuery({
    ...seqvarsApiResultrowListOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        resultset: () => toValue(resultSetUuid)!,
      },
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      query: () => ({
        page: toValue(page),
        page_size: toValue(pageSize),
        order_by: toValue(orderBy) ?? 'name',
        order_dir: toValue(orderDir) ?? 'asc',
      }),
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(resultSetUuid),
  })
}

/**
 * Query for a single seqvar result set details within a seqvar result set.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param resultSetUuid UUID of the seqvar result set that contains the execution.
 * @param resultRowUuid UUID of the seqvar result row to load.
 */
export const useSeqvarResultRowRetrieveQuery = ({
  resultSetUuid,
  resultRowUuid,
}: {
  resultSetUuid: MaybeRefOrGetter<string | undefined>
  resultRowUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...seqvarsApiResultrowRetrieveOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        resultset: () => toValue(resultSetUuid),
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        seqvarresultrow: () => toValue(resultRowUuid)!,
      },
    }),
    enabled: () => !!toValue(resultSetUuid) && !!toValue(resultRowUuid),
  })
}

/**
 * Query for a list of seqvar result rows within a case analysis session.
 *
 * @param resultSetUuid UUID of the seqvar result set to load rows for.
 * @param resultRowUuids UUIDs of the seqvar result rows to load.
 * @returns Query result with page of seqvars result rows.
 */
export const useSeqvarResultRowRetrieveQueries = ({
  resultSetUuid,
  resultRowUuids,
}: {
  resultSetUuid: MaybeRefOrGetter<string | undefined>
  resultRowUuids: MaybeRefOrGetter<string[] | undefined>
}) =>
  useQueries({
    queries: computed(() =>
      (toValue(resultRowUuids) ?? []).map((seqvarResultRowUuid) => ({
        ...seqvarsApiResultrowRetrieveOptions({
          client,
          path: {
            resultset: toValue(resultSetUuid)!,
            seqvarresultrow: seqvarResultRowUuid,
          },
        }),
        enabled: () =>
          !!toValue(resultSetUuid) && !!toValue(resultRowUuids)?.length,
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

/**
 * Queries for cases (list, details, count) powered by TanStack Query
 */
import { useQuery } from '@tanstack/vue-query'
import {
  casesApiCaseCountRetrieveOptions,
  casesApiCaseListListOptions,
  casesApiCaseRetrieveUpdateDestroyRetrieveOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, toValue } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Type for ordering query results. */
export type OrderDir = 'asc' | 'desc'

/**
 * Query for a list of cases within a project.
 *
 * @param projectUuid UUID of the project to query cases for.
 * @param queryString Query string to filter cases by.
 * @param page Page number to query.
 * @param pageSize Number of cases to query per page.
 * @param orderBy Field to order by.
 * @param orderDir Direction to order by.
 * @returns Query result with page of cases.
 */
export const useCaseListQuery = ({
  projectUuid,
  queryString,
  page,
  pageSize,
  orderBy,
  orderDir,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
  queryString: MaybeRefOrGetter<string | undefined>
  page: MaybeRefOrGetter<number>
  pageSize: MaybeRefOrGetter<number>
  orderBy: MaybeRefOrGetter<string | undefined>
  orderDir: MaybeRefOrGetter<OrderDir | undefined>
}) => {
  return useQuery({
    ...casesApiCaseListListOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        project: () => toValue(projectUuid)!,
      },
      query: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        page: page,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        page_size: pageSize,
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        order_by: () => toValue(orderBy) ?? 'name',
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        order_dir: () => toValue(orderDir) ?? 'asc',
        q: toValue(queryString),
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(projectUuid),
  })
}

/**
 * Query for the number of cases within a project.
 *
 * @param projectUuid UUID of the project to query cases for.
 * @param queryString Query string to filter cases by.
 * @returns Query result with number of cases.
 */
export const useCaseCountQuery = ({
  projectUuid,
  queryString,
}: {
  projectUuid: MaybeRefOrGetter<string | undefined>
  queryString: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...casesApiCaseCountRetrieveOptions({
      client,
      path: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        project: () => toValue(projectUuid)!,
      },
      query: {
        // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
        q: queryString,
      },
    }),
    enabled: () => !!toValue(projectUuid),
  })

export const useCaseRetrieveQuery = ({
  caseUuid,
}: {
  caseUuid: MaybeRefOrGetter<string | undefined>
}) =>
  useQuery({
    ...casesApiCaseRetrieveUpdateDestroyRetrieveOptions({
      client,
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { case: () => toValue(caseUuid)! },
    }),
    enabled: () => !!toValue(caseUuid),
  })

/**
 * Queries for cases (list, details, count) powered by TanStack Query
 */
import { UseQueryReturnType, useQuery } from '@tanstack/vue-query'
import {
  CasesApiCaseCountRetrieveResponse,
  CasesApiCaseListListResponse,
} from '@varfish-org/varfish-api/lib'
import {
  casesApiCaseCountRetrieveOptions,
  casesApiCaseListListOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { ComputedRef, Ref, computed } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Type for ordering query results. */
export type OrderDir = 'asc' | 'desc'
/** Union type for Vue3 `ref()` or `computed()` result. */
export type RefOrComputed<T> = Ref<T> | ComputedRef<T>

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
  projectUuid: RefOrComputed<string | undefined>
  queryString: RefOrComputed<string | undefined>
  page: RefOrComputed<number>
  pageSize: RefOrComputed<number>
  orderBy: RefOrComputed<string | undefined>
  orderDir: RefOrComputed<OrderDir | undefined>
}): UseQueryReturnType<CasesApiCaseListListResponse, Error> => {
  return useQuery(
    computed(() => ({
      ...casesApiCaseListListOptions({
        client,
        path: {
          project: projectUuid.value!,
        },
        query: {
          page: page.value,
          page_size: pageSize.value,
          order_by: orderBy.value ?? 'name',
          order_dir: orderDir.value ?? 'asc',
          q: queryString.value,
        },
      }),
      enabled: !!projectUuid.value,
    })),
  )
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
  projectUuid: RefOrComputed<string | undefined>
  queryString: RefOrComputed<string | undefined>
}): UseQueryReturnType<CasesApiCaseCountRetrieveResponse, Error> =>
  useQuery(
    computed(() => {
      return {
        ...casesApiCaseCountRetrieveOptions({
          client,
          path: {
            project: projectUuid.value!,
          },
          query: {
            q: queryString.value,
          },
        }),
        enabled: !!projectUuid.value,
      }
    }),
  )

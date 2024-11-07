/**
 * Queries for case analysies powered by TanStack Query.
 */
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import {
  casesAnalysisApiCaseanalysisListInfiniteOptions,
  casesAnalysisApiCaseanalysisListOptions,
} from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Query for a list case analysis objects of a given page.
 *
 * Uses the list API of TanStack Query and query for 100 items for now as the infinite
 * query API breaks the TanStack Query devtools plugin.
 *
 * @param caseUuid UUID of the case to query analyses for.
 * @returns Query result with page of case analyses.
 */
export const useCaseAnalysisListQuery = ({
  caseUuid,
}: {
  caseUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useQuery({
    ...casesAnalysisApiCaseanalysisListOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { case: () => toValue(caseUuid)! },
      query: {
        page: 1,
        page_size: 100,
      },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(caseUuid),
  })
}

/**
 * Query for a list case analysis objects of a given page.
 *
 * @param caseUuid UUID of the case to query analyses for.
 * @returns Query result with page of case analyses.
 */
export const useCaseAnalysisInfiniteListQuery = ({
  caseUuid,
}: {
  caseUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useInfiniteQuery({
    ...casesAnalysisApiCaseanalysisListInfiniteOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { case: () => toValue(caseUuid)! },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(caseUuid),
    getNextPageParam: (lastPage) => lastPage.next,
  })
}

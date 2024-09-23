/**
 * Queries for case analysies powered by TanStack Query.
 */
import { useInfiniteQuery } from '@tanstack/vue-query'
import { casesAnalysisApiCaseanalysissessionListInfiniteOptions } from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { MaybeRefOrGetter, toValue } from 'vue'

/**
 * Query for a list case analysis session objects of a given page.
 *
 * @param caseUuid UUID of the case to query sessions for.
 * @returns Query result with page of case analyses.
 */
export const useCaseAnalysisSessionListQuery = ({
  caseUuid,
}: {
  caseUuid: MaybeRefOrGetter<string | undefined>
}) => {
  return useInfiniteQuery({
    ...casesAnalysisApiCaseanalysissessionListInfiniteOptions({
      // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
      path: { case: () => toValue(caseUuid)! },
    }),
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    enabled: () => !!toValue(caseUuid),
    getNextPageParam: (lastPage) => lastPage.next ?? undefined,
  })
}

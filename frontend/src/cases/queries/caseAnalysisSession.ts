/**
 * Queries for case analysies powered by TanStack Query.
 */
import { UseQueryReturnType, useQuery } from '@tanstack/vue-query'
import { CasesAnalysisApiCaseanalysissessionListResponse } from '@varfish-org/varfish-api/lib'
import { casesAnalysisApiCaseanalysissessionListOptions } from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { ComputedRef, Ref, computed } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Union type for Vue3 `ref()` or `computed()` result. */
export type RefOrComputed<T> = Ref<T> | ComputedRef<T>

/**
 * Query for a list case analysis session objects of a given page.
 *
 * NB: the interface is paginated and we only load the first page assuming
 * there are fewer than 100 sessions (there can only be one atm).
 *
 * @param caseUuid UUID of the case to query sessions for.
 * @returns Query result with page of case analyses.
 */
export const useCaseAnalysisSessionListQuery = ({
  caseUuid,
}: {
  caseUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<
  CasesAnalysisApiCaseanalysissessionListResponse,
  Error
> => {
  return useQuery(
    computed(() => ({
      ...casesAnalysisApiCaseanalysissessionListOptions({
        client,
        path: { case: caseUuid.value! },
        query: {
          cursor: undefined,
          page_size: 100,
        },
      }),
      enabled: !!caseUuid.value,
    })),
  )
}

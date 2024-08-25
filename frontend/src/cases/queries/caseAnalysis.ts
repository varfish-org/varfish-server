/**
 * Queries for case analysies powered by TanStack Query.
 */
import { UseQueryReturnType, useQuery } from '@tanstack/vue-query'
import { CasesAnalysisApiCaseanalysisListResponse } from '@varfish-org/varfish-api/lib'
import { casesAnalysisApiCaseanalysisListOptions } from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { ComputedRef, Ref, computed } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Union type for Vue3 `ref()` or `computed()` result. */
export type RefOrComputed<T> = Ref<T> | ComputedRef<T>

/**
 * Query for a list case analysis objects of a given page.
 *
 * NB: the interface is paginated and we only load the first page assuming
 * there are fewer than 100 analyses (there can only be one atm).
 *
 * @param caseUuid UUID of the case to query analyses for.
 * @returns Query result with page of case analyses.
 */
export const useCaseAnalysisListQuery = ({
  caseUuid,
}: {
  caseUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<CasesAnalysisApiCaseanalysisListResponse, Error> => {
  return useQuery(
    computed(() => ({
      ...casesAnalysisApiCaseanalysisListOptions({
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

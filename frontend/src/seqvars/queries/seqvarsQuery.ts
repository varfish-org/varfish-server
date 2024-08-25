/**
 * Queries for case queries and related powered by TanStack Query.
 */
import { UseQueryReturnType, useQuery } from '@tanstack/vue-query'
import { CasesAnalysisApiCaseanalysissessionListResponse, SeqvarsApiQueryListResponse, SeqvarsApiQueryRetrieveResponse } from '@varfish-org/varfish-api/lib'
import { casesAnalysisApiCaseanalysissessionListOptions } from '@varfish-org/varfish-api/lib/@tanstack/vue-query.gen'
import { ComputedRef, Ref, computed } from 'vue'

import { client } from '@/cases/plugins/heyApi'

/** Union type for Vue3 `ref()` or `computed()` result. */
export type RefOrComputed<T> = Ref<T> | ComputedRef<T>

/**
 * Query for a list of seqvar queries within a case analysis session.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * NB: the interface is paginated and we only load the first page assuming
 * there are fewer than 100 sessions (there can only be one atm).
 *
 * @param sessionUuid UUID of the case analysis session to load queries for.
 * @returns Query result with page of seqvars queries.
 */
export const useSeqvarQueryListQuery = ({
  sessionUuid,
}: {
  sessionUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<
  SeqvarsApiQueryListResponse,
  Error
> => {
  throw new Error('Not implemented')
}

/**
 * Query for a single seqvar query details within a case analysis session.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param sessionUuid
 *    UUID of the case analysis session that contains the seqvar query.
 * @param seqvarQueryUuid UUID of the seqvar query to load.
 */
export const useSeqvarQueryRetrieveQuery = ({
  sessionUuid,
  seqvarQueryUuid,
}: {
  sessionUuid: RefOrComputed<string | undefined>
  seqvarQueryUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<
  SeqvarsApiQueryRetrieveResponse,
  Error
  > => {
  throw new Error('Not implemented')
}

/**
 * Query for a list of seqvar query executions within a seqvar query.
 *
 * The objects returned when listed are fairly flat and contain UUIDs to
 * related objects.
 *
 * @param queryUuid UUID of the seqvar query to load executions for.
 * @returns Query result with page of seqvar query executions.
 */
export const useSeqvarQueryExecutionListQuery = ({
  queryUuid
}: {
  queryUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<
  CasesAnalysisApiCaseanalysissessionListResponse,
  Error
  > => {
  throw new Error('Not implemented')
}

/**
 * Query for a single seqvar query execution details within a seqvar query.
 *
 * The objects returned when retrieved are more nested and contain the actual
 * data.
 *
 * @param queryUuid UUID of the seqvar query that contains the execution.
 * @param executionUuid UUID of the seqvar query execution to load.
 */
export const useSeqvarQueryExecutionRetrieveQuery = ({
  queryUuid,
  executionUuid
}: {
  queryUuid: RefOrComputed<string | undefined>
  executionUuid: RefOrComputed<string | undefined>
}): UseQueryReturnType<
  CasesAnalysisApiCaseanalysissessionListResponse,
  Error
  > => {
  throw new Error('Not implemented')
}

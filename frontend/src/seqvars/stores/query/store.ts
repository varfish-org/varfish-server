import {
  SeqvarsQueryColumnsConfig,
  SeqvarsQueryDetails,
  SeqvarsQueryDetailsRequest,
  SeqvarsQueryExecution,
  SeqvarsService,
} from '@varfish-org/varfish-api/lib'
import { acceptHMRUpdate, defineStore } from 'pinia'
import { reactive, ref, toRaw } from 'vue'

import { client } from '@/cases/plugins/heyApi'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { State, StoreState } from '@/varfish/storeUtils'

/**
 * Store for the seqvars queries.
 */
export const useSeqvarsQueryStore = defineStore('seqvarsQuery', () => {
  const seqvarPresetsStore = useSeqvarsPresetsStore()

  /** The current store state. */
  const storeState = reactive<StoreState>(new StoreState())

  /** The UUID of the project for the presets. */
  const projectUuid = ref<string | undefined>(undefined)
  /** The UUID of the current case. */
  const caseUuid = ref<string | undefined>(undefined)
  /** The UUID of the case analysis. */
  const analysisUuid = ref<string | undefined>(undefined)
  /** The UUID of the case analysis session. */
  const sessionUuid = ref<string | undefined>(undefined)
  /** The UUID of the current query presets. */
  const queryPresetsVersionUuid = ref<string | undefined>(undefined)

  /** The seqvar queries by UUID. */
  const seqvarQueries = reactive<Map<string, SeqvarsQueryDetails>>(new Map())
  /** The seqvar query columns configuration by UUID. */
  const seqvarQueryColumnsConfigs = reactive<
    Map<string, SeqvarsQueryColumnsConfig>
  >(new Map())
  /** The seqvars queries by UUID. */
  const seqvarsQueries = reactive<Map<string, SeqvarsQueryDetails>>(new Map())
  /** The seqvars query executions by UUID. */
  const seqvarsQueryExecutions = reactive<Map<string, SeqvarsQueryExecution>>(
    new Map(),
  )

  /**
   * Initialize the store.
   *
   */
  const initialize = async (
    projectUuid$: string,
    caseUuid$: string,
    analysisUuid$: string,
    sessionUuid$: string,
    queryPresetsVersionUuid$: string,
    forceReload$: boolean = false,
  ) => {
    // Do not reinitialize if the project is the same unless forced.
    if (
      projectUuid$ === projectUuid.value &&
      caseUuid$ === caseUuid.value &&
      analysisUuid$ === analysisUuid.value &&
      sessionUuid$ === sessionUuid.value &&
      queryPresetsVersionUuid$ === queryPresetsVersionUuid.value &&
      !forceReload$
    ) {
      return
    }

    $reset()
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$
    analysisUuid.value = analysisUuid$
    sessionUuid.value = sessionUuid$
    queryPresetsVersionUuid.value = queryPresetsVersionUuid$

    storeState.state = State.Fetching
    await Promise.all([
      seqvarPresetsStore.initialize(projectUuid$, forceReload$),
      (async () => {
        await loadSeqvarQueries()
        await loadSeqvarQueryExecutions()
      })(),
    ])
    try {
      storeState.serverInteractions += 1
    } catch (e) {
      console.error('error', e)
      storeState.state = State.Error
      storeState.message = `Error loading presets: ${e}`
    } finally {
      storeState.serverInteractions -= 1
    }
    storeState.state = State.Active
  }

  /**
   * Load queries, columns configs, and query settings.
   */
  const loadSeqvarQueries = async (): Promise<void> => {
    // Guard against missing initialization.
    if (sessionUuid.value === undefined) {
      throw new Error('sessionUuid is undefined')
    }
    const session = sessionUuid.value

    // Paginate through all queries.
    let cursor: string | undefined = undefined
    do {
      const response = await storeState.execAsync(
        async () =>
          await SeqvarsService.seqvarsApiQueryList({
            client,
            path: { session },
            query: { cursor, page_size: 100 },
          }),
      )
      if (response.data && response.data.results) {
        const results = response.data.results
        const responseDetails = await storeState.execAsync(
          async () =>
            await Promise.all(
              results.map((query) =>
                SeqvarsService.seqvarsApiQueryRetrieve({
                  client,
                  path: { query: query.sodar_uuid, session },
                }),
              ),
            ),
        )
        for (const responseDetail of responseDetails) {
          if (responseDetail.data) {
            seqvarQueries.set(
              responseDetail.data.sodar_uuid,
              responseDetail.data,
            )
          } else {
            throw new Error(
              `Problem fetching query details: ${responseDetail.error}`,
            )
          }
        }

        if (response.data.next) {
          const tmpCursor = new URL(response.data.next).searchParams.get(
            'cursor',
          )
          if (tmpCursor !== null) {
            cursor = tmpCursor
          }
        }
      }
    } while (cursor !== undefined)

    // Then, retrieve the query details for each query.  This will also give
    // us all column configs and query settings.
    const responses = await await storeState.execAsync(
      async () =>
        await Promise.all(
          Array.from(seqvarQueries.values()).map(({ sodar_uuid: query }) =>
            SeqvarsService.seqvarsApiQueryRetrieve({
              client,
              path: { session, query },
            }),
          ),
        ),
    )
    for (const response of responses) {
      if (response.data) {
        seqvarsQueries.set(response.data.settings.sodar_uuid, response.data)
        seqvarQueryColumnsConfigs.set(
          response.data.columnsconfig.sodar_uuid,
          response.data.columnsconfig,
        )
      }
    }
  }

  /**
   * Load the last one query executions for all queries.
   *
   * Must be called after finishing loading the queries.
   */
  const loadSeqvarQueryExecutions = async (): Promise<void> => {
    for (const seqvarQuery of seqvarQueries.values()) {
      const query = seqvarQuery.sodar_uuid
      const response = await storeState.execAsync(
        async () =>
          await SeqvarsService.seqvarsApiQueryexecutionList({
            path: { query },
            query: { page_size: 1 },
          }),
      )
      if (response.data && response.data.results) {
        for (const queryExecution of response.data.results) {
          seqvarsQueryExecutions.set(queryExecution.sodar_uuid, queryExecution)
        }
      }
    }
  }

  /**
   * Create a new seqvars query.
   *
   * This will register the query in the store and return its UUID.
   *
   * @param query The query details.
   * @returns The UUID of the new query.
   * @throws Error if there was an issue with the API call.
   */
  const createSeqvarsQuery = async (
    query: SeqvarsQueryDetailsRequest,
  ): Promise<string> => {
    if (!sessionUuid.value) {
      throw new Error('sessionUuid is undefined')
    }
    const session: string = sessionUuid.value

    const response = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQueryCreate({
        client,
        path: {
          session,
        },
        body: query,
      }),
    )
    if (!!response.data) {
      const queryUuid = response.data.sodar_uuid
      seqvarQueries.set(queryUuid, response.data)
      return queryUuid
    } else {
      throw new Error(`Problem creating query : ${response.error}`)
    }
  }

  /**
   * Copy a seqvars query from a predefined query.
   *
   * @param predefinedquery UUID of the predefined query to copy from.
   * @param label Optional label for the new query.
   * @returns The UUID of the new query.
   * @throws Error if there was an issue with the API call.
   */
  const copySeqvarsQueryFromPreset = async (
    predefinedquery: string,
    label?: string,
  ): Promise<string> => {
    if (!sessionUuid.value) {
      throw new Error('sessionUuid is undefined')
    }
    const session: string = sessionUuid.value

    const response = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQueryCreateFromCreate({
        client,
        path: {
          session,
        },
        body: {
          predefinedquery,
          label: label ?? 'NO LABEL',
        },
      }),
    )
    if (!!response.data) {
      const queryUuid = response.data.sodar_uuid
      seqvarQueries.set(queryUuid, response.data)
      return queryUuid
    } else {
      throw new Error(`Problem creating query : ${response.error}`)
    }
  }

  /**
   * Update a seqvars query.
   *
   * @param query The query details for updating.
   * @throws Error if there was an issue with the API call.
   */
  const updateSeqvarsQuery = async (
    query: SeqvarsQueryDetails,
  ): Promise<void> => {
    if (!seqvarQueries.has(query.sodar_uuid)) {
      throw new Error(`Query ${query.sodar_uuid} not found`)
    }
    if (!sessionUuid.value) {
      throw new Error('sessionUuid is undefined')
    }
    const session: string = sessionUuid.value

    // We perform an optimistic update here.
    const origQuery = structuredClone(
      toRaw(seqvarQueries.get(query.sodar_uuid))!,
    )
    seqvarQueries.set(query.sodar_uuid, query)

    const response = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQueryPartialUpdate({
        client,
        path: {
          session,
          query: query.sodar_uuid,
        },
        body: query,
      }),
    )
    if (!response.data) {
      // Revert the change on problems and throw.
      seqvarQueries.set(origQuery.sodar_uuid, origQuery)
      throw new Error(`Problem creating query : ${response.error}`)
    }
  }

  /**
   * Delete a seqvars query.
   *
   * @param query The query to delete.
   * @throws Error if there was an issue with the API call.
   */
  const deleteSeqvarsQuery = async (query: string): Promise<void> => {
    if (!sessionUuid.value) {
      throw new Error('sessionUuid is undefined')
    }
    const session: string = sessionUuid.value

    const response = await storeState.execAsync(
      async () =>
        await SeqvarsService.seqvarsApiQueryDestroy({
          client,
          path: {
            query,
            session,
          },
        }),
    )
    if (!!response.error) {
      throw new Error(`Problem deleting query : ${response.error}`)
    }
    seqvarQueries.delete(query)
  }

  /**
   * Clear the store.
   *
   * This can be useful against artifacts in the UI.
   */
  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    projectUuid.value = undefined
    caseUuid.value = undefined
    queryPresetsVersionUuid.value = undefined
  }

  return {
    // attributes
    storeState,
    projectUuid,
    caseUuid,
    analysisUuid,
    sessionUuid,
    queryPresetsUuid: queryPresetsVersionUuid,
    seqvarQueries,
    seqvarQueryColumnsConfigs,
    seqvarsQuerySettings: seqvarsQueries,
    seqvarsQueryExecutions,
    // methods
    initialize,
    createSeqvarsQuery,
    copySeqvarsQueryFromPreset,
    updateSeqvarsQuery,
    deleteSeqvarsQuery,
    $reset,
  }
})

// Enable HMR (Hot Module Replacement)
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useSeqvarsQueryStore, import.meta.hot))
}

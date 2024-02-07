/**
 * NB: this is one of the few stores that don't have an initializeRes on purpose.
 */

import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { SvClient } from '@svs/api/svClient'
import { useSvResultSetStore } from '@svs/stores/svResultSet'
import { State, StoreState } from '@varfish/storeUtils'
import { apiQueryStateToQueryState, QueryStates } from '@variants/enums'
import { copy } from '@variants/helpers'
import camelCase from 'camelcase'
import { defineStore } from 'pinia'
import { nextTick, reactive, ref } from 'vue'

/** Helper that fetches the presets and stores them in quickPresets.value and categoryPresets.value
 */
const fetchPresets = async (
  csrfToken,
  caseObj,
  quickPresets,
  categoryPresets,
) => {
  const svClient = new SvClient(csrfToken)
  // TODO: move fetch calls into QueryPresetsClient
  const fetchFactoryPresets = async () => {
    await Promise.all(
      [
        svClient.fetchQuickPresets().then((presets) => {
          quickPresets.value = presets
        }),
        svClient.fetchInheritancePresets(caseObj.sodar_uuid).then((presets) => {
          categoryPresets.value.inheritance = presets
        }),
      ] +
        [
          'genotype_criteria',
          'frequency',
          'impact',
          'sv_type',
          'chromosomes',
          'regulatory',
          'tad',
          'known_patho',
        ].map((category) => {
          svClient.fetchCategoryPresets(category).then((presets) => {
            categoryPresets.value[camelCase(category)] = presets
          })
        }),
    )
  }

  // TODO: allow for fetching user presets

  await fetchFactoryPresets()
}

/** Helper that gets the default settings and stores them in querySettingsPresets.value,
 * and querySettings.value.
 */
const fetchDefaultSettings = async (
  csrfToken,
  caseUuid,
  querySettingsPresets,
  querySettings,
) => {
  const svClient = new SvClient(csrfToken)
  const resJson = await svClient.retrieveQuerySettingsShortcut(caseUuid)
  querySettingsPresets.value = resJson.presets
  querySettings.value = resJson.query_settings
  // if (querySettings.value.prio_enabled === undefined) {
  //   querySettings.value.prio_enabled = false
  // }
  // if (querySettings.value.prio_algorithm === undefined) {
  //   querySettings.value.prio_algorithm = 'hiphive-human'
  // }
  // if (querySettings.value.prio_hpo_terms === undefined) {
  //   querySettings.value.prio_hpo_terms = []
  // }
  // if (querySettings.value.patho_enabled === undefined) {
  //   querySettings.value.patho_enabled = false
  // }
  // if (querySettings.value.patho_score === undefined) {
  //   querySettings.value.patho_score = 'mutationtaster'
  // }
  // if (querySettings.value.prio_enabled === undefined) {
  //   querySettings.value.prio_enabled = false
  // }
}

/** Helper that fetches the previous query UUID.
 */
const fetchPreviousQueryUuid = async (csrfToken, caseUuid) => {
  const svClient = new SvClient(csrfToken)
  const prevQueries = await svClient.listSvQuery(caseUuid)
  if (prevQueries.length) {
    return prevQueries[0].sodar_uuid
  } else {
    return null
  }
}

const FETCH_LOOP_DELAY = 1000 // 1 second
const FETCH_LOOP_ALLOW_FAILURES = 10 // up to 10 failures

export const useSvQueryStore = defineStore('svQuery', () => {
  // store dependencies

  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()
  /** The variantResultSet store */
  const svResultSetStore = useSvResultSetStore()

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref(null)
  /** UUID of the project.  */
  const projectUuid = ref(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref(null)
  /** The current application state. */
  const storeState = reactive(new StoreState())

  // other data

  // UI settings
  /** Whether to show the filtration inline help in UI. */
  const showFiltrationInlineHelp = ref(false)
  /** The filtration complexity mode to use for UI. */
  const filtrationComplexityMode = ref(null)

  // loaded via API
  /** Query settings presets. */
  const querySettingsPresets = ref(null)
  /** Current query settings. */
  const querySettings = ref(null)
  /** Details from previous query. */
  const previousQueryDetails = ref(null)
  /** Uuid of query. */
  const queryUuid = ref(null)
  // bookkeeping for query and results
  /** Current query state. */
  const queryState = ref(QueryStates.None.value)
  /** Current query state message. */
  const queryStateMsg = ref(null)
  /** Query logs as fetched from API. */
  const queryLogs = ref(null)

  /** Quick presets as loaded from API. */
  const quickPresets = ref(null)
  /** Per-category presets. */
  const categoryPresets = ref({
    inheritance: null,
    genotypeCriteria: null,
    frequency: null,
    impact: null,
    svType: null,
    chromosomes: null,
    regulatory: null,
    tad: null,
    knownPatho: null,
  })

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /**
   * Start the loop for waiting for the results and fetching them.
   */
  const runFetchLoop = async (svQueryUuid, failuresSeen = 0) => {
    const svClient = new SvClient(csrfToken.value)

    // Ensure that we are still fetching and fetching results for the correct query.
    if (
      previousQueryDetails.value.sodar_uuid !== svQueryUuid ||
      ![
        QueryStates.Initial.value,
        QueryStates.Running.value,
        QueryStates.Resuming.value,
      ].includes(queryState.value)
    ) {
      return // query was cancelled or other query was started
    }

    // Fetch query status, allowing up to FETCH_LOOP_ALLOW_FAILURES errors.
    try {
      const queryStatus = await svClient.retrieveSvQuery(svQueryUuid)
      queryLogs.value = queryStatus.logs
      queryState.value = apiQueryStateToQueryState(queryStatus.query_state)
      if (queryState.value.query_state_msg) {
        queryStateMsg.value = queryState.value.query_state_msg
      }
      await nextTick()
      failuresSeen = 0 // reset failure counter
    } catch (err) {
      failuresSeen += 1
      console.warn(
        `There was a problem retrieving the query status (${failuresSeen} / ${FETCH_LOOP_ALLOW_FAILURES}`,
        err,
      )
      if (failuresSeen > FETCH_LOOP_ALLOW_FAILURES) {
        queryState.value = QueryStates.Error.value
        return // do not continue
      }
    }

    // Once query is finished, load results, if still for the same query.
    if (queryState.value === QueryStates.Finished.value) {
      queryState.value = QueryStates.Fetching.value
      await nextTick()
      await svResultSetStore.loadResultSetViaQuery(svQueryUuid)
      queryState.value = QueryStates.Fetched.value
      return // break out of loop
    }

    // Call function again via `setTimeout()`.  Loop will be broken on top of next runFetchLoop call.
    setTimeout(runFetchLoop, FETCH_LOOP_DELAY, svQueryUuid, failuresSeen)
  }

  /**
   * Submit query with current settings.
   */
  const submitQuery = async () => {
    const svClient = new SvClient(csrfToken.value)

    const convert = (key, value) => {
      if (
        key.endsWith('_count') ||
        key.endsWith('_overlap') ||
        key.endsWith('_min') ||
        key.endsWith('_max')
      ) {
        if (value !== null && value !== '' && value !== undefined) {
          const res = parseFloat(value)
          if (res === res) {
            return res
          } else {
            return value // res is NaN
          }
        }
      }
      return value
    }
    const payload = {
      query_settings: Object.fromEntries(
        Object.entries(querySettings.value).map(([key, value]) => [
          key,
          convert(key, value),
        ]),
      ),
    }
    previousQueryDetails.value = await svClient.createSvQuery(
      caseUuid.value,
      payload,
    )
    queryState.value = QueryStates.Initial.value
    await nextTick()
    runFetchLoop(previousQueryDetails.value.sodar_uuid)
  }

  /**
   * Cancel currently running query, if any.
   */
  const cancelQuery = async () => {
    queryState.value = QueryStates.Cancelled.value
  }

  /**
   * Initialize the store for the given case.
   *
   * This will fetch all information via the REST API, but only once for each state.
   *
   * This will also initialize the store dependencies.
   *
   * @param csrfToken$ CSRF token to use.
   * @param projectUuid$ UUID of the project.
   * @param caseUuid$ UUID of the case to use.
   * @param appContext An application context object with more information.
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    csrfToken$,
    projectUuid$,
    caseUuid$,
    appContext,
    forceReload = false,
  ) => {
    // Initialize store dependencies.
    await caseDetailsStore.initialize(
      csrfToken$,
      projectUuid$,
      caseUuid$,
      forceReload,
    )

    // Initialize only once for each case.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$ &&
      caseUuid.value === caseUuid$
    ) {
      return initializeRes.value
    }

    $reset() // clear to avoid artifacts

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$
    // (copy appContext values -- none at the moment)
    const _ = appContext

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const svClient = new SvClient(csrfToken.value)

    // Initialize via API.  We fetch the bare minimum information and store the
    // corresponding promise in initializeRes.  We will go on after this and
    // trigger the loading of any previous results.
    initializeRes.value = Promise.all([
      // 1. fetch default settings
      fetchDefaultSettings(
        csrfToken.value,
        caseUuid.value,
        querySettingsPresets,
        querySettings,
      ),
      // 2. fetch previous query UUID
      fetchPreviousQueryUuid(csrfToken.value, caseUuid.value)
        .then((response) => {
          if (response) {
            queryUuid.value = response
            // Retrieve query details and extract query settings.
          }
          if (queryUuid.value) {
            return svClient.retrieveSvQuery(queryUuid.value)
          }
        })
        // 2.1 once we have previous query UUID, fetch query details
        .then((result) => {
          if (result) {
            previousQueryDetails.value = result
            querySettings.value = copy(result.query_settings)
          }
        })
        // 2.2 once we have the query details, change into resuming query state and launch the fetch loop
        .then(() => {
          if (previousQueryDetails.value) {
            queryState.value = QueryStates.Resuming.value
            nextTick()
            runFetchLoop(previousQueryDetails.value.sodar_uuid)
          }
        }),
      // 3. fetch quick presets etc.
      fetchPresets(
        csrfToken.value,
        caseDetailsStore.caseObj,
        quickPresets,
        categoryPresets,
      ),
    ])
      .then(() => {
        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing filterSv store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null
    showFiltrationInlineHelp.value = false
    filtrationComplexityMode.value = null
    csrfToken.value = null
    caseUuid.value = null
    querySettingsPresets.value = null
    querySettings.value = null
    previousQueryDetails.value = null
    queryUuid.value = null
    queryState.value = QueryStates.None.value
    queryStateMsg.value = null
    queryLogs.value = null
    quickPresets.value = null
    categoryPresets.value = {
      inheritance: null,
      genotypeCriteria: null,
      frequency: null,
      impact: null,
      svType: null,
      chromosomes: null,
      regulatory: null,
      tad: null,
      knownPatho: null,
    }
    initializeRes.value = null
  }

  return {
    // data / state
    csrfToken,
    projectUuid,
    caseUuid,
    storeState,
    showFiltrationInlineHelp,
    filtrationComplexityMode,
    querySettingsPresets,
    querySettings,
    previousQueryDetails,
    queryUuid,
    queryState,
    queryStateMsg,
    queryLogs,
    quickPresets,
    categoryPresets,
    initializeRes,
    // functions
    initialize,
    submitQuery,
    cancelQuery,
  }
})

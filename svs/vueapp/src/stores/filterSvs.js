import svsApi from '@svs/api/svs.js'
import variantsApi from '@variants/api/variants.js'
import { apiQueryStateToQueryState, QueryStates } from '@variants/enums.js'
import { copy } from '@variants/helpers.js'
import camelCase from 'camelcase'
import { defineStore } from 'pinia'
import { nextTick, ref } from 'vue'

/** Constants with the used store states. */
export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

/** Helper that fetches the presets and stores them in quickPresets.value and categoryPresets.value
 */
const fetchPresets = async (
  csrfToken,
  caseObj,
  quickPresets,
  categoryPresets
) => {
  // TODO: move fetch calls into queryPresetsApi
  const fetchFactoryPresets = async () => {
    await Promise.all(
      [
        svsApi.fetchQuickPresets(csrfToken).then((presets) => {
          quickPresets.value = presets
        }),
        svsApi
          .fetchInheritancePresets(csrfToken, caseObj.sodar_uuid)
          .then((presets) => {
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
          svsApi.fetchCategoryPresets(csrfToken, category).then((presets) => {
            categoryPresets.value[camelCase(category)] = presets
          })
        })
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
  querySettings
) => {
  const resJson = await svsApi.retrieveQuerySettingsShortcut(
    csrfToken,
    caseUuid
  )
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
  const prevQueries = await svsApi.listSvQuery(csrfToken, caseUuid)
  if (prevQueries.length) {
    return prevQueries[0].sodar_uuid
  } else {
    return null
  }
}

export const useSvFilterStore = defineStore('filterSvs', () => {
  const FETCH_LOOP_DELAY = 1000 // 1 second
  const FETCH_LOOP_ALLOW_FAILURES = 10 // up to 10 failures

  // Store state and message for UI
  /** State of the store. */
  const storeState = ref(StoreState.initial)
  /** Message to display for store state, e.g., in overlay. */
  const storeStateMessage = ref('')
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  // UI settings
  /** Whether to show the filtration inline help in UI. */
  const showFiltrationInlineHelp = ref(false)
  /** The filtration complexity mode to use for UI. */
  const filtrationComplexityMode = ref(null)

  // properties from application context
  /** CSRF Token to use (from app context). */
  const csrfToken = ref(null)
  /** The case UUID (from app context). */
  const caseUuid = ref(null)

  // loaded via API
  /** The case object. */
  const caseObj = ref(null)
  /** Query settings presets. */
  const querySettingsPresets = ref(null)
  /** Current query settings. */
  const querySettings = ref(null)
  /** Details from previous query. */
  const previousQueryDetails = ref(null)
  /** Result set of query. */
  const queryResultSet = ref(null)

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

  /**
   * Start the loop for waiting for the results and fetching them.
   */
  const runFetchLoop = async (svQueryUuid, failuresSeen = 0) => {
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
      const queryStatus = await svsApi.retrieveSvQuery(
        csrfToken.value,
        svQueryUuid
      )
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
        err
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
      // List the results
      const responseResultSetList = await svsApi.listSvQueryResultSet(
        csrfToken.value,
        svQueryUuid
      )
      if (!responseResultSetList.length) {
        console.log('ERROR: no results in response')
      } else if (
        queryState.value === QueryStates.Fetching.value &&
        previousQueryDetails.value.sodar_uuid === svQueryUuid
      ) {
        // Still fetching the same query; push to query result set.
        queryResultSet.value = responseResultSetList[0]
        queryState.value = QueryStates.Fetched.value
      }
      return // break out of loop
    }

    // Call function again via `setTimeout()`.  Loop will be broken on top of next runFetchLoop call.
    setTimeout(runFetchLoop, FETCH_LOOP_DELAY, svQueryUuid, failuresSeen)
  }

  /**
   * Submit query with current settings.
   */
  const submitQuery = async () => {
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
        ])
      ),
    }
    previousQueryDetails.value = await svsApi.createSvQuery(
      csrfToken.value,
      caseUuid.value,
      payload
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

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /** Initialize the store from the appContext. */
  const initialize = async (appContext, theCaseUuid) => {
    if (storeState.value !== 'initial' && caseUuid.value === theCaseUuid) {
      // only once
      return initializeRes.value
    }
    // first reset the store to avoid artifacts
    $reset()
    storeState.value = StoreState.initializing
    storeStateMessage.value = 'Initializing...'
    serverInteractions.value += 1

    // Initialize from appContext
    caseUuid.value = theCaseUuid
    csrfToken.value = appContext.csrf_token

    // Fetch caseObj first
    caseObj.value = await variantsApi.retrieveCase(
      csrfToken.value,
      caseUuid.value
    )

    // Initialize via API.  We fetch the bare minimum information and store the
    // corresponding promise in initializeRes.  We will go on after this and
    // trigger the loading of any previous results.
    initializeRes.value = Promise.all([
      // 1. fetch default settings
      fetchDefaultSettings(
        csrfToken.value,
        caseUuid.value,
        querySettingsPresets,
        querySettings
      ),
      // 2. fetch previous query UUID
      fetchPreviousQueryUuid(csrfToken.value, caseUuid.value)
        .then((queryUuid) => {
          if (queryUuid) {
            // Retrieve query details and extract query settings.
            return svsApi.retrieveSvQuery(csrfToken.value, queryUuid)
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
        caseObj.value,
        quickPresets,
        categoryPresets
      ),
    ])
      .then(() => {
        serverInteractions.value -= 1
        storeState.value = StoreState.active
      })
      .catch((err) => {
        console.error('Problem initializing filterQuery store', err)
        serverInteractions.value -= 1
        storeState.value = StoreState.error
      })

    return initializeRes.value
  }

  const $reset = () => {
    storeState.value = StoreState.initial
    storeStateMessage.value = ''
    serverInteractions.value = 0
    showFiltrationInlineHelp.value = false
    filtrationComplexityMode.value = null
    csrfToken.value = null
    caseUuid.value = null
    caseObj.value = null
    querySettingsPresets.value = null
    querySettings.value = null
    previousQueryDetails.value = null
    queryResultSet.value = null
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
    storeState,
    storeStateMessage,
    showFiltrationInlineHelp,
    filtrationComplexityMode,
    csrfToken,
    caseUuid,
    caseObj,
    querySettingsPresets,
    querySettings,
    previousQueryDetails,
    queryResultSet,
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

import queryPresetsApi from '@variants/api/queryPresets.js'
import variantsApi from '@variants/api/variants.js'
import { apiQueryStateToQueryState, QueryStates } from '@variants/enums.js'
import { copy } from '@variants/helpers'
import { previousQueryDetailsToQuerySettings } from '@variants/stores/filterQuery.funcs.js'
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
        variantsApi.fetchQuickPresets(csrfToken).then((presets) => {
          quickPresets.value = presets
        }),
        variantsApi
          .fetchInheritancePresets(csrfToken, caseObj.sodar_uuid)
          .then((presets) => {
            categoryPresets.value.inheritance = presets
          }),
      ] +
        ['frequency', 'impact', 'quality', 'chromosomes', 'flagsetc'].map(
          (category) =>
            variantsApi.fetchCategoryPresets(csrfToken).then((presets) => {
              categoryPresets.value[category] = presets
            })
        )
    )
  }

  const fetchUserPresets = async (presetSetUuid) => {
    await Promise.all([
      queryPresetsApi
        .retrievePresetSet(csrfToken.value, presetSetUuid)
        .then((apiPresetSet) => {
          quickPresets.value = Object.fromEntries(
            apiPresetSet.quickpresets_set.map((qp) => [
              qp.sodar_uuid,
              {
                label: qp.label,
                inheritance: qp.inheritance,
                frequency: qp.frequency,
                impact: qp.impact,
                quality: qp.quality,
                chromosomes: qp.chromosome,
                flagsetc: qp.flagsetc,
                database: apiPresetSet.database,
              },
            ])
          )

          const categories = [
            'frequency',
            'impact',
            'quality',
            'chromosomes',
            'flagsetc',
          ]
          for (const category of categories) {
            const category2 =
              category === 'chromosomes' ? 'chromosome' : category
            categoryPresets.value[category] = Object.fromEntries(
              apiPresetSet[`${category2}presets_set`].map((ps) => [
                ps.sodar_uuid,
                ps,
              ])
            )
          }
        }),
      variantsApi
        .fetchInheritancePresets(csrfToken, caseObj.sodar_uuid)
        .then((presets) => {
          categoryPresets.value.inheritance = presets
        }),
    ])
  }

  if (caseObj.presetset) {
    await fetchUserPresets(caseObj.presetset)
  } else {
    await fetchFactoryPresets()
  }
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
  const resJson = await variantsApi.fetchQueryShortcuts(csrfToken, caseUuid)
  querySettingsPresets.value = resJson.presets
  querySettings.value = resJson.query_settings
  if (querySettings.value.prio_enabled === undefined) {
    querySettings.value.prio_enabled = false
  }
  if (querySettings.value.prio_algorithm === undefined) {
    querySettings.value.prio_algorithm = 'hiphive-human'
  }
  if (querySettings.value.prio_hpo_terms === undefined) {
    querySettings.value.prio_hpo_terms = []
  }
  if (querySettings.value.patho_enabled === undefined) {
    querySettings.value.patho_enabled = false
  }
  if (querySettings.value.patho_score === undefined) {
    querySettings.value.patho_score = 'mutationtaster'
  }
  if (querySettings.value.prio_enabled === undefined) {
    querySettings.value.prio_enabled = false
  }
}

/** Helper that fetches the previous query UUID.
 */
const fetchPreviousQueryUuid = async (csrfToken, caseUuid) => {
  const prevQueries = await variantsApi.fetchCaseQueries(csrfToken, caseUuid)
  if (prevQueries.length) {
    return prevQueries[0].sodar_uuid
  } else {
    return null
  }
}

/** Legacy handling code that can be removed once legacy UI has been removed.
 */
const fixupQueryPayloadForLegacy = (payload) => {
  // Handle recessive-index and recessive-parent values (must be removed).
  // TODO: this code can go away once the old HTML based UI is removed
  for (const [key, value] of Object.entries(payload.query_settings.genotype)) {
    if (value.startsWith('recessive-') || value.startsWith('comphet-')) {
      payload.query_settings.genotype[key] = null
    }
  }
  return payload
}

export const useFilterQueryStore = defineStore('filterQuery', () => {
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
  /** UMD Predictor API token (from app context). */
  const umdPredictorApiToken = ref(null)
  /** Whether HGMD Pro is enabled (from app contet). */
  const hgmdProEnabled = ref(null)
  /** The URL prefix for HGMD Pro (from app context). */
  const hgmdProPrefix = ref(null)
  /** Whether the GA4GH beacon network widget is enabled (from app context). */
  const ga4ghBeaconNetworkWidgetEnabled = ref(null)
  /** Whether exomiser support is enabled (from app context). */
  const exomiserEnabled = ref(null)
  /** Whether CADD is enabled (from app context). */
  const caddEnabled = ref(null)

  // loaded via API
  /** The case object. */
  const caseObj = ref(null)
  /** Query settings presets. */
  const querySettingsPresets = ref(null)
  /** Current query settings. */
  const querySettings = ref(null)
  /** Details from previous query. */
  const previousQueryDetails = ref(null)
  /** Results of query. */
  const queryResults = ref(null)

  // bookkeeping for query and results
  /** Current query state. */
  const queryState = ref(QueryStates.Initial.value)
  /** Query logs as fetched from API. */
  const queryLogs = ref(null)

  /** Quick presets as loaded from API. */
  const quickPresets = ref(null)
  /** Per-category presets. */
  const categoryPresets = ref({
    inheritance: null,
    frequency: null,
    impact: null,
    quality: null,
    chromosomes: null,
    flagsetc: null,
  })

  /**
   * Start the loop for waiting for the results and fetching them.
   */
  const runFetchLoop = async (queryUuid, failuresSeen = 0) => {
    // Ensure that we are still fetching and fetching results for the correct query.
    if (
      previousQueryDetails.value.sodar_uuid !== queryUuid ||
      ![QueryStates.Running.value, QueryStates.Resuming.value].includes(
        queryState.value
      )
    ) {
      return // query was cancelled or other query was started
    }

    // Fetch query status, allowing up to FETCH_LOOP_ALLOW_FAILURES errors.
    try {
      const queryStatus = await variantsApi.getQueryStatus(
        csrfToken.value,
        queryUuid
      )
      queryLogs.value = queryStatus.logs
      queryState.value = apiQueryStateToQueryState(queryStatus.status)
      nextTick()
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
      nextTick()
      const response = await variantsApi.fetchResults(
        csrfToken.value,
        queryUuid
      )
      if (
        queryState.value === QueryStates.Fetching.value &&
        previousQueryDetails.value.sodar_uuid === queryUuid
      ) {
        // Still fetching the same query; push to query results.
        queryResults.value = response
        queryState.value = QueryStates.Fetched.value
      }
    }

    // Call function again via `setTimeout()`.  Loop will be broken on top of next runFetchLoop call.
    setTimeout(runFetchLoop, FETCH_LOOP_DELAY, queryUuid, failuresSeen)
  }

  /**
   * Submit query with current settings.
   */
  const submitQuery = async () => {
    const payload = fixupQueryPayloadForLegacy({
      form_id: 'variants.small_variant_filter_form',
      form_version: 1,
      query_settings: copy(querySettings.value),
    })
    previousQueryDetails.value = await variantsApi.submitQuery(
      csrfToken.value,
      caseUuid.value,
      payload
    )
    queryState.value = QueryStates.Running.value
    nextTick()
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
  const initialize = async (appContext) => {
    if (storeState.value !== 'initial') {
      // only once
      return initializeRes.value
    }
    storeState.value = StoreState.initializing
    storeStateMessage.value = 'Initializing...'
    serverInteractions.value += 1

    // Initialize from appContext
    caseUuid.value = appContext.case_uuid
    umdPredictorApiToken.value = appContext.umd_predictor_api_token
    hgmdProEnabled.value = appContext.hgmd_pro_enabled
    hgmdProPrefix.value = appContext.hgmd_pro_prefix
    ga4ghBeaconNetworkWidgetEnabled.value =
      appContext.ga4gh_beacon_network_widget_enabled
    csrfToken.value = appContext.csrf_token
    exomiserEnabled.value = appContext.exomiser_enabled
    caddEnabled.value = appContext.cadd_enabled

    // Fetch caseObj first
    caseObj.value = await variantsApi.retrieveCase(csrfToken, caseUuid.value)

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
            return variantsApi.retrieveQueryDetails(csrfToken.value, queryUuid)
          }
        })
        // 2.1 once we have previous query UUID, fetch query details
        .then((result) => {
          if (result) {
            previousQueryDetails.value = result
            querySettings.value = previousQueryDetailsToQuerySettings(
              caseObj.value,
              previousQueryDetails.value
            )
          }
        })
        // 2.2 once we have the query details, assume running state and launch the fetch loop
        .then(() => {
          queryState.value = QueryStates.Resuming.value
          nextTick()
          runFetchLoop(previousQueryDetails.value.sodar_uuid)
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
    umdPredictorApiToken,
    hgmdProEnabled,
    hgmdProPrefix,
    ga4ghBeaconNetworkWidgetEnabled,
    exomiserEnabled,
    caddEnabled,
    previousQueryDetails,
    queryResults,
    queryState,
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

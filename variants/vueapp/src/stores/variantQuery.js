import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { State, StoreState } from '@varfish/storeUtils'
import { QueryPresetsClient } from '@variants/api/queryPresetsClient'
import { VariantClient } from '@variants/api/variantClient'
import { apiQueryStateToQueryState, QueryStates } from '@variants/enums'
import { copy } from '@variants/helpers'
import { previousQueryDetailsToQuerySettings } from '@variants/stores/variantQuery.funcs'
import { useVariantResultSetStore } from '@variants/stores/variantResultSet'
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
  const variantClient = new VariantClient(csrfToken)

  // TODO: move fetch calls into QueryPresetsClient
  const fetchFactoryPresets = async () => {
    await Promise.all([
      variantClient.fetchQuickPresets().then((presets) => {
        quickPresets.value = presets
      }),
      variantClient
        .fetchInheritancePresets(caseObj.sodar_uuid)
        .then((presets) => {
          categoryPresets.value.inheritance = presets
        }),
      ...['frequency', 'impact', 'quality', 'chromosomes', 'flagsetc'].map(
        (category) => {
          return variantClient
            .fetchCategoryPresets(category)
            .then((presets) => {
              categoryPresets.value[category] = presets
            })
        },
      ),
    ])
  }

  const fetchUserPresets = async (csrfToken, presetSetUuid) => {
    const queryPresetsClient = new QueryPresetsClient(csrfToken)
    await Promise.all([
      queryPresetsClient
        .retrievePresetSet(presetSetUuid)
        .then((apiPresetSet) => {
          quickPresets.value = Object.fromEntries(
            apiPresetSet.quickpresets_set.map((qp) => [
              qp.sodar_uuid,
              {
                label: qp.label,
                inheritance: qp.inheritance,
                frequency: qp.frequency,
                impact: qp.impact,
                sv_type: qp.sv_type,
                quality: qp.quality,
                chromosomes: qp.chromosome,
                flagsetc: qp.flagsetc,
                database: apiPresetSet.database,
              },
            ]),
          )

          const categories = [
            'frequency',
            'impact',
            'sv_type',
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
              ]),
            )
          }
        }),
      variantClient
        .fetchInheritancePresets(caseObj.sodar_uuid)
        .then((presets) => {
          categoryPresets.value.inheritance = presets
        }),
    ])
  }

  if (caseObj.presetset) {
    await fetchUserPresets(csrfToken.value, caseObj.presetset)
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
  querySettings,
) => {
  const variantClient = new VariantClient(csrfToken)
  const resJson = await variantClient.fetchQueryShortcuts(caseUuid)
  querySettingsPresets.value = resJson.presets
  querySettings.value = resJson.query_settings
  if (querySettings.value.prio_enabled === undefined) {
    querySettings.value.prio_enabled = false
  }
  if (querySettings.value.gm_enabled === undefined) {
    querySettings.value.gm_enabled = false
  }
  if (querySettings.value.pedia_enabled === undefined) {
    querySettings.value.pedia_enabled = false
  }
  if (querySettings.value.prio_algorithm === undefined) {
    querySettings.value.prio_algorithm = 'hiphive-human'
  }
  if (querySettings.value.prio_gm === undefined) {
    querySettings.value.prio_gm = ''
  }
  if (querySettings.value.photo_file === undefined) {
    querySettings.value.photo_file = ''
  }
  if (querySettings.value.prio_hpo_terms === undefined) {
    querySettings.value.prio_hpo_terms = []
  }
  if (querySettings.value.patho_enabled === undefined) {
    querySettings.value.patho_enabled = false
  }
  if (querySettings.value.patho_score === undefined) {
    querySettings.value.patho_score = 'cadd'
  }
}

/** Helper that fetches the previous query UUID.
 */
const fetchPreviousQueryUuid = async (csrfToken, caseUuid) => {
  const variantClient = new VariantClient(csrfToken)
  const prevQueries = await variantClient.fetchCaseQueries(caseUuid)
  if (prevQueries.length) {
    return prevQueries[0].sodar_uuid
  } else {
    return null
  }
}

/** Helper that fetches extra anno fields.
 */
const fetchExtraAnnoFields = async (csrfToken) => {
  const variantClient = new VariantClient(csrfToken)
  return await variantClient.fetchExtraAnnoFields()
}

/** Helper that fetches the HPO terms.
 */
const fetchHpoTerms = async (csrfToken, hpoTerms) => {
  const variantClient = new VariantClient(csrfToken)
  const _hpoNames = []
  for (const hpoTerm of hpoTerms) {
    await variantClient.fetchHpoTerms(hpoTerm).then((res) => {
      if (res.length === 0) {
        console.warn("No term for HPO ID '" + hpoTerm + "' found")
      } else {
        if (res.length > 1) {
          console.warn(
            "Multiple terms for HPO ID '" +
              hpoTerm +
              "' found. Taking first one.",
          )
        }
        _hpoNames.push(res[0].name)
      }
    })
  }
  return _hpoNames
}

const FETCH_LOOP_DELAY = 1000 // 1 second
const FETCH_LOOP_ALLOW_FAILURES = 10 // up to 10 failures

export const useVariantQueryStore = defineStore('variantQuery', () => {
  // store dependencies

  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()
  /** The variantResultSet store */
  const variantResultSetStore = useVariantResultSetStore()

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

  // more properties from application context
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
  /** Whether CADA is enabled (from app context). */
  const cadaEnabled = ref(null)
  /** Whether GestaltMatcher prioritization is enabled (from app context). */
  const gmEnabled = ref(null)
  /** Whether PEDIA prioritization is enabled (from app context). */
  const pediaEnabled = ref(null)
  /** The response from gestaltMatcher (from app context). */
  const prioGm = ref(null)

  // loaded via API
  /** Query settings presets. */
  const querySettingsPresets = ref(null)
  /** Current query settings. */
  const querySettings = ref(null)
  /** Details from previous query. */
  const previousQueryDetails = ref(null)
  /** Uuid of query. */
  const queryUuid = ref(null)
  /** Download status TSV. */
  const downloadStatusTsv = ref(null)
  /** Download status VCF. */
  const downloadStatusVcf = ref(null)
  /** Download status XLSX. */
  const downloadStatusXlsx = ref(null)
  /** UUID of export job for TSV file. */
  const exportJobUuidTsv = ref(null)
  /** UUID of export job for VCF file. */
  const exportJobUuidVcf = ref(null)
  /** UUID of export job for XLSX file. */
  const exportJobUuidXlsx = ref(null)
  /** Extra annotation field names. */
  const extraAnnoFields = ref(null)
  /** HPO names for HPO terms from the query settings. */
  const hpoNames = ref([])

  // bookkeeping for query and results
  /** Current query state. */
  const queryState = ref(QueryStates.Initial.value)
  /** Current query state message. */
  const queryStateMsg = ref(null)
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

  /** Promise for initialization of the store. */
  const initializeRes = ref(null)

  /**
   * Start the loop for waiting for the results and fetching them.
   */
  const runFetchLoop = async (queryUuid, failuresSeen = 0) => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    // Ensure that we are still fetching and fetching results for the correct query.
    if (
      previousQueryDetails.value.sodar_uuid !== queryUuid ||
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
      const queryStatus = await variantClient.retrieveQuery(queryUuid)
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

    if (queryState.value === QueryStates.Finished.value) {
      queryState.value = QueryStates.Fetching.value
      await nextTick()
      await variantResultSetStore.loadResultSetViaQuery(queryUuid)
      queryState.value = QueryStates.Fetched.value
      return // break out of loop
    }

    // Call function again via `setTimeout()`.  Loop will be broken on top of next runFetchLoop call.
    setTimeout(runFetchLoop, FETCH_LOOP_DELAY, queryUuid, failuresSeen)
  }

  /**
   * Submit query with current settings.
   */
  const submitQuery = async () => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )
    previousQueryDetails.value = await variantClient.createQuery(
      caseUuid.value,
      { query_settings: copy(querySettings.value) },
    )
    queryState.value = QueryStates.Running.value
    downloadStatusTsv.value = null
    downloadStatusVcf.value = null
    downloadStatusXlsx.value = null
    exportJobUuidTsv.value = null
    exportJobUuidVcf.value = null
    exportJobUuidXlsx.value = null
    hpoNames.value = await fetchHpoTerms(
      csrfToken.value,
      querySettings.value.prio_hpo_terms,
    )
    queryUuid.value = previousQueryDetails.value.sodar_uuid
    await nextTick()
    await runFetchLoop(previousQueryDetails.value.sodar_uuid)
  }

  /**
   * Cancel currently running query, if any.
   */
  const cancelQuery = async () => {
    queryState.value = QueryStates.Cancelled.value
  }

  /**
   * Generate the files for download.
   */
  const generateDownloadResults = async (fileType) => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )
    await variantClient
      .generateDownloadResults(fileType, queryUuid.value)
      .then((response) => {
        if (fileType === 'tsv') {
          exportJobUuidTsv.value = response.export_job__sodar_uuid
        } else if (fileType === 'vcf') {
          exportJobUuidVcf.value = response.export_job__sodar_uuid
        } else if (fileType === 'xlsx') {
          exportJobUuidXlsx.value = response.export_job__sodar_uuid
        } else {
          return
        }
        runFetchDownloadLoop(response.export_job__sodar_uuid, fileType)
      })
  }

  /**
   * Get link to download the results file.
   */
  const serveDownloadResults = (fileType) => {
    const exportJobUuid = reactive({
      tsv: exportJobUuidTsv,
      vcf: exportJobUuidVcf,
      xlsx: exportJobUuidXlsx,
    })
    return `/variants/ajax/query-case/download/serve/${
      ref(exportJobUuid[fileType]).value
    }/`
  }

  /**
   * Get the status of the file generation job.
   */
  const getDownloadStatus = (fileType) => {
    const downloadStatus = reactive({
      tsv: downloadStatusTsv,
      vcf: downloadStatusVcf,
      xlsx: downloadStatusXlsx,
    })
    return downloadStatus[fileType]
  }

  /**
   * Start the loop for waiting for the results download.
   */
  const runFetchDownloadLoop = async (
    exportJobUuid,
    fileType,
    failuresSeen = 0,
  ) => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    // Fetch query status, allowing up to FETCH_LOOP_ALLOW_FAILURES errors.
    try {
      const response = await variantClient.statusDownloadResults(exportJobUuid)
      if (fileType === 'tsv') {
        downloadStatusTsv.value = response.status
      } else if (fileType === 'vcf') {
        downloadStatusVcf.value = response.status
      } else if (fileType === 'xlsx') {
        downloadStatusXlsx.value = response.status
      }

      if (response.status === 'failed') {
        return
      }

      await nextTick()
      failuresSeen = 0 // reset failure counter
    } catch (err) {
      failuresSeen += 1
      console.warn(
        `There was a problem retrieving the download status (${failuresSeen} / ${FETCH_LOOP_ALLOW_FAILURES}`,
        err,
      )
      if (failuresSeen > FETCH_LOOP_ALLOW_FAILURES) {
        if (fileType === 'tsv') {
          downloadStatusTsv.value = 'failed'
        } else if (fileType === 'vcf') {
          downloadStatusVcf.value = 'failed'
        } else if (fileType === 'xlsx') {
          downloadStatusXlsx.value = 'failed'
        }
        return // do not continue
      }
    }

    if (fileType === 'tsv' && downloadStatusTsv.value === 'done') {
      return
    } else if (fileType === 'vcf' && downloadStatusVcf.value === 'done') {
      return
    } else if (fileType === 'xlsx' && downloadStatusXlsx.value === 'done') {
      return
    }

    // Call function again via `setTimeout()`.  Loop will be broken on top of next runFetchLoop call.
    setTimeout(
      runFetchDownloadLoop,
      FETCH_LOOP_DELAY,
      exportJobUuid,
      fileType,
      failuresSeen,
    )
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
    // (copy appContext values)
    umdPredictorApiToken.value = appContext.umd_predictor_api_token
    hgmdProEnabled.value = appContext.hgmd_pro_enabled
    hgmdProPrefix.value = appContext.hgmd_pro_prefix
    ga4ghBeaconNetworkWidgetEnabled.value =
      appContext.ga4gh_beacon_network_widget_enabled
    exomiserEnabled.value = appContext.exomiser_enabled
    caddEnabled.value = appContext.cadd_enabled
    cadaEnabled.value = appContext.cada_enabled
    gmEnabled.value = appContext.gm_enabled
    pediaEnabled.value = appContext.pedia_enabled
    prioGm.value = appContext.prio_gm

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    // Initialize via API.  We fetch the bare minimum information and store the
    // corresponding promise in initializeRes.  We will go on after this and
    // trigger the loading of any previous results.
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

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
            // Retrieve query details and extract query settings.
            queryUuid.value = response
          }
          if (queryUuid.value) {
            return variantClient.retrieveQuery(queryUuid.value)
          }
        })
        // 2.1 once we have previous query UUID, fetch query details
        .then((result) => {
          if (result) {
            previousQueryDetails.value = result
            querySettings.value = previousQueryDetailsToQuerySettings(
              caseDetailsStore.caseObj,
              previousQueryDetails.value,
            )
          }
        })
        // 2.2 once we have the query details, assume running state and launch the fetch loop
        .then(() => {
          if (previousQueryDetails.value) {
            queryState.value = QueryStates.Resuming.value
            nextTick()
            runFetchLoop(previousQueryDetails.value.sodar_uuid)
          }
        })
        // 2.3 fetch the HPO names from the query settings for the HPO terms, if any
        .then(() => {
          if (querySettings.value?.prio_hpo_terms?.length > 0) {
            hpoNames.value = fetchHpoTerms(
              csrfToken.value,
              querySettings.value.prio_hpo_terms,
            )
          }
        }),
      // 3. fetch quick presets etc.
      fetchPresets(
        csrfToken.value,
        caseDetailsStore.caseObj,
        quickPresets,
        categoryPresets,
      ),
      // 4. fetch extra anno fields
      fetchExtraAnnoFields(csrfToken.value ?? 'undefined-csrf-token').then(
        (result) => {
          extraAnnoFields.value = result
        },
      ),
    ])
      .then(() => {
        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing filterQuery store', err)
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
    umdPredictorApiToken.value = null
    hgmdProEnabled.value = null
    hgmdProPrefix.value = null
    ga4ghBeaconNetworkWidgetEnabled.value = null
    exomiserEnabled.value = null
    caddEnabled.value = null
    cadaEnabled.value = null
    gmEnabled.value = null
    pediaEnabled.value = null
    prioGm.value = null
    querySettingsPresets.value = null
    querySettings.value = null
    previousQueryDetails.value = null
    queryUuid.value = null
    downloadStatusTsv.value = null
    downloadStatusVcf.value = null
    downloadStatusXlsx.value = null
    exportJobUuidTsv.value = null
    exportJobUuidVcf.value = null
    exportJobUuidXlsx.value = null
    extraAnnoFields.value = null
    hpoNames.value = []
    queryState.value = QueryStates.Initial.value
    queryStateMsg.value = null
    queryLogs.value = null
    quickPresets.value = null
    categoryPresets.value = {
      inheritance: null,
      frequency: null,
      impact: null,
      quality: null,
      chromosomes: null,
      flagsetc: null,
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
    umdPredictorApiToken,
    hgmdProEnabled,
    hgmdProPrefix,
    ga4ghBeaconNetworkWidgetEnabled,
    exomiserEnabled,
    caddEnabled,
    cadaEnabled,
    gmEnabled,
    pediaEnabled,
    prioGm,
    querySettingsPresets,
    querySettings,
    previousQueryDetails,
    queryUuid,
    queryState,
    queryStateMsg,
    queryLogs,
    quickPresets,
    categoryPresets,
    extraAnnoFields,
    hpoNames,
    initializeRes,
    // functions
    initialize,
    submitQuery,
    cancelQuery,
    generateDownloadResults,
    serveDownloadResults,
    getDownloadStatus,
    runFetchLoop,
    $reset,
  }
})

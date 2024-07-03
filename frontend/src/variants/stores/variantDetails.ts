import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@/varfish/storeUtils'
import { AnnonarsApiClient } from '@/varfish/api/annonars'
import { MehariApiClient } from '@/varfish/api/mehari'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCtxStore } from '@/varfish/stores/ctx'

type SmallVariant = any
type GeneInfos = any
type GeneClinvarInfos = any
type VarAnnos = any
type TxCsq = any

export const useVariantDetailsStore = defineStore('variantDetails', () => {
  // store dependencies

  /** The ctx store */
  const ctxStore = useCtxStore()
  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()

  // data passed to `initialize` and store state

  /** UUID of the project.  */
  const projectUuid = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The small variant that the previous record has been retrieved for. */
  const smallVariant = ref<SmallVariant | null>(null)
  /** Gene-related information from annonars. */
  const gene = ref<GeneInfos | null>(null)
  /** ClinVar gene-related information from annoars. */
  const geneClinvar = ref<GeneClinvarInfos | null>(null)
  /** Variant-related information from annonars. */
  const varAnnos = ref<VarAnnos | null>(null)
  /** Transcript consequence information from mehari. */
  const txCsq = ref<TxCsq[] | null>(null)

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  // functions

  /**
   * Initialize the store for the given case.
   *
   * This will fetch all information via the REST API, but only once for each state.
   *
   * This will also initialize the store dependencies.
   *
   * @param projectUuid$ UUID of the project.
   * @param caseUuid$ UUID of the case to use.
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    projectUuid$: string,
    caseUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseDetailsStore.initialize(projectUuid$, caseUuid$, forceReload)

    // Initialize only once for each case.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$ &&
      caseUuid.value === caseUuid$
    ) {
      return initializeRes.value
    }

    // Set simple properties.
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$
  }

  const fetchVariantDetails = async (smallVariant$: SmallVariant) => {
    // Prevent fetching twice.
    if (smallVariant$.sodar_uuid === smallVariant.value?.sodar_uuid) {
      return
    }

    // Clear old store contents
    smallVariant.value = null
    gene.value = null
    geneClinvar.value = null
    varAnnos.value = null
    txCsq.value = null

    // Fetch new details
    const annonarsClient = new AnnonarsApiClient(ctxStore.csrfToken)
    const mehariClient = new MehariApiClient(ctxStore.csrfToken)
    const hgncId = smallVariant$.payload.hgnc_id

    await Promise.all([
      annonarsClient.retrieveGeneInfos([hgncId]).then((result) => {
        gene.value = result[0]
      }),
      annonarsClient.retrieveGeneClinvarInfos([hgncId]).then((result) => {
        geneClinvar.value = result[0]
      }),
      annonarsClient
        .retrieveVariantAnnos(
          smallVariant$.release.toLowerCase(),
          smallVariant$.chromosome,
          smallVariant$.start,
          smallVariant$.reference,
          smallVariant$.alternative,
        )
        .then((result) => {
          varAnnos.value = result.result
        }),
      mehariClient
        .retrieveTxCsq(
          smallVariant$.release.toLowerCase(),
          smallVariant$.chromosome,
          smallVariant$.start,
          smallVariant$.reference,
          smallVariant$.alternative,
          hgncId,
        )
        .then((result) => {
          txCsq.value = result.result
        }),
    ])

    storeState.state = State.Active
    smallVariant.value = smallVariant$
  }

  return {
    // data / state
    projectUuid,
    caseUuid,
    storeState,
    gene,
    geneClinvar,
    varAnnos,
    txCsq,
    smallVariant,
    initializeRes,
    // functions
    initialize,
    fetchVariantDetails,
  }
})

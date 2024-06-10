/**
 * Pinia store for handling per-variant ACMG rating.
 */
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { SvClient, AcmgRating, strucvarEqual } from '@svs/api/strucvarClient'
import {
  LinearStrucvar,
  LinearStrucvarImpl,
  Strucvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'

export const useSvAcmgRatingStore = defineStore('svAcmgRating', () => {
  // store dependencies

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | undefined>(undefined)
  /** UUID of the project. */
  const projectUuid = ref<string | undefined>(undefined)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | undefined>(undefined)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The sequence variant that acmgRating are handled for. */
  const strucvar = ref<Strucvar | undefined>(undefined)
  /** The small variants ACMG rating as fetched from API. */
  const acmgRating = ref<AcmgRating | undefined>(undefined)
  /** The ACMG ratings for all variants of the case with the given `caseUuid`. */
  const caseAcmgRatings = ref<Map<string, AcmgRating>>(new Map())

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any>>(Promise.resolve(undefined))

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
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    csrfToken$: string,
    projectUuid$: string,
    caseUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize only once for each case.
    if (
      !forceReload &&
      storeState.state !== State.Initial &&
      projectUuid.value === projectUuid$ &&
      caseUuid.value === caseUuid$
    ) {
      return initializeRes.value
    }

    $reset()

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    // Fetch all ratings via API.
    //
    // We use thennable `initializeRes` so we can expose the Promise for the
    // initialization to the outside.
    initializeRes.value = svClient
      .listAcmgRating(caseUuid.value)
      .then((acmgRatings) => {
        caseAcmgRatings.value.clear()
        for (const acmgRating of acmgRatings) {
          caseAcmgRatings.value.set(acmgRating.sodarUuid, acmgRating)
        }

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing acmgRating store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /**
   * Select current seuence variant.
   *
   * Will re-use ACMG rating fetched previously.
   *
   * @param seqvar$ The sequence variant to select.
   * @returns Promise with the finalization results.
   * @throws Error if no ACMG rating is found for the given variant.
   */
  const setStrucvar = (strucvar$?: LinearStrucvar) => {
    strucvar.value = strucvar$
    if (strucvar$ === undefined) {
      acmgRating.value = undefined
    } else {
      for (const caseAcmgRating of caseAcmgRatings.value.values()) {
        if (strucvarEqual(caseAcmgRating, strucvar$)) {
          acmgRating.value = caseAcmgRating
          return
        }
      }
      acmgRating.value = undefined
    }
  }

  /**
   * Create a new acmgRating entry.
   */
  const createAcmgRating = async (
    strucvar: LinearStrucvar,
    payload: AcmgRating,
    resultRowUuid: string,
  ) => {
    if (!caseUuid.value) {
      throw new Error('No case UUID set')
    }
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result: AcmgRating | undefined
    try {
      result = await svClient.createAcmgRating(caseUuid.value, strucvar, {
        ...strucvar,
        ...payload,
        csrfToken: csrfToken.value,
        sodarUuid: resultRowUuid,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem creating ACMG rating for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    if (result) {
      caseAcmgRatings.value.set(result?.sodarUuid!, result)
      setStrucvar(strucvar)
    }
    return result
  }

  /**
   * Update existing acmgRating.
   */
  const updateAcmgRating = async (
    acmgRating$: AcmgRating,
  ): Promise<AcmgRating> => {
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    if (!acmgRating.value) {
      throw new Error(
        'Trying to update acmgRating with acmgRating.value being falsy',
      )
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result: AcmgRating
    try {
      result = await svClient.updateAcmgRating(
        acmgRating.value.sodarUuid!,
        acmgRating$,
      )

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem updating ACMG rating for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseAcmgRatings.value.set(result?.sodarUuid!, result)
    setStrucvar(
      new LinearStrucvarImpl(
        result.svType,
        result.genomeBuild,
        result.chrom,
        result.start,
        result.stop,
        result.copyNumber,
        result.userRepr,
      ),
    )
    return result
  }

  /**
   * Delete current acmgRating.
   */
  const deleteAcmgRating = async () => {
    if (!acmgRating.value) {
      throw new Error(
        'Trying to delete acmgRating with acmgRating.value being falsy',
      )
    }
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await svClient.deleteAcmgRating(acmgRating.value.sodarUuid!)

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem deleting ACMG rating for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseAcmgRatings.value.delete(acmgRating.value.sodarUuid!)
    acmgRating.value = undefined
  }

  /**
   * Return acmgRating for a given variant from the store.
   */
  const getAcmgRating = (variant: LinearStrucvar) => {
    for (const caseAcmgRating of caseAcmgRatings.value.values()) {
      if (strucvarEqual(caseAcmgRating, variant)) {
        return caseAcmgRating.classOverride
      }
    }
    return undefined
  }

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    csrfToken.value = undefined
    caseUuid.value = undefined
    projectUuid.value = undefined
    strucvar.value = undefined
    acmgRating.value = undefined
    caseAcmgRatings.value = new Map()
    initializeRes.value = Promise.resolve(undefined)
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    strucvar,
    acmgRating,
    caseAcmgRatings,
    initializeRes,
    // functions
    initialize,
    setStrucvar,
    createAcmgRating,
    updateAcmgRating,
    deleteAcmgRating,
    getAcmgRating,
  }
})

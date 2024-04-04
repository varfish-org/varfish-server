/**
 * Pinia store for handling per-variant flags.
 *
 * ## Store Dependencies
 *
 * - `caseDetailsStore`
 */
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { VariantClient } from '@variants/api/variantClient'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import isEqual from 'fast-deep-equal'

/** Alias definition of SmallVariantFlags type; to be defined later. */
type SmallVariantFlags = any

export const useVariantFlagsStore = defineStore('variantFlags', () => {
  // store dependencies

  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** UUID of the project.  */
  const projectUuid = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The small variant that flags are handled for. */
  const seqvar = ref<Seqvar | null>(null)
  /** For current variant: mapping from SmallVariantFlags UUID to SmallVariantFlags */
  const flags = ref<SmallVariantFlags | null>(null)
  /** For whole case: flags for all variants of the case with the given `caseUuid`. */
  const caseFlags = ref<Map<string, SmallVariantFlags>>(new Map())

  /** Template object to use for for empty flags. */
  const emptyFlagsTemplate = Object.freeze({
    flag_bookmarked: false,
    flag_incidental: false,
    flag_for_validation: false,
    flag_candidate: false,
    flag_final_causative: false,
    flag_no_disease_association: false,
    flag_segregates: false,
    flag_doesnt_segregate: false,
    flag_visual: 'empty',
    flag_molecular: 'empty',
    flag_validation: 'empty',
    flag_phenotype_match: 'empty',
    flag_summary: 'empty',
  })

  /** Template object to use for initial flags. */
  const initialFlagsTemplate = Object.freeze({
    ...emptyFlagsTemplate,
    flag_bookmarked: true,
  })

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

    $reset()

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    initializeRes.value = variantClient
      .listFlags(caseUuid.value)
      .then((flags) => {
        caseFlags.value.clear()
        for (const flag of flags) {
          caseFlags.value.set(flag.sodar_uuid, flag)
        }

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing variantFlags store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /**
   * Retrieve flags for the given variant.
   */
  const retrieveFlags = async (seqvar$: Seqvar, caseUuid$?: string) => {
    // Prevent re-retrieval of the flags.
    if (isEqual(seqvar.value, seqvar$)) {
      return
    }

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    // Throw error if case UUID has not been set.
    if (!caseUuid.value || !caseUuid$) {
      throw new Error('Case UUID not set')
    }

    flags.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      const res = await variantClient.listFlags(
        caseUuid.value ?? caseUuid$,
        seqvar$,
      )
      if (res.length) {
        flags.value = res[0]
      } else {
        flags.value = null
      }

      seqvar.value = seqvar$

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem loading flags for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }
  }

  /**
   * Create a new flags entry.
   */
  const createFlags = async (
    seqvar: Seqvar,
    payload: SmallVariantFlags,
    resultRowUuid: string,
  ): Promise<SmallVariantFlags> => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.createFlags(
        caseUuid.value ?? 'undefined-csrf-token',
        seqvar,
        {
          ...{
            release: seqvar.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
            chromosome: seqvar.chrom,
            start: seqvar.pos,
            end: seqvar.pos + seqvar.del.length - 1,
            reference: seqvar.del,
            alternative: seqvar.ins,
            sodar_uuid: resultRowUuid,
          },
          ...payload,
        },
      )

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem creating flags for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseFlags.value.set(result.sodar_uuid, result)
    flags.value = result

    return result
  }

  /**
   * Update existing flags.
   */
  const updateFlags = async (
    payload: SmallVariantFlags,
  ): Promise<SmallVariantFlags> => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    if (!flags.value) {
      console.warn('Trying to update flags with flags.value being falsy')
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.updateFlags(flags.value.sodar_uuid, {
        ...seqvar,
        ...payload,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem updating flags for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseFlags.value.set(result.sodar_uuid, result)
    flags.value = result

    return result
  }

  /**
   * Delete current flags.
   */
  const deleteFlags = async () => {
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    if (!flags.value) {
      console.warn('Trying to delete flags with flags.value being falsy')
      return
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await variantClient.deleteFlags(flags.value.sodar_uuid)

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem deleting flags for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseFlags.value.delete(flags.value.sodar_uuid)
    flags.value = null
  }

  /**
   * Return flags for a given variant from the store.
   */
  const getFlags = (variant: Seqvar): SmallVariantFlags | null => {
    for (const flag of caseFlags.value.values()) {
      if (
        flag.release.toLowerCase() === variant.genomeBuild &&
        flag.chromosome === variant.chrom &&
        flag.start === variant.pos &&
        flag.reference === variant.del &&
        flag.alternative === variant.ins
      ) {
        return flag
      }
    }
    return null
  }

  const flagAsArtifact = async (variant: Seqvar, resultRowUuid: string) => {
    await retrieveFlags(variant)
    if (flags.value) {
      // update existing flags
      await updateFlags({
        ...flags.value,
        flag_summary: 'negative',
        flag_visual: 'negative',
      })
    } else {
      // create new flags
      await createFlags(
        variant,
        {
          ...emptyFlagsTemplate,
          flag_summary: 'negative',
          flag_visual: 'negative',
        },
        resultRowUuid,
      )
    }
  }

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    csrfToken.value = null
    caseUuid.value = null
    projectUuid.value = null
    seqvar.value = null
    flags.value = null
    caseFlags.value = new Map()
    initializeRes.value = null
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    seqvar,
    flags,
    caseFlags,
    emptyFlagsTemplate,
    initialFlagsTemplate,
    initializeRes,
    // functions
    initialize,
    retrieveFlags,
    createFlags,
    updateFlags,
    deleteFlags,
    getFlags,
    flagAsArtifact,
  }
})

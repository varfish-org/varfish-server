/**
 * Pinia store for handling per-SV flags.
 */
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'
import { SvClient } from '@svs/api/strucvarClient'
import { bndInsOverlap, reciprocalOverlap } from '@varfish/helpers'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import isEqual from 'fast-deep-equal'

/** Alias definition of StructuralVariant type; to be defined later. */
type StructuralVariant = any
/** Alias definition of StructuralVariantFlags type; to be defined later. */
type StructuralVariantFlags = any

export const emptyFlagsTemplate = Object.freeze({
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

export const initialFlagsTemplate = Object.freeze({
  ...emptyFlagsTemplate,
  flag_bookmarked: true,
})

export const useSvFlagsStore = defineStore('svFlags', () => {
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

  /** The structural that flags are handled for in detail view. */
  const sv = ref<Strucvar | null>(null)
  /** The flags for the structural variant `sv` as fetched from API for the detail view. */
  const flags = ref<StructuralVariantFlags | null>(null)
  /** The flags for all structural variants of the case with the given `caseUuid`. */
  const caseFlags = ref<Map<string, StructuralVariantFlags>>(new Map())

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

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    initializeRes.value = svClient
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
        console.error('Problem initializing svFlags store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /**
   * Retrieve flags for the given SV.
   */
  const retrieveFlags = async (strucvar$: Strucvar, caseUuid$?: string) => {
    // Prevent re-retrieval of the flags.
    if (isEqual(sv.value, strucvar$)) {
      return
    }

    // Throw error if case UUID has not been set.
    if (!caseUuid.value || !caseUuid$) {
      throw new Error('Case UUID not set')
    }

    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    flags.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      const res = await svClient.listFlags(
        caseUuid.value ?? caseUuid$,
        strucvar$,
      )
      if (res.length) {
        flags.value = res[0]
      } else {
        flags.value = null
      }

      sv.value = strucvar$
      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem loading flags for SV', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }
  }

  /**
   * Create a new flags entry.
   */
  const createFlags = async (
    strucvar: Strucvar,
    payload: StructuralVariantFlags,
  ): Promise<StructuralVariantFlags> => {
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')
    // Throw error if case UUID has not been set.
    if (!caseUuid.value) {
      throw new Error('Case UUID not set')
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let end
    if (strucvar.svType === 'INS' || strucvar.svType === 'BND') {
      end = strucvar.start
    } else {
      end = strucvar.stop
    }

    let result
    try {
      result = await svClient.createFlags(caseUuid.value, strucvar, {
        ...{
          release: strucvar.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
          chromosome: strucvar.chrom,
          start: strucvar.start,
          end,
          sv_type: strucvar.svType,
          sv_sub_type: strucvar.svType,
        },
        ...payload,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem creating flags for SV', err)
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
    payload: StructuralVariantFlags,
  ): Promise<StructuralVariantFlags> => {
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    if (!flags.value) {
      console.warn('Trying to update flags with flags.value being falsy')
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await svClient.updateFlags(flags.value.sodar_uuid, {
        ...sv,
        ...payload,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem updating flags for SV', err)
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
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    if (!flags.value) {
      console.warn('Trying to delete flags with flags.value being falsy')
      return
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await svClient.deleteFlags(flags.value.sodar_uuid)

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem deleting flags for SV', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseFlags.value.delete(flags.value.sodar_uuid)
    flags.value = null
  }

  /**
   * Return first matching flag for the given `sv`.
   */
  const getFlags = (sv: StructuralVariant): StructuralVariantFlags | null => {
    if (!caseFlags.value) {
      return null
    }

    const bndInsRadius = 50
    const minReciprocalOverlap = 0.8
    for (const flag of caseFlags.value.values()) {
      if (
        ['BND', 'INS'].includes(flag.sv_type) &&
        flag.sv_type === sv.sv_type &&
        bndInsOverlap(flag, sv, bndInsRadius)
      ) {
        return flag
      } else if (
        flag.sv_type === sv.sv_type &&
        reciprocalOverlap(flag, sv) >= minReciprocalOverlap
      ) {
        return flag
      }
    }
    return null
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    sv,
    flags,
    caseFlags,
    emptyFlagsTemplate,
    initialFlagsTemplate,
    // functions
    initialize,
    retrieveFlags,
    createFlags,
    updateFlags,
    deleteFlags,
    getFlags,
  }
})

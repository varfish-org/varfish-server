/**
 * Pinia store for handling per-variant flags.
 */

import { StoreState } from '@cases/stores/cases.js'
import variantsApi from '@variants/api/variants.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useVariantFlagsStore = defineStore('variantFlags', () => {
  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The CSRF token to use. */
  const csrfToken = ref(null)
  /** The UUID of the case. */
  const caseUuid = ref(null)
  /** The small variant that flags are handled for. */
  const smallVariant = ref(null)
  /** The small variants as fetched from API. */
  const flags = ref(null)

  /** The flags for all variants of the case with the given `caseUuid`. */
  const caseFlags = ref(null)

  const emptyFlagsTemplate = Object.freeze({
    flag_bookmarked: false,
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

  const initialFlagsTemplate = Object.freeze({
    ...emptyFlagsTemplate,
    flag_bookmarked: true,
  })

  /**
   * Initialize the store.
   */
  const initialize = async (applicationContext, caseUuidArg) => {
    if (storeState.value !== StoreState.initial) {
      // initialize only once
      return
    }

    caseUuid.value = caseUuidArg
    csrfToken.value = applicationContext.csrf_token

    await _fetchCaseFlags()

    storeState.value = StoreState.active
  }

  /**
   * Fetch all flags for the current case
   */
  const _fetchCaseFlags = async () => {
    serverInteractions.value += 1
    try {
      const res = await variantsApi.listFlags(csrfToken.value, caseUuid.value)
      caseFlags.value = Object.fromEntries(
        res.map((flags) => [flags.sodar_uuid, flags]),
      )
    } catch (err) {
      storeState.value = StoreState.error
      throw err
    } finally {
      serverInteractions.value -= 1
    }
  }

  /**
   * Retrieve flags for the given variant.
   */
  const retrieveFlags = async (smallVariant$) => {
    smallVariant.value = null
    serverInteractions.value += 1

    try {
      const res = await variantsApi.listFlags(
        csrfToken.value,
        caseUuid.value,
        smallVariant$,
      )
      if (res.length) {
        flags.value = res[0]
      } else {
        flags.value = null
      }
    } catch (err) {
      storeState.value = StoreState.error
      throw err // re-throw
    } finally {
      serverInteractions.value -= 1
    }

    smallVariant.value = smallVariant$
  }

  /**
   * Create a new flags entry.
   */
  const createFlags = async (smallVariant, payload) => {
    serverInteractions.value += 1
    let result
    try {
      result = await variantsApi.createFlags(
        csrfToken.value,
        caseUuid.value,
        smallVariant,
        { ...smallVariant, ...payload },
      )
    } finally {
      serverInteractions.value -= 1
    }

    caseFlags.value[result.sodar_uuid] = result
    flags.value = result

    return result
  }

  /**
   * Update existing flags.
   */
  const updateFlags = async (payload) => {
    if (!flags.value) {
      console.warn('Trying to update flags with flags.value being falsy')
    }

    serverInteractions.value += 1
    let result
    try {
      result = await variantsApi.updateFlags(
        csrfToken.value,
        flags.value.sodar_uuid,
        {
          ...smallVariant,
          ...payload,
        },
      )
    } finally {
      serverInteractions.value -= 1
    }

    caseFlags.value[result.sodar_uuid] = result
    flags.value = result

    return result
  }

  /**
   * Delete current flags.
   */
  const deleteFlags = async () => {
    if (!flags.value) {
      console.warn('Trying to delete flags with flags.value being falsy')
      return
    }
    serverInteractions.value += 1
    try {
      await variantsApi.deleteFlags(csrfToken.value, flags.value.sodar_uuid)
    } finally {
      serverInteractions.value -= 1
    }

    delete caseFlags.value[flags.value.sodar_uuid]
    flags.value = null
  }

  /**
   * Return flags for a given variant from the store.
   */
  const getFlags = (variant) => {
    if (!caseFlags.value) {
      return null
    }
    for (const flag of Object.values(caseFlags.value)) {
      if (
        flag.release === variant.release &&
        flag.chromosome === variant.chromosome &&
        flag.start === variant.start &&
        flag.end === variant.end &&
        flag.reference === variant.reference &&
        flag.alternative === variant.alternative
      ) {
        return flag
      }
    }
    return null
  }

  const flagAsArtifact = async (variant) => {
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
      await createFlags(variant, {
        ...emptyFlagsTemplate,
        flag_summary: 'negative',
        flag_visual: 'negative',
      })
    }
  }

  return {
    // data / state
    storeState,
    serverInteractions,
    csrfToken,
    caseUuid,
    smallVariant,
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
    flagAsArtifact,
  }
})

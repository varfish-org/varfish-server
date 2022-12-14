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

  /**
   * Initialize the store.
   */
  const initialize = async (applicationContext, caseUuuidArg) => {
    if (storeState.value !== StoreState.initial) {
      // initialize only once
      return
    }
    storeState.value = StoreState.active
    caseUuid.value = caseUuuidArg
    csrfToken.value = applicationContext.csrf_token
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
        smallVariant$
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
        { ...smallVariant, ...payload }
      )
    } finally {
      serverInteractions.value -= 1
    }

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
        }
      )
    } finally {
      serverInteractions.value -= 1
    }

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

    flags.value = null
  }

  return {
    // data / state
    storeState,
    serverInteractions,
    csrfToken,
    caseUuid,
    smallVariant,
    flags,
    // functions
    initialize,
    retrieveFlags,
    createFlags,
    updateFlags,
    deleteFlags,
  }
})

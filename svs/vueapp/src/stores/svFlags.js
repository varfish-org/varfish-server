/**
 * Pinia store for handling per-SV flags.
 */

import { StoreState } from '@cases/stores/cases.js'
import svsApi from '@svs/api/svs.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const emptyFlagsTemplate = Object.freeze({
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

export const initialFlagsTemplate = Object.freeze({
  ...emptyFlagsTemplate,
  flag_bookmarked: true,
})

export const useSvFlagsStore = defineStore('svFlags', () => {
  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The CSRF token to use. */
  const csrfToken = ref(null)
  /** The UUID of the case. */
  const caseUuid = ref(null)
  /** The small variant that flags are handled for. */
  const sv = ref(null)
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
   * Retrieve flags for the given SV.
   */
  const retrieveFlags = async (sv$) => {
    sv.value = null
    flags.value = null
    serverInteractions.value += 1

    try {
      const res = await svsApi.listFlags(csrfToken.value, caseUuid.value, sv$)
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

    sv.value = sv$
  }

  /**
   * Create a new flags entry.
   */
  const createFlags = async (sv, payload) => {
    serverInteractions.value += 1
    let result
    try {
      result = await svsApi.createFlags(csrfToken.value, caseUuid.value, sv, {
        ...sv,
        ...payload,
      })
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
      result = await svsApi.updateFlags(
        csrfToken.value,
        flags.value.sodar_uuid,
        {
          ...sv,
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
      await svsApi.deleteFlags(csrfToken.value, flags.value.sodar_uuid)
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
    sv,
    flags,
    // functions
    initialize,
    retrieveFlags,
    createFlags,
    updateFlags,
    deleteFlags,
  }
})

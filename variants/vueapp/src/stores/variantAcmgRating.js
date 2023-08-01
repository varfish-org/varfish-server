/**
 * Pinia store for handling per-variant ACMG rating.
 */
import { StoreState } from '@cases/stores/cases'
import variantsApi from '@variants/api/variants'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useVariantAcmgRatingStore = defineStore(
  'variantAcmgRating',
  () => {
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
    /** The small variants ACMG rating as fetched from API. */
    const acmgRating = ref(null)

    /** The ACMG ratings for all variants of the case with the given `caseUuid`. */
    const caseAcmgRatings = ref(null)

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

      await _fetchCaseAcmgRatings()

      storeState.value = StoreState.active
    }

    /**
     * Fetch all ACMG ratings for the current case
     */
    const _fetchCaseAcmgRatings = async () => {
      serverInteractions.value += 1
      try {
        const res = await variantsApi.listAcmgRating(
          csrfToken.value,
          caseUuid.value,
        )
        caseAcmgRatings.value = Object.fromEntries(
          res.map((acmgRating) => [acmgRating.sodar_uuid, acmgRating]),
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
    const retrieveAcmgRating = async (smallVariant$) => {
      smallVariant.value = null
      serverInteractions.value += 1

      try {
        const res = await variantsApi.listAcmgRating(
          csrfToken.value,
          caseUuid.value,
          smallVariant$,
        )
        if (res.length) {
          acmgRating.value = res[0]
        } else {
          acmgRating.value = null
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
    const createAcmgRating = async (smallVariant, payload) => {
      serverInteractions.value += 1
      let result
      try {
        result = await variantsApi.createAcmgRating(
          csrfToken.value,
          caseUuid.value,
          smallVariant,
          { ...smallVariant, ...payload },
        )
      } finally {
        serverInteractions.value -= 1
      }

      caseAcmgRatings.value[result.sodar_uuid] = result
      acmgRating.value = result

      return result
    }

    /**
     * Update existing flags.
     */
    const updateAcmgRating = async (payload) => {
      if (!acmgRating.value) {
        console.warn('Trying to update flags with flags.value being falsy')
      }

      serverInteractions.value += 1
      let result
      try {
        result = await variantsApi.updateAcmgRating(
          csrfToken.value,
          acmgRating.value.sodar_uuid,
          {
            ...smallVariant,
            ...payload,
          },
        )
      } finally {
        serverInteractions.value -= 1
      }

      caseAcmgRatings.value[result.sodar_uuid] = result
      acmgRating.value = result

      return result
    }

    /**
     * Delete current flags.
     */
    const deleteAcmgRating = async () => {
      if (!acmgRating.value) {
        console.warn('Trying to delete flags with flags.value being falsy')
        return
      }
      serverInteractions.value += 1
      try {
        await variantsApi.deleteAcmgRating(
          csrfToken.value,
          acmgRating.value.sodar_uuid,
        )
      } finally {
        serverInteractions.value -= 1
      }

      delete caseAcmgRatings.value[acmgRating.value.sodar_uuid]
      acmgRating.value = null
    }

    /**
     * Return flags for a given variant from the store.
     */
    const getAcmgRating = (variant) => {
      if (!caseAcmgRatings.value) {
        return null
      }
      for (const caseAcmgRating of Object.values(caseAcmgRatings.value)) {
        if (
          caseAcmgRating.release === variant.release &&
          caseAcmgRating.chromosome === variant.chromosome &&
          caseAcmgRating.start === variant.start &&
          caseAcmgRating.end === variant.end &&
          caseAcmgRating.reference === variant.reference &&
          caseAcmgRating.alternative === variant.alternative
        ) {
          return caseAcmgRating.class_override || caseAcmgRating.class_auto
        }
      }
      return null
    }

    return {
      // data / state
      storeState,
      serverInteractions,
      csrfToken,
      caseUuid,
      smallVariant,
      acmgRating,
      caseAcmgRatings,
      // functions
      initialize,
      retrieveAcmgRating,
      createAcmgRating,
      updateAcmgRating,
      deleteAcmgRating,
      getAcmgRating,
    }
  },
)

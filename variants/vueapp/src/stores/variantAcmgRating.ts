/**
 * Pinia store for handling per-variant ACMG rating.
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

/** Alias definition of SmallVariant type; to be defined later. */
type SmallVariant = any
/** Alias definition of AcmgRating type; to be defined later. */
type AcmgRating = any

export const useVariantAcmgRatingStore = defineStore(
  'variantAcmgRating',
  () => {
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

    /** The small variant that acmgRating are handled for. */
    const smallVariant = ref<SmallVariant | null>(null)
    /** The small variants ACMG rating as fetched from API. */
    const acmgRating = ref<AcmgRating | null>(null)
    /** The ACMG ratings for all variants of the case with the given `caseUuid`. */
    const caseAcmgRatings = ref<Map<string, AcmgRating>>(new Map())

    /** Promise for initialization of the store. */
    const initializeRes = ref<Promise<any>>(null)

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

      const variantClient = new VariantClient(csrfToken.value)

      initializeRes.value = variantClient
        .listAcmgRating(caseUuid.value)
        .then((acmgRatings) => {
          caseAcmgRatings.value.clear()
          for (const acmgRating of acmgRatings) {
            caseAcmgRatings.value.set(acmgRating.sodar_uuid, acmgRating)
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
     * Retrieve acmgRating for the given variant.
     */
    const retrieveAcmgRating = async (smallVariant$) => {
      const variantClient = new VariantClient(csrfToken.value)

      smallVariant.value = null
      storeState.state = State.Fetching
      storeState.serverInteractions += 1

      try {
        const res = await variantClient.listAcmgRating(
          caseUuid.value,
          smallVariant$,
        )
        if (res.length) {
          acmgRating.value = res[0]
        } else {
          acmgRating.value = null
        }

        smallVariant.value = smallVariant$

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      } catch (err) {
        console.error('Problem loading ACMG ratings for variant', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
        throw err // re-throw
      }
    }

    /**
     * Create a new acmgRating entry.
     */
    const createAcmgRating = async (smallVariant, payload) => {
      const variantClient = new VariantClient(csrfToken.value)

      storeState.state = State.Fetching
      storeState.serverInteractions += 1

      let result
      try {
        result = await variantClient.createAcmgRating(
          caseUuid.value,
          smallVariant,
          { ...smallVariant, ...payload },
        )

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      } catch (err) {
        console.error('Problem creating ACMG rating for variant', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
        throw err // re-throw
      }

      caseAcmgRatings.value.set(result.sodar_uuid, result)
      acmgRating.value = result

      return result
    }

    /**
     * Update existing acmgRating.
     */
    const updateAcmgRating = async (payload) => {
      const variantClient = new VariantClient(csrfToken.value)

      if (!acmgRating.value) {
        console.warn(
          'Trying to update acmgRating with acmgRating.value being falsy',
        )
      }

      storeState.state = State.Fetching
      storeState.serverInteractions += 1

      let result
      try {
        result = await variantClient.updateAcmgRating(
          acmgRating.value.sodar_uuid,
          {
            ...smallVariant,
            ...payload,
          },
        )

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      } catch (err) {
        console.error('Problem updating ACMG rating for variant', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
        throw err // re-throw
      }

      caseAcmgRatings.value.set(result.sodar_uuid, result)
      acmgRating.value = result

      return result
    }

    /**
     * Delete current acmgRating.
     */
    const deleteAcmgRating = async () => {
      const variantClient = new VariantClient(csrfToken.value)

      if (!acmgRating.value) {
        console.warn(
          'Trying to delete acmgRating with acmgRating.value being falsy',
        )
        return
      }

      storeState.state = State.Fetching
      storeState.serverInteractions += 1

      try {
        await variantClient.deleteAcmgRating(acmgRating.value.sodar_uuid)

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      } catch (err) {
        console.error('Problem deleting ACMG rating for variant', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
        throw err // re-throw
      }

      caseAcmgRatings.value.delete(acmgRating.value.sodar_uuid)
      acmgRating.value = null
    }

    /**
     * Return acmgRating for a given variant from the store.
     */
    const getAcmgRating = (variant) => {
      for (const caseAcmgRating of caseAcmgRatings.value.values()) {
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
      csrfToken,
      storeState,
      caseUuid,
      projectUuid,
      smallVariant,
      acmgRating,
      caseAcmgRatings,
      initializeRes,
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

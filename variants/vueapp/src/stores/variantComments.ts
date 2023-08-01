/**
 * Pinia store for handling per-variant comments.
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
/** Alias definition of SmallVariantComments type; to be defined later. */
type SmallVariantComment = any

export const useVariantCommentsStore = defineStore('variantComments', () => {
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

  /** The small variant that comments are handled for. */
  const smallVariant = ref<SmallVariant | null>(null)
  /** The small variants as fetched from API. */
  const comments = ref<SmallVariantComment | null>(null)
  /** The comments for all variants of the case with the given `caseUuid`. */
  const caseComments = ref<Map<string, SmallVariantComment>>(new Map())

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any>>(null)

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

    const variantClient = new VariantClient(csrfToken.value)

    initializeRes.value = variantClient
      .listComment(caseUuid.value)
      .then((comments) => {
        caseComments.value.clear()
        for (const comment of comments) {
          caseComments.value.set(comment.sodar_uuid, comment)
        }

        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing variantComments store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /**
   * Retrieve comments for the given variant.
   */
  const retrieveComments = async (smallVariant$: SmallVariant) => {
    const variantClient = new VariantClient(csrfToken.value)

    comments.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      comments.value = await variantClient.listComment(
        caseUuid.value,
        smallVariant$,
      )

      smallVariant.value = smallVariant$

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem loading comments for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }
  }

  /**
   * Create a new comment.
   */
  const createComment = async (
    smallVariant: SmallVariant,
    text: string,
  ): Promise<SmallVariant> => {
    const variantClient = new VariantClient(csrfToken.value)

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.createComment(caseUuid.value, smallVariant, {
        ...smallVariant,
        text,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem creating comments for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.set(result.sodar_uuid, result)
    comments.value.push(result)

    return result
  }

  /**
   * Update an existing comment.
   */
  const updateComment = async (
    commentUuid: string,
    text: string,
  ): Promise<SmallVariant> => {
    const variantClient = new VariantClient(csrfToken.value)

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.updateComment(commentUuid, {
        ...smallVariant,
        text,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem updating comment for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.set(result.sodar_uuid, result)

    for (let i = 0; i < comments.value.length; i++) {
      if (comments.value[i].sodar_uuid === commentUuid) {
        comments.value[i] = result
        break
      }
    }

    return result
  }

  /**
   * Delete a comment by UUID.
   */
  const deleteComment = async (commentUuid: string) => {
    const variantClient = new VariantClient(csrfToken.value)

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await variantClient.deleteComment(commentUuid)
    } catch (err) {
      console.error('Problem deleting comment for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.delete(commentUuid)
    comments.value = comments.value.filter(
      (comment) => comment.sodar_uuid !== commentUuid,
    )
  }

  /**
   * Does a variant have comments?
   */
  const hasComments = (variant: SmallVariant): boolean => {
    for (const comment of caseComments.value.values()) {
      if (
        comment.release === variant.release &&
        comment.chromosome === variant.chromosome &&
        comment.start === variant.start &&
        comment.end === variant.end &&
        comment.reference === variant.reference &&
        comment.alternative === variant.alternative
      ) {
        return true
      }
    }

    return false
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    smallVariant,
    comments,
    caseComments,
    initializeRes,
    // functions
    initialize,
    retrieveComments,
    createComment,
    updateComment,
    deleteComment,
    hasComments,
  }
})

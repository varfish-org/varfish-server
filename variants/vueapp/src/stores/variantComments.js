/**
 * Pinia store for handling per-variant comments.
 */

import { StoreState } from '@cases/stores/cases.js'
import variantsApi from '@variants/api/variants.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useVariantCommentsStore = defineStore('variantComments', () => {
  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The CSRF token to use. */
  const csrfToken = ref(null)
  /** The UUID of the case. */
  const caseUuid = ref(null)
  /** The small variant that comments are handled for. */
  const smallVariant = ref(null)
  /** The small variants as fetched from API. */
  const comments = ref(null)

  /** The comments for all variants of the case with the given `caseUuid`. */
  const caseComments = ref(null)

  /**
   * Initialize the store.
   */
  const initialize = async (applicationContext, caseUuuidArg) => {
    if (storeState.value !== StoreState.initial) {
      // initialize only once
      return
    }

    caseUuid.value = caseUuuidArg
    csrfToken.value = applicationContext.csrf_token

    await _fetchCaseComments()

    storeState.value = StoreState.active
  }

  /**
   * Fetch all comments for the current case
   */
  const _fetchCaseComments = async () => {
    serverInteractions.value += 1
    try {
      const res = await variantsApi.listComment(csrfToken.value, caseUuid.value)
      caseComments.value = Object.fromEntries(
        res.map((comments) => [comments.sodar_uuid, comments]),
      )
    } catch (err) {
      storeState.value = StoreState.error
      throw err
    } finally {
      serverInteractions.value -= 1
    }
  }

  /**
   * Retrieve comments for the given variant.
   */
  const retrieveComments = async (smallVariant$) => {
    smallVariant.value = null
    serverInteractions.value += 1

    try {
      comments.value = await variantsApi.listComment(
        csrfToken.value,
        caseUuid.value,
        smallVariant$,
      )
    } catch (err) {
      storeState.value = StoreState.error
      throw err // re-throw
    } finally {
      serverInteractions.value -= 1
    }

    smallVariant.value = smallVariant$
  }

  /**
   * Create a new comment.
   */
  const createComment = async (smallVariant, text) => {
    serverInteractions.value += 1
    let result
    try {
      result = await variantsApi.createComment(
        csrfToken.value,
        caseUuid.value,
        smallVariant,
        { ...smallVariant, text },
      )
    } finally {
      serverInteractions.value -= 1
    }

    caseComments.value[result.sodar_uuid] = result
    comments.value.push(result)

    return result
  }

  /**
   * Update an existing comment.
   */
  const updateComment = async (commentUuid, text) => {
    serverInteractions.value += 1
    let result
    try {
      result = await variantsApi.updateComment(csrfToken.value, commentUuid, {
        ...smallVariant,
        text,
      })
    } finally {
      serverInteractions.value -= 1
    }

    caseComments.value[result.sodar_uuid] = result

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
  const deleteComment = async (commentUuid) => {
    serverInteractions.value += 1
    try {
      await variantsApi.deleteComment(csrfToken.value, commentUuid)
    } finally {
      serverInteractions.value -= 1
    }

    delete caseComments.value[commentUuid]
    comments.value = comments.value.filter(
      (comment) => comment.sodar_uuid !== commentUuid,
    )
  }

  /**
   * Does a variant have comments?
   */
  const hasComments = (variant) => {
    if (!caseComments.value) {
      return false
    }
    for (const comment of Object.values(caseComments.value)) {
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
    storeState,
    serverInteractions,
    csrfToken,
    caseUuid,
    smallVariant,
    comments,
    // functions
    initialize,
    retrieveComments,
    createComment,
    updateComment,
    deleteComment,
    hasComments,
  }
})

/**
 * Pinia store for handling per-SV comments.
 */

import { StoreState } from '@cases/stores/cases.js'
import svsApi from '@svs/api/svs.js'
import { reciprocalOverlap } from '@varfish/helpers.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSvCommentsStore = defineStore('svComments', () => {
  /** The current application state. */
  const storeState = ref(StoreState.initial)
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** The CSRF token to use. */
  const csrfToken = ref(null)
  /** The UUID of the case. */
  const caseUuid = ref(null)

  /** The structural variant that comments are handled for. */
  const sv = ref(null)
  /** The comments for the current structural variant as fetched from API. */
  const comments = ref(null)

  /** The comments for all structural variants of the case with the given `caseUuid`. */
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
      const res = await svsApi.listComment(csrfToken.value, caseUuid.value)
      caseComments.value = Object.fromEntries(
        res.map((comment) => [comment.sodar_uuid, comment])
      )
    } catch (err) {
      storeState.value = StoreState.error
      throw err
    } finally {
      serverInteractions.value -= 1
    }
  }
  /**
   * Retrieve comments for the given SV.
   */
  const retrieveComments = async (sv$) => {
    sv.value = null
    comments.value = null
    serverInteractions.value += 1

    try {
      comments.value = await svsApi.listComment(
        csrfToken.value,
        caseUuid.value,
        sv$
      )
    } catch (err) {
      storeState.value = StoreState.error
      throw err // re-throw
    } finally {
      serverInteractions.value -= 1
    }

    sv.value = sv$
  }

  /**
   * Create a new comment.
   */
  const createComment = async (sv, text) => {
    serverInteractions.value += 1
    let result
    try {
      result = await svsApi.createComment(csrfToken.value, caseUuid.value, sv, {
        ...sv,
        text,
      })
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
      result = await svsApi.updateComment(csrfToken.value, commentUuid, {
        ...sv,
        text,
      })
    } finally {
      serverInteractions.value -= 1
    }

    for (let i = 0; i < comments.value.length; i++) {
      if (comments.value[i].sodar_uuid === commentUuid) {
        comments.value[i] = result
        break
      }
    }

    caseComments.value[result.sodar_uuid] = result

    return result
  }

  /**
   * Delete a comment by UUID.
   */
  const deleteComment = async (commentUuid) => {
    serverInteractions.value += 1
    try {
      await svsApi.deleteComment(csrfToken.value, commentUuid)
    } finally {
      serverInteractions.value -= 1
    }

    delete caseComments.value[commentUuid]

    comments.value = comments.value.filter(
      (comment) => comment.sodar_uuid !== commentUuid
    )
  }

  /**
   * Return whether there is a comment for the given variant.
   */
  const hasComment = (sv) => {
    const minReciprocalOverlap = 0.8
    for (const comment of Object.values(caseComments.value)) {
      if (
        comment.sv_type == sv.sv_type &&
        reciprocalOverlap(comment, sv) >= minReciprocalOverlap
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
    sv,
    comments,
    caseComments,
    // functions
    initialize,
    retrieveComments,
    createComment,
    updateComment,
    deleteComment,
    hasComment,
  }
})

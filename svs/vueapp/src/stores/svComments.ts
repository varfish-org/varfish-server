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
import { SvClient } from '@svs/api/svClient'
import { reciprocalOverlap } from '@varfish/helpers'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'

/** Alias definition of StructuralVariant type; to be defined later. */
type StructuralVariant = any
/** Alias definition of StructuralVariantComment type; to be defined later. */
type StructuralVariantComment = any

export const useSvCommentsStore = defineStore('svComments', () => {
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

  /** The structural variant that comments are handled for. */
  const sv = ref<StructuralVariant | null>(null)
  /** The comments for the current structural variant as fetched from API. */
  const comments = ref<StructuralVariantComment | null>(null)
  /** The comments for all structural variants of the case with the given `caseUuid`. */
  const caseComments = ref<Map<string, StructuralVariantComment>>(new Map())

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

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
        console.error('Problem initializing svComments store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /**
   * Retrieve comments for the given SV.
   */
  const retrieveComments = async (sv$: StructuralVariant) => {
    // Prevent re-retrieval of the comment.
    if (sv.value?.sodar_uuid === sv$?.sodar_uuid) {
      return
    }
    // Error if case UUID is unset.
    if (!caseUuid.value) {
      throw new Error('Case UUID is not set')
    }

    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    sv.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      comments.value = await svClient.listComment(caseUuid.value, sv$)

      sv.value = sv$

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem loading comments for SV', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }
  }

  /**
   * Create a new comment.
   */
  const createComment = async (
    sv: StructuralVariant,
    text: string,
  ): Promise<StructuralVariant> => {
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')
    // Error if case UUID is unset.
    if (!caseUuid.value) {
      throw new Error('Case UUID is not set')
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await svClient.createComment(caseUuid.value, sv, {
        ...sv,
        text,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem creating comment for SV', err)
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
  ): Promise<StructuralVariant> => {
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await svClient.updateComment(commentUuid, {
        ...sv,
        text,
      })

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem updating comment for SV', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.set(result.sodarUuid, result)

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
    const svClient = new SvClient(csrfToken.value ?? 'undefined-csrf-token')

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await svClient.deleteComment(commentUuid)

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem deleting comment for SV', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.delete(commentUuid)
    comments.value = comments.value.filter(
      (comment: any) => comment.sodar_uuid !== commentUuid,
    )
  }

  /**
   * Return whether there is a comment for the given variant.
   */
  const hasComment = (sv: StructuralVariant): boolean => {
    const minReciprocalOverlap = 0.8
    for (const comment of caseComments.value.values()) {
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
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    sv,
    comments,
    caseComments,
    initializeRes,
    // functions
    initialize,
    retrieveComments,
    createComment,
    updateComment,
    deleteComment,
    hasComment,
  }
})

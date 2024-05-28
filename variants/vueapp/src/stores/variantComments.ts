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
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

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
  const seqvar = ref<Seqvar | null>(null)
  /** The small variants as fetched from API. */
  const comments = ref<SmallVariantComment | null>(null)
  /** The comments for all variants of the case with the given `caseUuid`. */
  const caseComments = ref<Map<string, SmallVariantComment>>(new Map())
  /** The project-wide variant comments. */
  const projectWideVariantComments = ref<Array<SmallVariantComment>>([])
  /** The project-wide comments. */
  const projectWideComments = ref<Map<string, Array<SmallVariantComment>>>(
    new Map(),
  )

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

    $reset()

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    initializeRes.value = Promise.all([
      variantClient.listComment(caseUuid.value).then((result) => {
        caseComments.value.clear()
        for (const comment of result) {
          caseComments.value.set(comment.sodar_uuid, comment)
        }
      }),
      variantClient
        .listProjectComment(projectUuid.value, caseUuid.value)
        .then((result) => {
          for (const comment of result) {
            const key = `${comment.chromosome}-${comment.start}-${comment.reference}-${comment.alternative}`
            if (!projectWideComments.value.has(key)) {
              projectWideComments.value.set(key, [comment])
            } else {
              let comments = projectWideComments.value.get(key)
              if (comments) {
                comments.push(comment)
              } else {
                comments = [comment]
              }
              projectWideComments.value.set(key, comments)
            }
          }
        }),
    ]).catch((err) => {
      console.error('Problem initializing variantComments store', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
    })

    storeState.serverInteractions -= 1
    storeState.state = State.Active

    return initializeRes.value
  }

  /**
   * Retrieve comments for the given variant.
   */
  const retrieveComments = async (seqvar$: Seqvar) => {
    if (!caseUuid.value) {
      throw new Error('caseUuid not set')
    }

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    comments.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      comments.value = await variantClient.listComment(caseUuid.value, seqvar$)
      seqvar.value = seqvar$

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
    seqvar: Seqvar,
    text: string,
    resultRowUuid: string,
  ): Promise<Seqvar> => {
    if (!caseUuid.value) {
      throw new Error('caseUuid not set')
    }
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.createComment(caseUuid.value, seqvar, {
        ...{
          release: seqvar.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
          chromosome: seqvar.chrom,
          start: seqvar.pos,
          end: seqvar.pos + seqvar.del.length - 1,
          reference: seqvar.del,
          alternative: seqvar.ins,
          sodar_uuid: resultRowUuid,
        },
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
  ): Promise<Seqvar> => {
    if (!seqvar.value) {
      throw new Error('seqvar not set')
    }
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let result
    try {
      result = await variantClient.updateComment(commentUuid, {
        ...{
          release: seqvar.value.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
          chromosome: seqvar.value.chrom,
          start: seqvar.value.pos,
          end: seqvar.value.pos + seqvar.value.del.length - 1,
          reference: seqvar.value.del,
          alternative: seqvar.value.ins,
        },
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
    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      await variantClient.deleteComment(commentUuid)

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem deleting comment for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }

    caseComments.value.delete(commentUuid)
    comments.value = comments.value.filter(
      (comment: SmallVariantComment) => comment.sodar_uuid !== commentUuid,
    )
  }

  /**
   * Does a variant have comments?
   */
  const hasComments = (seqvar: Seqvar): boolean => {
    for (const comment of caseComments.value.values()) {
      if (
        comment.release ===
          (seqvar.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38') &&
        comment.chromosome === seqvar.chrom &&
        comment.start === seqvar.pos &&
        comment.end === seqvar.pos + seqvar.del.length - 1 &&
        comment.reference === seqvar.del &&
        comment.alternative === seqvar.ins
      ) {
        return true
      }
    }

    return false
  }

  const hasProjectWideComments = (seqvar: Seqvar): boolean => {
    const val = projectWideComments.value.get(
      `${seqvar.chrom}-${seqvar.pos}-${seqvar.del}-${seqvar.ins}`,
    )
    if (val) {
      return val.length > 0
    }
    return false
  }

  /**
   * Retrieve project-wide comments.
   */
  const retrieveProjectWideVariantComments = async (seqvar$: Seqvar) => {
    if (!caseUuid.value) {
      throw new Error('caseUuid not set')
    }

    if (!projectUuid.value) {
      throw new Error('projectUuid not set')
    }

    const variantClient = new VariantClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    projectWideVariantComments.value = []
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      projectWideVariantComments.value = await variantClient.listProjectComment(
        projectUuid.value,
        caseUuid.value,
        seqvar$,
      )

      storeState.serverInteractions -= 1
      storeState.state = State.Active
    } catch (err) {
      console.error('Problem loading comments for variant', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
      throw err // re-throw
    }
  }

  const $reset = () => {
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

    csrfToken.value = null
    caseUuid.value = null
    projectUuid.value = null
    seqvar.value = null
    comments.value = null
    caseComments.value = new Map()
    initializeRes.value = null
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    seqvar,
    comments,
    caseComments,
    projectWideVariantComments,
    projectWideComments,
    initializeRes,
    // functions
    initialize,
    retrieveComments,
    retrieveProjectWideVariantComments,
    createComment,
    updateComment,
    deleteComment,
    hasComments,
    hasProjectWideComments,
    $reset,
  }
})

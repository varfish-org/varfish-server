/**
 * Pinia store for handling per-variant comments.
 *
 * ## Store Dependencies
 *
 * - `caseDetailsStore`
 */
import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import isEqual from 'fast-deep-equal'
import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { SvClient } from '@/svs/api/strucvarClient'
import { reciprocalOverlap } from '@/varfish/helpers'
import { State, StoreState } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'

/** Alias definition of StructuralVariantComment type; to be defined later. */
type StructuralVariantComment = any

export const useSvCommentsStore = defineStore('svComments', () => {
  // store dependencies

  /** Context store. */
  const ctxStore = useCtxStore()
  /** The caseDetails store */
  const caseDetailsStore = useCaseDetailsStore()

  // data passed to `initialize` and store state

  /** UUID of the project.  */
  const projectUuid = ref<string | null>(null)
  /** UUID of the case that this store holds annotations for. */
  const caseUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = reactive<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** The structural variant that comments are handled for. */
  const sv = ref<Strucvar | null>(null)
  /** The comments for the current structural variant as fetched from API. */
  const comments = ref<StructuralVariantComment | null>(null)
  /** The comments for all structural variants of the case with the given `caseUuid`. */
  const caseComments = ref<Map<string, StructuralVariantComment>>(new Map())
  /** The project-wide variant comments. */
  const projectWideVariantComments = ref<Array<StructuralVariantComment>>([])
  /** The project-wide comments. */
  const projectWideComments = ref<Array<StructuralVariantComment>>([])

  /** Promise for initialization of the store. */
  const initializeRes = ref<Promise<any> | null>(null)

  /**
   * Initialize the store for the given case.
   *
   * This will fetch all information via the REST API, but only once for each state.
   *
   * This will also initialize the store dependencies.
   *
   * @param projectUuid$ UUID of the project.
   * @param caseUuid$ UUID of the case to use.
   * @param forceReload Whether to force the reload.
   * @returns Promise with the finalization results.
   */
  const initialize = async (
    projectUuid$: string,
    caseUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseDetailsStore.initialize(projectUuid$, caseUuid$, forceReload)

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
    projectUuid.value = projectUuid$
    caseUuid.value = caseUuid$

    // Start fetching.
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    const svClient = new SvClient(ctxStore.csrfToken)

    initializeRes.value = Promise.all([
      svClient.listComment(caseUuid.value).then((comments) => {
        caseComments.value.clear()
        for (const comment of comments) {
          caseComments.value.set(comment.sodar_uuid, comment)
        }
      }),
      svClient
        .listProjectComment(projectUuid.value, caseUuid.value)
        .then((result) => {
          projectWideComments.value = result
        }),
    ]).catch((err) => {
      console.error('Problem initializing svComments store', err)
      storeState.serverInteractions -= 1
      storeState.state = State.Error
    })

    storeState.serverInteractions -= 1
    storeState.state = State.Active

    return initializeRes.value
  }

  /**
   * Retrieve comments for the given SV.
   */
  const retrieveComments = async (sv$: Strucvar, caseUuid$?: string) => {
    // Prevent re-retrieval of the comment.
    if (isEqual(sv.value, sv$)) {
      return
    }
    // Error if case UUID is unset.
    if (!caseUuid.value || !caseUuid$) {
      throw new Error('Case UUID is not set')
    }

    const svClient = new SvClient(ctxStore.csrfToken)

    sv.value = null
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      comments.value = await svClient.listComment(
        caseUuid.value ?? caseUuid$,
        sv$,
      )

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
    strucvar: Strucvar,
    text: string,
  ): Promise<Strucvar> => {
    const svClient = new SvClient(ctxStore.csrfToken)
    // Error if case UUID is unset.
    if (!caseUuid.value) {
      throw new Error('Case UUID is not set')
    }

    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    let end
    if (strucvar.svType === 'INS' || strucvar.svType === 'BND') {
      end = strucvar.start
    } else {
      end = strucvar.stop
    }

    let result
    try {
      result = await svClient.createComment(caseUuid.value, strucvar, {
        ...{
          release: strucvar.genomeBuild === 'grch37' ? 'GRCh37' : 'GRCh38',
          chromosome: strucvar.chrom,
          start: strucvar.start,
          end,
          sv_type: strucvar.svType,
          sv_sub_type: strucvar.svType,
        },
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
  ): Promise<Strucvar> => {
    const svClient = new SvClient(ctxStore.csrfToken)

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
    const svClient = new SvClient(ctxStore.csrfToken)

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

  const _hasComment = (
    strucvar$: Strucvar,
    comments: StructuralVariantComment,
  ): boolean => {
    const minReciprocalOverlap = 0.8
    for (const comment of comments) {
      let end
      if (strucvar$.svType === 'INS' || strucvar$.svType === 'BND') {
        end = strucvar$.start
      } else {
        end = strucvar$.stop
      }
      if (
        comment.sv_type === strucvar$.svType &&
        reciprocalOverlap(comment, {
          chromosome: strucvar$.chrom,
          start: strucvar$.start,
          end,
        }) >= minReciprocalOverlap
      ) {
        return true
      }
    }
    return false
  }

  /**
   * Return whether there is a comment for the given variant.
   */
  const hasComment = (strucvar$: Strucvar): boolean => {
    return _hasComment(strucvar$, caseComments.value.values())
  }

  const hasProjectWideComments = (strucvar$: Strucvar): boolean => {
    return _hasComment(strucvar$, projectWideVariantComments.value)
  }

  /**
   * Retrieve project-wide variant comments.
   */
  const retrieveProjectWideVariantComments = async (strucvar$: Strucvar) => {
    if (!caseUuid.value) {
      throw new Error('caseUuid not set')
    }

    if (!projectUuid.value) {
      throw new Error('projectUuid not set')
    }

    const svClient = new SvClient(ctxStore.csrfToken)

    projectWideVariantComments.value = []
    storeState.state = State.Fetching
    storeState.serverInteractions += 1

    try {
      projectWideVariantComments.value = await svClient.listProjectComment(
        projectUuid.value,
        caseUuid.value,
        strucvar$,
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

  return {
    // data / state
    storeState,
    caseUuid,
    projectUuid,
    sv,
    comments,
    caseComments,
    projectWideVariantComments,
    projectWideComments,
    initializeRes,
    // functions
    initialize,
    retrieveComments,
    createComment,
    updateComment,
    deleteComment,
    hasComment,
    hasProjectWideComments,
    retrieveProjectWideVariantComments,
  }
})

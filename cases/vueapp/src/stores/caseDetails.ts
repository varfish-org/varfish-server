/** Store for case details.
 *
 * This includes user annotations of variants.
 *
 * ## Store Dependencies
 *
 * - `caseListStore`
 */

import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'

import { StoreState, State } from '@varfish/storeUtils'

import { CaseClient } from '@cases/api/caseClient'
import { useCaseListStore } from '@cases/stores/caseList'

/** Alias definition of Case type; to be defined later. */
type Case = any
/** Alias definition of CaseComment type; to be defined later. */
type CaseComment = any
/** Alias definition of GeneAnnotation type; to be defined later. */
type GeneAnnotation = any
/** Alias definiton of VarAnno type; to be defined later. */
type VarAnno = any
/** Alias definiton of VarComment type; to be defined later. */
type VarComment = any
/** Alias definition fo AcmgRating type; to be defind later. */
type AcmgRating = any
/** Alias definition of SvAnno type; to be defined later. */
type SvAnno = any
/** Alias definition of SvComment type; to be defined later. */
type SvComment = any
/** Alias definition of CaseAlignmentStats type; to be defined later. */
type CaseAlignmnentStats = any
/** Alias definition of CaseVariantStats type; to be defined later. */
type CaseVariantStats = any
/** Alias definition of CaseRelatedness type; to be defined later. */
type CaseRelatedness = any
/** Alias definition of CasePhenotypeTerms type; to be defined later. */
type CasePhenotypeTerms = any
/** Alias definition of CaseAnnotationReleaseInfos type; to be defined later. */
type CaseAnnotationReleaseInfos = any
/** Alias definition of CaseSvAnnotationReleaseInfos type; to be defined later. */
type CaseSvAnnotationReleaseInfos = any

export const useCaseDetailsStore = defineStore('caseDetails', () => {
  // store dependencies

  /** The caseList store */
  const caseListStore = useCaseListStore()

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

  /** The case object. */
  const caseObj = ref<Case>(null)

  /** The comments on the case. */
  const caseComments = ref<CaseComment[]>(null)
  /** The per-gene annotation of the case. */
  const geneAnnotations = ref<GeneAnnotation[]>(null)

  /** Object with mapping of variant identifier to variant annotations. */
  const varAnnos = ref<Map<string, VarAnno>>(new Map())
  /** List of all variant annotations. */
  const varAnnoList = computed<VarAnno[]>(() =>
    Array.from(varAnnos.value.values()),
  )

  /** Object with mapping of variant identifier to variant comment. */
  const varComments = ref<Map<string, VarComment>>(new Map())
  /** List of all variant comments. */
  const varCommentList = computed<VarComment[]>(() =>
    Array.from(varAnnos.value.values()),
  )

  /** Object with mapping of variant identifier to ACMG ratings. */
  const acmgRatings = ref<Map<string, AcmgRating>>(new Map())
  /** List of all ACMG ratings. */
  const acmgRatingList = computed<AcmgRating[]>(() =>
    Array.from(varAnnos.value.values()),
  )

  /** Object with mapping of SV identifier to SV annotations. */
  const svAnnos = ref<Map<string, SvAnno>>(new Map())
  /** List of all SV annotations. */
  const svAnnoList = computed<SvAnno[]>(() =>
    Array.from(varAnnos.value.values()),
  )

  /** Object with mapping of SV identifier to variant comment. */
  const svComments = ref<Map<string, SvComment>>(new Map())
  /** List of all SV comments. */
  const svCommentList = computed<SvComment[]>(() =>
    Array.from(varAnnos.value.values()),
  )

  /** Case alignment stats. */
  const caseAlignmentStats = ref<CaseAlignmnentStats | null>(null)
  /** Case variant stats. */
  const caseVariantStats = ref<CaseVariantStats | null>(null)
  /** Case relatedness. */
  const caseRelatedness = ref<CaseRelatedness | null>(null)
  /** Case phenotype terms. */
  const casePhenotypeTerms = ref<CasePhenotypeTerms | null>(null)
  /** Case annotation release infos. */
  const caseAnnotationReleaseInfos = ref<CaseAnnotationReleaseInfos | null>(
    null,
  )
  /** Case SV annotation release infos. */
  const caseSvAnnotationReleaseInfos = ref<CaseSvAnnotationReleaseInfos | null>(
    null,
  )

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
    await caseListStore.initialize(csrfToken$, projectUuid$, forceReload)

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

    const caseClient = new CaseClient(csrfToken.value)

    initializeRes.value = Promise.all([
      caseClient.retrieveCase(caseUuid.value).then((res) => {
        caseObj.value = res
      }),
      caseClient.listCaseComment(caseUuid.value).then((res) => {
        caseComments.value = res
      }),
      caseClient.fetchVarAnnos(caseUuid.value).then((res) => {
        varAnnos.value = res
      }),
      caseClient.fetchSvAnnos(caseUuid.value).then((res) => {
        svAnnos.value = res
      }),
      caseClient.fetchCaseGeneAnnotation(caseUuid.value).then((res) => {
        geneAnnotations.value = res
      }),
      caseClient.fetchCaseVariantStats(caseUuid.value).then((res) => {
        caseVariantStats.value = Object.fromEntries(
          res.map((line) => [line.sample_name, line]),
        )
      }),
      caseClient.fetchCaseRelatedness(caseUuid.value).then((res) => {
        caseRelatedness.value = res
      }),
      caseClient.listCasePhenotypeTerms(caseUuid.value).then((res) => {
        casePhenotypeTerms.value = res
      }),
      caseClient.fetchAnnotationReleaseInfos(caseUuid.value).then((res) => {
        caseAnnotationReleaseInfos.value = res
      }),
      caseClient.fetchSvAnnotationReleaseInfos(caseUuid.value).then((res) => {
        caseSvAnnotationReleaseInfos.value = res
      }),
      caseClient.fetchCaseAlignmentStats(caseUuid.value).then((res) => {
        if (res.length > 0) {
          caseAlignmentStats.value = res[0]
        } else {
          caseAlignmentStats.value = null
        }
      }),
    ])
      .then(() => {
        storeState.serverInteractions -= 1
        storeState.state = State.Active
      })
      .catch((err) => {
        console.error('Problem initializing caseListStore store', err)
        storeState.serverInteractions -= 1
        storeState.state = State.Error
      })

    return initializeRes.value
  }

  /** Update the case with the given data. */
  const updateCase = async (payload: Case) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      caseObj.value = await caseClient.updateCase(
        caseObj.value.sodar_uuid,
        payload,
      )
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  /** Get case comment by UUID. */
  const getCaseComment = (caseCommentUuid: string): CaseComment | null => {
    for (const obj of caseComments.value) {
      if (obj.sodar_uuid === caseCommentUuid) {
        return obj
      }
    }
    return null
  }

  /** Create a new case comment for the current case. */
  const createCaseComment = async (payload: CaseComment) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      const apiCaseComment = await caseClient.createCaseComment(
        caseObj.value.sodar_uuid,
        payload,
      )
      caseComments.value.push(apiCaseComment)
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  /** Update a case comment for the current case. */
  const updateCaseComment = async (
    caseCommentUuid: string,
    payload: CaseComment,
  ) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      const apiCaseComment = await caseClient.updateCaseComment(
        caseCommentUuid,
        payload,
      )
      for (let i = 0; i < caseComments.value.length; ++i) {
        if (caseComments.value[i].sodar_uuid === apiCaseComment.sodar_uuid) {
          caseComments.value[i] = apiCaseComment
          break
        }
      }
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  /** Destroy a case comment for the current case. */
  const destroyCaseComment = async (caseCommentUuid: string) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      await caseClient.destroyCaseComment(caseCommentUuid)
      for (let i = 0; i < caseComments.value.length; ++i) {
        if (caseComments.value[i].sodar_uuid === caseCommentUuid) {
          caseComments.value.splice(i, 1)
          break
        }
      }
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  /** Get case phenotypes from store. */
  const getCasePhenotypeTerms = (casePhenotypeTermsUuid) => {
    for (const phenotypeTerms of casePhenotypeTerms.value) {
      if (phenotypeTerms.sodar_uuid === casePhenotypeTermsUuid) {
        return phenotypeTerms
      }
    }
  }

  /** Update case phenotype terms via API and in store. */
  const updateCasePhenotypeTerms = async (
    casePhenotypeTermsUuid: string,
    payload: CasePhenotypeTerms,
  ) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      const apiCasePhenotypeTerms = await caseClient.updateCasePhenotypeTerms(
        casePhenotypeTermsUuid,
        payload,
      )
      for (let i = 0; i < casePhenotypeTerms.value.length; ++i) {
        if (casePhenotypeTerms.value[i].sodar_uuid === casePhenotypeTermsUuid) {
          casePhenotypeTerms.value[i] = apiCasePhenotypeTerms
          break
        }
      }
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  /** Create case phenotype terms via API and in store. */
  const createCasePhenotypeTerms = async (
    caseUuid: string,
    payload: CasePhenotypeTerms,
  ) => {
    const caseClient = new CaseClient(csrfToken.value)

    storeState.serverInteractions += 1
    const oldState = storeState.state
    storeState.state = State.Fetching

    try {
      const apiCasePhenotypeTerms = await caseClient.createCasePhenotypeTerms(
        caseUuid,
        payload,
      )
      casePhenotypeTerms.value.push(apiCasePhenotypeTerms)
    } finally {
      storeState.serverInteractions -= 1
      storeState.state = oldState
    }
  }

  return {
    // data / state
    csrfToken,
    storeState,
    caseUuid,
    projectUuid,
    caseObj,
    caseComments,
    geneAnnotations,
    varAnnos,
    varAnnoList,
    varComments,
    varCommentList,
    acmgRatings,
    acmgRatingList,
    svAnnos,
    svAnnoList,
    svComments,
    svCommentList,
    caseAlignmentStats,
    caseVariantStats,
    caseRelatedness,
    casePhenotypeTerms,
    caseAnnotationReleaseInfos,
    caseSvAnnotationReleaseInfos,
    // functions
    initialize,
    updateCase,
    getCaseComment,
    createCaseComment,
    updateCaseComment,
    destroyCaseComment,
    getCasePhenotypeTerms,
    updateCasePhenotypeTerms,
    createCasePhenotypeTerms,
  }
})

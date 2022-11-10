/** Store for case details.
 *
 * This includes user annotations of variants.
 */

import casesApi from '@cases/api/cases.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const buildComputedObjToList = (baseValue) => {
  return computed(() => {
    if (baseValue.value === null) {
      return []
    } else {
      return Object.values(baseValue)
    }
  })
}

export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

export const useCaseDetailsStore = defineStore(
  {
    id: 'caseDetails',
  },
  () => {
    /** The current application state. */
    const storeState = ref(StoreState.initial)
    /** UUID of the case that this store holds annotations for. */
    const caseUuid = ref(null)
    /** The case object. */
    const caseObj = ref(null)

    /** The comments on the case. */
    const caseComments = ref(null)
    /** The per-gene annotation of the case. */
    const geneAnnotations = ref(null)

    /** Object with mapping of variant identifier to variant annotations. */
    const varAnnos = ref(null)
    /** List of all variant annotations. */
    const varAnnoList = buildComputedObjToList(varAnnos)

    /** Object with mapping of variant identifier to variant comment. */
    const varComments = ref(null)
    /** List of all variant comments. */
    const varCommentList = buildComputedObjToList(varComments)

    /** Object with mapping of variant identifier to ACMG ratings. */
    const acmgRatings = ref(null)
    /** List of all ACMG ratings. */
    const acmgRatingList = buildComputedObjToList(acmgRatings)

    /** Object with mapping of SV identifier to SV annotations. */
    const svAnnos = ref(null)
    /** List of all SV annotations. */
    const svAnnoList = buildComputedObjToList(svAnnos)

    /** Object with mapping of SV identifier to variant comment. */
    const svComments = ref(null)
    /** List of all SV comments. */
    const svCommentList = buildComputedObjToList(svComments)

    /** Case alignment stats. */
    const caseAlignmentStats = ref(null)
    /** Case variant stats. */
    const caseVariantStats = ref(null)
    /** Case relatedness. */
    const caseRelatedness = ref(null)
    /** Case phenotype terms. */
    const casePhenotypeTerms = ref(null)
    /** Case annotation release infos. */
    const caseAnnotationReleaseInfos = ref(null)
    /** Case SV annotation release infos. */
    const caseSvAnnotationReleaseInfos = ref(null)

    /** Promise for initialization of the store. */
    const initializeRes = ref(null)

    /** Initialize the store for the given case. */
    const initialize = (caseObj$) => {
      if (
        storeState.value !== 'initial' &&
        caseObj$.sodar_uuid === caseObj.value.sodar_uuid
      ) {
        // only once for each case
        return initializeRes.value
      }

      storeState.value = StoreState.initializing
      const casesStore = useCasesStore()
      casesStore.serverInteractions += 1
      const csrfToken = casesStore.appContext.csrf_token
      initializeRes.value = Promise.all([
        casesApi.listCaseComment(csrfToken, caseObj$.sodar_uuid).then((res) => {
          caseComments.value = res
        }),
        casesApi.fetchVarAnnos(csrfToken, caseObj$.sodar_uuid).then((res) => {
          varAnnos.value = res
        }),
        casesApi.fetchSvAnnos(csrfToken, caseObj$.sodar_uuid).then((res) => {
          svAnnos.value = res
        }),
        casesApi
          .fetchCaseGeneAnnotation(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            geneAnnotations.value = res
          }),
        casesApi
          .fetchCaseVariantStats(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            caseVariantStats.value = Object.fromEntries(
              res.map((line) => [line.sample_name, line])
            )
          }),
        casesApi
          .fetchCaseRelatedness(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            caseRelatedness.value = res
          }),
        casesApi
          .listCasePhenotypeTerms(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            casePhenotypeTerms.value = res
          }),
        casesApi
          .fetchAnnotationReleaseInfos(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            caseAnnotationReleaseInfos.value = res
          }),
        casesApi
          .fetchSvAnnotationReleaseInfos(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            caseSvAnnotationReleaseInfos.value = res
          }),
        casesApi
          .fetchCaseAlignmentStats(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
            if (res.length > 0) {
              caseAlignmentStats.value = res[0]
            } else {
              caseAlignmentStats.value = null
            }
          }),
      ])
        .then(() => {
          caseObj.value = caseObj$
          caseUuid.value = caseUuid
          casesStore.serverInteractions -= 1
          storeState.value = StoreState.active
        })
        .catch((err) => {
          console.error('Problem initializing casesStore store', err)
          casesStore.serverInteractions -= 1
          storeState.value = StoreState.error
        })

      return initializeRes.value
    }

    /** Update the case with the given data. */
    const updateCase = async (payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        caseObj.value = await casesApi.updateCase(
          csrfToken,
          caseObj.value.sodar_uuid,
          payload
        )
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    /** Get case comment by UUID. */
    const getCaseComment = (caseCommentUuid) => {
      for (const obj of caseComments.value) {
        if (obj.sodar_uuid === caseCommentUuid) {
          return obj
        }
      }
      return null
    }

    /** Create a new case comment for the current case. */
    const createCaseComment = async (payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        const apiCaseComment = await casesApi.createCaseComment(
          csrfToken,
          caseObj.value.sodar_uuid,
          payload
        )
        caseComments.value.push(apiCaseComment)
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    /** Update a case comment for the current case. */
    const updateCaseComment = async (caseCommentUuid, payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        const apiCaseComment = await casesApi.updateCaseComment(
          csrfToken,
          caseCommentUuid,
          payload
        )
        for (let i = 0; i < caseComments.value.length; ++i) {
          if (caseComments.value[i].sodar_uuid === apiCaseComment.sodar_uuid) {
            caseComments.value[i] = apiCaseComment
            break
          }
        }
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    /** Destroy a case comment for the current case. */
    const destroyCaseComment = async (caseCommentUuid) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        await casesApi.destroyCaseComment(csrfToken, caseCommentUuid)
        for (let i = 0; i < caseComments.value.length; ++i) {
          if (caseComments.value[i].sodar_uuid === caseCommentUuid) {
            caseComments.value.splice(i, 1)
            break
          }
        }
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    /** Get case phenotypes from store. */
    const getCasePhenotypeTerms = (casePhenotypeTermsUuid) => {
      for (const phenotypeTerms of caseObj.value.phenotype_terms) {
        if (phenotypeTerms.sodar_uuid === casePhenotypeTermsUuid) {
          return phenotypeTerms
        }
      }
    }

    /** Update case phenotype terms via API and in store. */
    const updateCasePhenotypeTerms = async (
      casePhenotypeTermsUuid,
      payload
    ) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        const apiCasePhenotypeTerms = await casesApi.updateCasePhenotypeTerms(
          csrfToken,
          casePhenotypeTermsUuid,
          payload
        )
        for (let i = 0; i < caseObj.value.phenotype_terms.length; ++i) {
          if (
            caseObj.value.phenotype_terms[i].sodar_uuid ===
            casePhenotypeTermsUuid
          ) {
            caseObj.value.phenotype_terms[i] = apiCasePhenotypeTerms
            break
          }
        }
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    /** Create case phenotype terms via API and in store. */
    const createCasePhenotypeTerms = async (caseUuid, payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteractions += 1
      try {
        const apiCasePhenotypeTerms = await casesApi.createCasePhenotypeTerms(
          csrfToken,
          caseUuid,
          payload
        )
        caseObj.value.phenotype_terms.push(apiCasePhenotypeTerms)
      } finally {
        casesStore.serverInteractions -= 1
      }
    }

    return {
      storeState,
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
  }
)

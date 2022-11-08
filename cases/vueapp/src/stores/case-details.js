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

export const useCaseDetailsStore = defineStore(
  {
    id: 'caseDetails',
  },
  () => {
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

    /** Initialize the store for the given case. */
    const initialize = (caseObj$) => {
      // clear out old values
      caseObj.value = null
      caseUuid.value = null
      varAnnos.value = null
      svAnnos.value = null

      const casesStore = useCasesStore()
      casesStore.serverInteraction += 1
      const csrfToken = casesStore.appContext.csrf_token
      Promise.all([
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
      ]).then((_res) => {
        caseObj.value = caseObj$
        caseUuid.value = caseUuid
        casesStore.serverInteraction -= 1
      })
    }

    /** Update the case with the given data. */
    const updateCase = async (payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteraction += 1
      try {
        const apiCase = await casesApi.updateCase(
          csrfToken,
          caseObj.value.sodar_uuid,
          payload
        )
        caseObj.value = apiCase
      } finally {
        casesStore.serverInteraction -= 1
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
      casesStore.serverInteraction += 1
      try {
        const apiCaseComment = await casesApi.createCaseComment(
          csrfToken,
          caseObj.value.sodar_uuid,
          payload
        )
        caseComments.value.push(apiCaseComment)
      } finally {
        casesStore.serverInteraction -= 1
      }
    }

    /** Update a case comment for the current case. */
    const updateCaseComment = async (caseCommentUuid, payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteraction += 1
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
        casesStore.serverInteraction -= 1
      }
    }

    /** Destroy a case comment for the current case. */
    const destroyCaseComment = async (caseCommentUuid) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteraction += 1
      try {
        await casesApi.destroyCaseComment(csrfToken, caseCommentUuid)
        for (let i = 0; i < caseComments.value.length; ++i) {
          if (caseComments.value[i].sodar_uuid === caseCommentUuid) {
            caseComments.value.splice(i, 1)
            break
          }
        }
      } finally {
        casesStore.serverInteraction -= 1
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
      casesStore.serverInteraction += 1
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
        casesStore.serverInteraction -= 1
      }
    }

    /** Create case phenotype terms via API and in store. */
    const createCasePhenotypeTerms = async (caseUuid, payload) => {
      const casesStore = useCasesStore()
      const csrfToken = casesStore.appContext.csrf_token
      casesStore.serverInteraction += 1
      try {
        const apiCasePhenotypeTerms = await casesApi.createCasePhenotypeTerms(
          csrfToken,
          caseUuid,
          payload
        )
        caseObj.value.phenotype_terms.push(apiCasePhenotypeTerms)
      } finally {
        casesStore.serverInteraction -= 1
      }
    }

    return {
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

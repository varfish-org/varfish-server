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
      const csrfToken = casesStore.appContext.csrfToken
      Promise.all([
        casesApi
          .fetchCaseComments(csrfToken, caseObj$.sodar_uuid)
          .then((res) => {
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
    }
  }
)

import variantsApi from '@variants/api/variants.js'
import { VariantValidatorStates } from '@variants/enums'
import { defineStore } from 'pinia'
import { ref } from 'vue'

const emptyAcmgCriteriaRatingTemplate = {
  pvs1: 0,
  ps1: 0,
  ps2: 0,
  ps3: 0,
  ps4: 0,
  pm1: 0,
  pm2: 0,
  pm3: 0,
  pm4: 0,
  pm5: 0,
  pm6: 0,
  pp1: 0,
  pp2: 0,
  pp3: 0,
  pp4: 0,
  pp5: 0,
  ba1: 0,
  bs1: 0,
  bs2: 0,
  bs3: 0,
  bs4: 0,
  bp1: 0,
  bp2: 0,
  bp3: 0,
  bp4: 0,
  bp5: 0,
  bp6: 0,
  bp7: 0,
  class_override: null,
}

export const useVariantDetailsStore = defineStore('variantDetails', () => {
  const csrfToken = ref(null)
  const fetched = ref(false)
  const geneId = ref(null)
  const smallVariant = ref(null)
  const clinvar = ref(null)
  const knownGeneAa = ref(null)
  const effectDetails = ref(null)
  const extraAnnos = ref(null)
  const populations = ref(null)
  const popFreqs = ref(null)
  const inhouseFreq = ref(null)
  const mitochondrialFreqs = ref(null)
  const gene = ref(null)
  const ncbiSummary = ref(null)
  const ncbiGeneRifs = ref(null)
  const variantValidatorResults = ref(null)
  const beaconAddress = ref(null)
  const acmgCriteriaRatingToSubmit = ref({ ...emptyAcmgCriteriaRatingTemplate })
  const setAcmgCriteriaRatingMode = ref(false)
  const acmgCriteriaRatingConflicting = ref(false)
  const variantValidatorState = ref(VariantValidatorStates.Initial)
  const database = ref(null)
  const gridRow = ref(null)
  const gridApi = ref(null)
  const queryDetails = ref(null)
  const acmgCriteriaRating = ref(null)

  const initialize = async (appContext) => {
    csrfToken.value = appContext.csrf_token
  }

  const submitAcmgCriteriaRating = async (csrfToken) => {
    let url, payload, httpMethod
    const acmgCriteriaRatingToSubmitNoAuto = {
      ...acmgCriteriaRatingToSubmit.value,
    }
    delete acmgCriteriaRatingToSubmitNoAuto['class_auto']
    const acmgCriteriaRatingEmpty =
      JSON.stringify(acmgCriteriaRatingToSubmitNoAuto) ===
      JSON.stringify(emptyAcmgCriteriaRatingTemplate)
    if (!acmgCriteriaRating.value && acmgCriteriaRatingEmpty) {
      setAcmgCriteriaRatingMode.value = false
      acmgCriteriaRatingToSubmit.value = {
        ...emptyAcmgCriteriaRatingTemplate,
      }
      return
    }
    if (acmgCriteriaRating.value && acmgCriteriaRatingEmpty) {
      url = `/variants/ajax/acmg-criteria-rating/delete/${acmgCriteriaRating.value.sodar_uuid}/`
      httpMethod = 'DELETE'
    } else if (acmgCriteriaRating.value && !acmgCriteriaRatingEmpty) {
      url = `/variants/ajax/acmg-criteria-rating/update/${acmgCriteriaRating.value.sodar_uuid}/`
      payload = {
        body: JSON.stringify({
          ...acmgCriteriaRatingToSubmit.value,
        }),
      }
      httpMethod = 'PATCH'
    } else {
      url = `/variants/ajax/acmg-criteria-rating/create/${smallVariant.value.case_uuid}/`
      payload = {
        body: JSON.stringify({
          release: smallVariant.value.release,
          chromosome: smallVariant.value.chromosome,
          start: smallVariant.value.start,
          end: smallVariant.value.end,
          bin: smallVariant.value.bin,
          reference: smallVariant.value.reference,
          alternative: smallVariant.value.alternative,
          ...acmgCriteriaRatingToSubmit.value,
        }),
      }
      httpMethod = 'POST'
    }
    const res = await fetch(url, {
      method: httpMethod,
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      ...payload,
    })
    if (res.ok) {
      if (httpMethod === 'DELETE') {
        smallVariant.value.acmg_class_auto = null
        smallVariant.value.acmg_class_override = null
        acmgCriteriaRating.value = null
        acmgCriteriaRatingToSubmit.value = {
          ...emptyAcmgCriteriaRatingTemplate,
        }
      } else {
        acmgCriteriaRating.value = await res.json()
        smallVariant.value.acmg_class_auto = acmgCriteriaRating.value.class_auto
        smallVariant.value.acmg_class_override =
          acmgCriteriaRating.value.class_override
      }
      // Todo: Redrawing shouldn't be required as the data is updated.
      // Todo: However, only the first change is reacted to, not the subsequent changes.
      // setTimeout(function() { gridApi.value.redrawRows({ rows: [gridRow.value] }); }, 0)
      try {
        gridApi.value.redrawRows({ rows: [gridRow.value] })
      } catch (error) {
        // noop
      }
    }
    setAcmgCriteriaRatingMode.value = false
  }

  const fetchVariantDetails = async (
    gridRow$,
    gridApi$,
    smallVariant$,
    database$
  ) => {
    database.value = database$
    gridRow.value = gridRow$
    gridApi.value = gridApi$
    smallVariant.value = smallVariant$
    variantValidatorResults.value = null
    beaconAddress.value = null
    fetched.value = false
    // setFlagsMode.value = false
    setAcmgCriteriaRatingMode.value = false
    variantValidatorState.value = VariantValidatorStates.Initial
    const res = await variantsApi.retrieveVariantDetails(
      csrfToken.value,
      database.value,
      smallVariant.value
    )
    fetched.value = true
    gene.value = res.gene
    clinvar.value = res.clinvar
    populations.value = res.populations
    popFreqs.value = res.pop_freqs
    inhouseFreq.value = res.inhouse_freq
    mitochondrialFreqs.value = res.mitochondrial_freqs
    knownGeneAa.value = res.knownGeneAa
    extraAnnos.value = res.extra_annos
    effectDetails.value = res.effect_details
    acmgCriteriaRating.value = res.acmg_rating

    // resetFlags()
    resetAcmgCriteriaRating()
  }

  const unsetAcmgCriteriaRating = () => {
    acmgCriteriaRatingToSubmit.value = { ...emptyAcmgCriteriaRatingTemplate }
    calculateAcmgCriteriaRating()
  }

  const resetAcmgCriteriaRating = () => {
    if (acmgCriteriaRating.value) {
      acmgCriteriaRatingToSubmit.value.pvs1 = acmgCriteriaRating.value.pvs1
      acmgCriteriaRatingToSubmit.value.ps1 = acmgCriteriaRating.value.ps1
      acmgCriteriaRatingToSubmit.value.ps2 = acmgCriteriaRating.value.ps2
      acmgCriteriaRatingToSubmit.value.ps3 = acmgCriteriaRating.value.ps3
      acmgCriteriaRatingToSubmit.value.ps4 = acmgCriteriaRating.value.ps4
      acmgCriteriaRatingToSubmit.value.pm1 = acmgCriteriaRating.value.pm1
      acmgCriteriaRatingToSubmit.value.pm2 = acmgCriteriaRating.value.pm2
      acmgCriteriaRatingToSubmit.value.pm3 = acmgCriteriaRating.value.pm3
      acmgCriteriaRatingToSubmit.value.pm4 = acmgCriteriaRating.value.pm4
      acmgCriteriaRatingToSubmit.value.pm5 = acmgCriteriaRating.value.pm5
      acmgCriteriaRatingToSubmit.value.pm6 = acmgCriteriaRating.value.pm6
      acmgCriteriaRatingToSubmit.value.pp1 = acmgCriteriaRating.value.pp1
      acmgCriteriaRatingToSubmit.value.pp2 = acmgCriteriaRating.value.pp2
      acmgCriteriaRatingToSubmit.value.pp3 = acmgCriteriaRating.value.pp3
      acmgCriteriaRatingToSubmit.value.pp4 = acmgCriteriaRating.value.pp4
      acmgCriteriaRatingToSubmit.value.pp5 = acmgCriteriaRating.value.pp5
      acmgCriteriaRatingToSubmit.value.ba1 = acmgCriteriaRating.value.ba1
      acmgCriteriaRatingToSubmit.value.bs1 = acmgCriteriaRating.value.bs1
      acmgCriteriaRatingToSubmit.value.bs2 = acmgCriteriaRating.value.bs2
      acmgCriteriaRatingToSubmit.value.bs3 = acmgCriteriaRating.value.bs3
      acmgCriteriaRatingToSubmit.value.bs4 = acmgCriteriaRating.value.bs4
      acmgCriteriaRatingToSubmit.value.bp1 = acmgCriteriaRating.value.bp1
      acmgCriteriaRatingToSubmit.value.bp2 = acmgCriteriaRating.value.bp2
      acmgCriteriaRatingToSubmit.value.bp3 = acmgCriteriaRating.value.bp3
      acmgCriteriaRatingToSubmit.value.bp4 = acmgCriteriaRating.value.bp4
      acmgCriteriaRatingToSubmit.value.bp5 = acmgCriteriaRating.value.bp5
      acmgCriteriaRatingToSubmit.value.bp6 = acmgCriteriaRating.value.bp6
      acmgCriteriaRatingToSubmit.value.bp7 = acmgCriteriaRating.value.bp7
      acmgCriteriaRatingToSubmit.value.class_auto =
        acmgCriteriaRating.value.class_auto
      acmgCriteriaRatingToSubmit.value.class_override =
        acmgCriteriaRating.value.class_override
      calculateAcmgCriteriaRating()
    } else {
      unsetAcmgCriteriaRating()
    }
  }

  const cancelAcmgCriteriaRating = () => {
    resetAcmgCriteriaRating()
    setAcmgCriteriaRatingMode.value = false
  }

  const calculateAcmgCriteriaRating = () => {
    const pvs = acmgCriteriaRatingToSubmit.value.pvs1
    const ps =
      acmgCriteriaRatingToSubmit.value.ps1 +
      acmgCriteriaRatingToSubmit.value.ps2 +
      acmgCriteriaRatingToSubmit.value.ps3 +
      acmgCriteriaRatingToSubmit.value.ps4
    const pm =
      acmgCriteriaRatingToSubmit.value.pm1 +
      acmgCriteriaRatingToSubmit.value.pm2 +
      acmgCriteriaRatingToSubmit.value.pm3 +
      acmgCriteriaRatingToSubmit.value.pm4 +
      acmgCriteriaRatingToSubmit.value.pm5 +
      acmgCriteriaRatingToSubmit.value.pm6
    const pp =
      acmgCriteriaRatingToSubmit.value.pp1 +
      acmgCriteriaRatingToSubmit.value.pp2 +
      acmgCriteriaRatingToSubmit.value.pp3 +
      acmgCriteriaRatingToSubmit.value.pp4 +
      acmgCriteriaRatingToSubmit.value.pp5
    const ba = acmgCriteriaRatingToSubmit.value.ba1
    const bs =
      acmgCriteriaRatingToSubmit.value.bs1 +
      acmgCriteriaRatingToSubmit.value.bs2 +
      acmgCriteriaRatingToSubmit.value.bs3 +
      acmgCriteriaRatingToSubmit.value.bs4
    const bp =
      acmgCriteriaRatingToSubmit.value.bp1 +
      acmgCriteriaRatingToSubmit.value.bp2 +
      acmgCriteriaRatingToSubmit.value.bp3 +
      acmgCriteriaRatingToSubmit.value.bp4 +
      acmgCriteriaRatingToSubmit.value.bp5 +
      acmgCriteriaRatingToSubmit.value.bp6 +
      acmgCriteriaRatingToSubmit.value.bp7
    const isPathogenic =
      (pvs === 1 &&
        (ps >= 1 || pm >= 2 || (pm === 1 && pp === 1) || pp >= 2)) ||
      ps >= 2 ||
      (ps === 1 && (pm >= 3 || (pm >= 2 && pp >= 2) || (pm === 1 && pp >= 4)))
    const isLikelyPathogenic =
      (pvs === 1 && pm === 1) ||
      (ps === 1 && pm >= 1 && pm <= 2) ||
      (ps === 1 && pp >= 2) ||
      pm >= 3 ||
      (pm === 2 && pp >= 2) ||
      (pm === 1 && pp >= 4)
    const isLikelyBenign = (bs >= 1 && bp >= 1) || bp >= 2
    const isBenign = ba > 0 || bs >= 2
    const isConflicting =
      (isPathogenic || isLikelyPathogenic) && (isBenign || isLikelyBenign)
    acmgCriteriaRatingToSubmit.value.class_auto = 3
    if (isPathogenic) {
      acmgCriteriaRatingToSubmit.value.class_auto = 5
    } else if (isLikelyPathogenic) {
      acmgCriteriaRatingToSubmit.value.class_auto = 4
    } else if (isBenign) {
      acmgCriteriaRatingToSubmit.value.class_auto = 1
    } else if (isLikelyBenign) {
      acmgCriteriaRatingToSubmit.value.class_auto = 2
    }
    if (isConflicting) {
      acmgCriteriaRatingToSubmit.value.class_auto = 3
      acmgCriteriaRatingToSubmit.value.valueConflicting = true
    } else {
      acmgCriteriaRatingToSubmit.value.valueConflicting = false
    }
  }

  return {
    // data / state
    csrfToken,
    fetched,
    geneId,
    smallVariant,
    // flags,
    clinvar,
    knownGeneAa,
    effectDetails,
    extraAnnos,
    populations,
    popFreqs,
    inhouseFreq,
    mitochondrialFreqs,
    gene,
    ncbiSummary,
    ncbiGeneRifs,
    variantValidatorResults,
    beaconAddress,
    acmgCriteriaRatingToSubmit,
    setAcmgCriteriaRatingMode,
    acmgCriteriaRatingConflicting,
    variantValidatorState,
    gridRow,
    gridApi,
    queryDetails,
    acmgCriteriaRating,
    // functions
    initialize,
    submitAcmgCriteriaRating,
    unsetAcmgCriteriaRating,
    resetAcmgCriteriaRating,
    cancelAcmgCriteriaRating,
    calculateAcmgCriteriaRating,
    fetchVariantDetails,
  }
})

import { AnnonarsApiClient } from '@varfish/api/annonars'
import variantsApi from '@variants/api/variants.js'
import { VariantValidatorStates } from '@variants/enums'
import { defineStore } from 'pinia'
import { ref } from 'vue'

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
  /** Gene-related information from annonars. */
  const gene = ref(null)
  /** Variant-related information from annonars. */
  const varAnnos = ref(null)
  const ncbiSummary = ref(null)
  const ncbiGeneRifs = ref(null)
  const variantValidatorResults = ref(null)
  const beaconAddress = ref(null)
  const variantValidatorState = ref(VariantValidatorStates.Initial)
  const database = ref(null)
  const gridRow = ref(null)
  const gridApi = ref(null)
  const queryDetails = ref(null)
  const modalTab = ref('info-tab')

  const initialize = async (appContext) => {
    csrfToken.value = appContext.csrf_token
  }

  const fetchVariantDetails = async (smallVariantRecord$, database$) => {
    database.value = database$
    smallVariant.value = smallVariantRecord$.payload
    variantValidatorResults.value = null
    beaconAddress.value = null
    fetched.value = false
    variantValidatorState.value = VariantValidatorStates.Initial

    const annonarsClient = new AnnonarsApiClient(csrfToken.value)

    await Promise.all([
      annonarsClient
        .retrieveGeneInfos([smallVariantRecord$.payload.hgnc_id])
        .then((result) => {
          gene.value = result[0]
        }),
      annonarsClient
        .retrieveVariantAnnos(
          smallVariantRecord$.release.toLowerCase(),
          smallVariantRecord$.chromosome,
          smallVariantRecord$.start,
          smallVariantRecord$.reference,
          smallVariantRecord$.alternative
        )
        .then((result) => {
          varAnnos.value = result.result
        }),
      variantsApi
        .retrieveVariantDetails(
          csrfToken.value,
          database.value,
          smallVariant.value
        )
        .then((res) => {
          fetched.value = true
          clinvar.value = res.clinvar
          populations.value = res.populations
          popFreqs.value = res.pop_freqs
          inhouseFreq.value = res.inhouse_freq
          mitochondrialFreqs.value = res.mitochondrial_freqs
          knownGeneAa.value = res.knownGeneAa
          extraAnnos.value = res.extra_annos
          effectDetails.value = res.effect_details
        }),
    ])
  }

  return {
    // data / state
    csrfToken,
    fetched,
    geneId,
    smallVariant,
    clinvar,
    knownGeneAa,
    effectDetails,
    extraAnnos,
    populations,
    popFreqs,
    inhouseFreq,
    mitochondrialFreqs,
    gene,
    varAnnos,
    ncbiSummary,
    ncbiGeneRifs,
    variantValidatorResults,
    beaconAddress,
    variantValidatorState,
    gridRow,
    gridApi,
    queryDetails,
    modalTab,
    // functions
    initialize,
    fetchVariantDetails,
  }
})

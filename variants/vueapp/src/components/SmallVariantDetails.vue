<template>
  <div style="font-size: 0.9em">
    <div class="card">
      <div class="card-header" style="font-size: 1.2em">
        <ul class="nav nav-pills">
          <li class="nav-item" role="presentation">
            <a
              class="nav-link active"
              id="info-tab"
              data-toggle="tab"
              data-target="#info"
              type="button"
              role="tab"
              aria-controls="info"
              aria-selected="true"
            >
              Info
            </a>
          </li>
          <li class="nav-item" role="presentation">
            <a
              class="nav-link"
              id="comments-flags-tab"
              data-toggle="tab"
              data-target="#comments-flags"
              type="button"
              role="tab"
              aria-controls="comments-flags"
              aria-selected="false"
            >
              Comments & Flags
            </a>
          </li>
          <li class="nav-item" role="presentation">
            <a
              class="nav-link"
              id="acmg-rating-tab"
              data-toggle="tab"
              data-target="#acmg-rating"
              type="button"
              role="tab"
              aria-controls="acmg-rating"
              aria-selected="false"
            >
              ACMG Rating
            </a>
          </li>
          <li class="nav-item" role="presentation">
            <a
              class="nav-link"
              id="second-hit-tab"
              data-toggle="tab"
              data-target="#second-hit"
              type="button"
              role="tab"
              aria-controls="second-hit"
              aria-selected="false"
            >
              Second Hit
            </a>
          </li>
          <li class="nav-item" role="presentation">
            <a
              class="nav-link"
              id="other-carriers-tab"
              data-toggle="tab"
              data-target="#other-carriers"
              type="button"
              role="tab"
              aria-controls="other-carriers"
              aria-selected="false"
            >
              Other Carriers
            </a>
          </li>
          <li class="nav-item" role="presentation">
            <a
              class="nav-link"
              id="variant-validator-tab"
              data-toggle="tab"
              data-target="#variant-validator"
              type="button"
              role="tab"
              aria-controls="variant-validator"
              aria-selected="false"
            >
              Variant Validator
            </a>
          </li>
        </ul>
      </div>
      <div class="card-body">
        <div class="tab-content">
          <div
            class="tab-pane fade show active"
            id="info"
            role="tabpanel"
            aria-labelledby="info-tab"
          >
            <SmallVariantDetailsLinkOuts
              :gene="detailsStore.gene"
              :small-variant="detailsStore.smallVariant"
              :hgmd-pro-enabled="queryStore.hgmdProEnabled"
              :hgmd-pro-prefix="queryStore.hgmdProPrefix"
              :umd-predictor-api-token="queryStore.umdPredictorApiToken"
            />
            <div class="row">
              <div class="col-12 col-xl-6 pl-0 pr-2">
                <SmallVariantDetailsGene
                  :gene="detailsStore.gene"
                  :ncbi-summary="detailsStore.ncbiSummary"
                  :ncbi-gene-rifs="detailsStore.ncbiGeneRifs"
                  :small-variant="detailsStore.smallVariant"
                />
              </div>
              <div class="col-12 col-xl-6 pl-2 pr-0">
                <SmallVariantDetailsGa4ghBeacons
                  v-if="queryStore.ga4ghBeaconNetworkWidgetEnabled"
                  :small-variant="detailsStore.smallVariant"
                />
                <SmallVariantDetailsClinvar />
                <SmallVariantDetailsFreqs
                  v-if="
                    (detailsStore.populations && detailsStore.popFreqs) ||
                    detailsStore.mitochondrialFreqs
                  "
                  :small-variant="detailsStore.smallVariant"
                  :mitochondrial-freqs="detailsStore.mitochondrialFreqs"
                  :populations="detailsStore.populations"
                  :inhouse-freq="detailsStore.inhouseFreq"
                  :pop-freqs="detailsStore.popFreqs"
                />
                <SmallVariantDetailsExtraAnnos
                  :extra-annos="detailsStore.extraAnnos"
                />
              </div>
            </div>
            <div class="row">
              <div class="col-12 col-xl-6 pl-0 pr-2">
                <SmallVariantDetailsTranscripts
                  :effect-details="detailsStore.effectDetails"
                />
              </div>
              <div class="col-12 col-xl-6 pl-2 pr-0">
                <SmallVariantDetailsCallDetails
                  :case-description="queryStore.case"
                  :small-variant="detailsStore.smallVariant"
                />
              </div>
            </div>
            <div class="row">
              <div class="col-12 pl-0 pr-0">
                <SmallVariantDetailsConservation
                  v-if="detailsStore.knownGeneAa"
                  :known-gene-aa="detailsStore.knownGeneAa"
                />
              </div>
            </div>
          </div>
          <div
            class="tab-pane fade"
            id="comments-flags"
            role="tabpanel"
            aria-labelledby="comments-flags-tab"
          >
            <SmallVariantDetailsCommentsFlags />
          </div>
          <div
            class="tab-pane fade"
            id="acmg-rating"
            role="tabpanel"
            aria-labelledby="acmg-rating-tab"
          >
            <SmallVariantDetailsAcmgRating />
          </div>
          <div
            class="tab-pane fade"
            id="second-hit"
            role="tabpanel"
            aria-labelledby="second-hit-tab"
          >
            <div class="alert alert-secondary">
              <i-mdi-clock />
              Work in progress ...
            </div>
          </div>
          <div
            class="tab-pane fade"
            id="other-carriers"
            role="tabpanel"
            aria-labelledby="other-carriers-tab"
          >
            <div class="alert alert-secondary">
              <i-mdi-clock />
              Work in progress ...
            </div>
          </div>
          <div
            class="tab-pane fade"
            id="variant-validator"
            role="tabpanel"
            aria-labelledby="variant-validator-tab"
          >
            <SmallVariantDetailsVariantValidator
              :small-variant="detailsStore.smallVariant"
              v-model:variant-validator-state="
                detailsStore.variantValidatorState
              "
              v-model:variant-validator-results="
                detailsStore.variantValidatorResults
              "
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SmallVariantDetailsCallDetails from './SmallVariantDetailsCallDetails.vue'
import SmallVariantDetailsClinvar from './SmallVariantDetailsClinvar.vue'
import SmallVariantDetailsCommentsFlags from './SmallVariantDetailsCommentsFlags.vue'
import SmallVariantDetailsConservation from './SmallVariantDetailsConservation.vue'
import SmallVariantDetailsExtraAnnos from './SmallVariantDetailsExtraAnnos.vue'
import SmallVariantDetailsFreqs from './SmallVariantDetailsFreqs.vue'
import SmallVariantDetailsGa4ghBeacons from './SmallVariantDetailsGa4ghBeacons.vue'
import SmallVariantDetailsGene from './SmallVariantDetailsGene.vue'
import SmallVariantDetailsTranscripts from './SmallVariantDetailsTranscripts.vue'
import SmallVariantDetailsVariantValidator from './SmallVariantDetailsVariantValidator.vue'
import SmallVariantDetailsAcmgRating from './SmallVariantDetailsAcmgRating.vue'
import SmallVariantDetailsLinkOuts from './SmallVariantDetailsLinkOuts.vue'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { useFilterQueryStore } from '@variants/stores/filterQuery'

export default {
  components: {
    SmallVariantDetailsCallDetails,
    SmallVariantDetailsClinvar,
    SmallVariantDetailsCommentsFlags,
    SmallVariantDetailsConservation,
    SmallVariantDetailsExtraAnnos,
    SmallVariantDetailsFreqs,
    SmallVariantDetailsGa4ghBeacons,
    SmallVariantDetailsGene,
    SmallVariantDetailsTranscripts,
    SmallVariantDetailsVariantValidator,
    SmallVariantDetailsAcmgRating,
    SmallVariantDetailsLinkOuts,
  },
  setup() {
    const detailsStore = useVariantDetailsStore()
    const queryStore = useFilterQueryStore()
    return {
      detailsStore,
      queryStore,
    }
  },
}
</script>

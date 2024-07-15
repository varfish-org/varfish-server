<script setup>
import Overlay from '@/varfish/components/Overlay.vue'
import FilterFormGenotypePane from '@/variants/components/FilterForm//GenotypePane.vue'
import FilterFormFrequencyPane from '@/variants/components/FilterForm//FrequencyPane.vue'
import FilterFormFooter from '@/variants/components/FilterForm//Footer.vue'
import FilterFormPriotizationPane from '@/variants/components/FilterForm//PrioritizationPane.vue'
import FilterFormEffectPane from '@/variants/components/FilterForm//EffectPane.vue'
import FilterFormClinvarPane from '@/variants/components/FilterForm//ClinvarPane.vue'
import FilterFormGenesRegionsPane from '@/variants/components/FilterForm//GenesRegionsPane.vue'
import FilterFormFlagsPane from '@/variants/components/FilterForm//FlagsPane.vue'
import FilterFormDevPane from '@/varfish/components/FilterForm//DevPane.vue'
import FilterFormQualityPane from '@/variants/components/FilterForm//QualityPane.vue'
import FilterFormQuickPresets from '@/variants/components/FilterForm//QuickPresets.vue'
import { QueryStates } from '@/variants/enums'
import { computed, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'

const variantQueryStore = useVariantQueryStore()
const caseDetailsStore = useCaseDetailsStore()

const genotypePaneRef = ref(null)
const frequencyPaneRef = ref(null)
const prioritizationPaneRef = ref(null)
const effectPaneRef = ref(null)
const qualityPaneRef = ref(null)
const genePaneRef = ref(null)

const makePaneHasError = (pane) =>
  computed(() => {
    return pane.value && pane.value.v$ && pane.value.v$.$error
  })

const genotypeHasError = makePaneHasError(genotypePaneRef)
const frequencyHasError = makePaneHasError(frequencyPaneRef)
const prioritizationHasError = makePaneHasError(prioritizationPaneRef)
const effectHasError = makePaneHasError(effectPaneRef)
const qualityHasError = makePaneHasError(qualityPaneRef)
const geneHasError = computed(() => {
  return genePaneRef.value && !genePaneRef.value.isValid()
})

const anyHasError = computed(() => {
  return (
    genotypeHasError.value ||
    frequencyHasError.value ||
    prioritizationHasError.value ||
    effectHasError.value ||
    qualityHasError.value ||
    geneHasError.value
  )
})

const v$ = useVuelidate()

const showOverlay = computed(() =>
  ['initial', 'initializing'].includes(variantQueryStore.storeState),
)

var eventMethod = window.addEventListener ? 'addEventListener' : 'attachEvent'
var eventer = window[eventMethod]
var messageEvent = eventMethod == 'attachEvent' ? 'onmessage' : 'message'
var imageRes

// Listen to message from child window
eventer(
  messageEvent,
  function (event) {
    var key = event.message ? 'jsonRes' : 'data'
    imageRes = event[key]

    if (event.origin == 'http://127.0.0.1:7000') {
      if (JSON.stringify(imageRes).includes('gene_entrez_id')) {
        variantQueryStore.querySettings.prio_gm = JSON.stringify(imageRes)
      } else if (JSON.stringify(imageRes).includes('ImageName')) {
        variantQueryStore.querySettings.photo_file =
          JSON.stringify(imageRes).split(':')[1]
      }
    }
  },
  false,
)

const onSubmitCancelButtonClicked = () => {
  const cancelableStates = [
    QueryStates.Running.value,
    QueryStates.Resuming.value,
    QueryStates.Finished.value,
    QueryStates.Fetching.value,
  ]
  if (cancelableStates.includes(variantQueryStore.queryState)) {
    variantQueryStore.cancelQuery()
  } else {
    variantQueryStore.submitQuery()
  }
}
</script>

<template>
  <form id="filterForm" method="post" class="position-relative">
    <div
      v-if="
        variantQueryStore.querySettings !== null &&
        variantQueryStore.querySettingsPreset !== null
      "
      class="card"
      :class="{ 'border-danger': v$.$error || geneHasError }"
    >
      <div class="card-header">
        <FilterFormQuickPresets
          :show-filtration-inline-help="
            variantQueryStore.showFiltrationInlineHelp
          "
          :quick-presets="variantQueryStore.quickPresets"
          :category-presets="variantQueryStore.categoryPresets"
          :query-settings="variantQueryStore.querySettings"
          :case="caseDetailsStore.caseObj"
        />
      </div>
      <div class="card-header row border-bottom-1 pt-1 pr-1">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a
              id="genotype-tab"
              class="nav-link active"
              :class="{ 'border-danger text-danger': genotypeHasError }"
              data-toggle="tab"
              href="#panel-genotype"
              role="tab"
              title="Require genotypes in individuals"
            >
              Genotype
              <i-mdi-alert-circle-outline v-if="genotypeHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="frequency-tab"
              class="nav-link"
              :class="{ 'texborder-danger -danger': frequencyHasError }"
              data-toggle="tab"
              href="#panel-frequency"
              role="tab"
              title="Population frequencies and het./hom. counts"
            >
              Frequency
              <i-mdi-alert-circle-outline v-if="frequencyHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="prioritization-tab"
              class="nav-link"
              :class="{ 'border-danger text-danger': prioritizationHasError }"
              data-toggle="tab"
              href="#panel-prioritization"
              role="tab"
              title="Configure variant prioritization"
            >
              Prioritization
              <i-mdi-alert-circle-outline v-if="prioritizationHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="effect-tab"
              class="nav-link"
              :class="{ 'text-danger': effectHasError }"
              data-toggle="tab"
              href="#panel-effect"
              role="tab"
              title="Variant types/effects, coding/non-coding transcripts"
            >
              Variants &amp; Effects
              <i-mdi-alert-circle-outline v-if="effectHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="quality-tab"
              class="nav-link"
              :class="{ 'text-danger': qualityHasError }"
              data-toggle="tab"
              href="#panel-quality"
              role="tab"
              title="Quality, allelic balance, coverage"
            >
              Quality
              <i-mdi-alert-circle-outline v-if="qualityHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="clinvar-tab"
              class="nav-link"
              data-toggle="tab"
              href="#panel-clinvar"
              role="tab"
              title="Filter based on ClinVar"
            >
              ClinVar
            </a>
          </li>
          <li class="nav-item">
            <a
              id="allowlist-tab"
              class="nav-link"
              :class="{ 'text-danger': geneHasError }"
              data-toggle="tab"
              href="#panel-allowlist"
              role="tab"
              title="Allow-list genes and genomic regions"
            >
              Gene Lists &amp; Regions
              <i-mdi-alert-circle-outline v-if="geneHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              id="flags-tab"
              class="nav-link"
              data-toggle="tab"
              href="#panel-flags"
              role="tab"
              title="Filter for user flags and comments"
            >
              Flags &amp; Comments
            </a>
          </li>
          <li
            v-if="variantQueryStore.filtrationComplexityMode === 'dev'"
            class="nav-item"
          >
            <a
              id="dev-tab"
              class="nav-link"
              data-toggle="tab"
              href="#panel-dev"
              role="tab"
              title="Developer settings"
            >
              Developer Settings
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body p-0">
        <div class="tab-content">
          <div
            id="panel-genotype"
            ref="genotypePaneRef"
            class="tab-pane fade show active"
            role="tabpanel"
            aria-labelledby="genotype-tab"
          >
            <FilterFormGenotypePane
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
              :case="caseDetailsStore.caseObj"
            />
          </div>
          <div
            id="panel-frequency"
            ref="frequencyPaneRef"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="frequency-tab"
          >
            <FilterFormFrequencyPane
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
              :case="caseDetailsStore.caseObj"
              :query-settings="variantQueryStore.querySettings"
            />
          </div>
          <div
            id="panel-prioritization"
            ref="prioritizationPaneRef"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="prioritization-tab"
          >
            <FilterFormPriotizationPane
              v-model:pedia-enabled="
                variantQueryStore.querySettings.pedia_enabled
              "
              v-model:patho-enabled="
                variantQueryStore.querySettings.patho_enabled
              "
              v-model:patho-score="variantQueryStore.querySettings.patho_score"
              :csrf-token="variantQueryStore.csrfToken"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :exomiser-enabled="variantQueryStore.exomiserEnabled"
              :cadd-enabled="variantQueryStore.caddEnabled"
              :cada-enabled="variantQueryStore.cadaEnabled"
              v-model:prio-enabled="
                variantQueryStore.querySettings.prio_enabled
              "
              v-model:prio-algorithm="
                variantQueryStore.querySettings.prio_algorithm
              "
              v-model:prio-hpo-terms="
                variantQueryStore.querySettings.prio_hpo_terms
              "
              v-model:prio-gm="variantQueryStore.querySettings.prio_gm"
              v-model:photo-file="variantQueryStore.querySettings.photo_file"
              v-model:gm-enabled="variantQueryStore.querySettings.gm_enabled"
            />
          </div>
          <div
            id="panel-effect"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="effect-tab"
          >
            <FilterFormEffectPane
              ref="effectPaneRef"
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-quality"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="quality-tab"
          >
            <FilterFormQualityPane
              ref="qualityPaneRef"
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
              :case-obj="caseDetailsStore.caseObj"
            />
          </div>
          <div
            id="panel-allowlist"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="allowlist-tab"
          >
            <FilterFormGenesRegionsPane
              ref="genePaneRef"
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-flags"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="flags-tab"
          >
            <FilterFormFlagsPane
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-clinvar"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="clinvar-tab"
          >
            <FilterFormClinvarPane
              v-model:query-settings="variantQueryStore.querySettings"
              :show-filtration-inline-help="
                variantQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                variantQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            v-if="variantQueryStore.filtrationComplexityMode === 'dev'"
            id="panel-dev"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="dev-tab"
          >
            <FilterFormDevPane
              v-model:query-settings="variantQueryStore.querySettings"
            />
          </div>
        </div>
        <FilterFormFooter
          v-model:database="variantQueryStore.querySettings.database"
          :query-state="variantQueryStore.queryState"
          :any-has-error="anyHasError"
          :filtration-complexity-mode="
            variantQueryStore.filtrationComplexityMode
          "
          @submit-cancel-button-click="onSubmitCancelButtonClicked()"
        />
      </div>
    </div>
    <div v-else class="alert alert-info">
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2">Loading filter form ...</strong>
    </div>
    <Overlay
      v-if="showOverlay"
      :message="variantQueryStore.storeStateMessage"
    />
  </form>
</template>

<style>
footer.sodar-footer,
.sodar-sub-navbar-container {
  display: none;
}
</style>

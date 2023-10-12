<script setup>
import Overlay from '@varfish/components/Overlay.vue'
import SvFilterFormGenotypePane from '@svs/components/SvFilterForm/GenotypePane.vue'
import SvFilterFormCriteriaDefinitionPane from '@svs/components/SvFilterForm/CriteriaDefinitionPane.vue'
import SvFilterFormFrequencyPane from '@svs/components/SvFilterForm/FrequencyPane.vue'
import SvFilterFormImpactPane from '@svs/components/SvFilterForm/ImpactPane.vue'
import SvFilterFormGenesRegionsPane from '@svs/components/SvFilterForm/GenesRegionsPane.vue'
import SvFilterFormRegulatoryPane from '@svs/components/SvFilterForm/RegulatoryPane.vue'
import SvFilterFormQuickPresets from '@svs/components/SvFilterForm/QuickPresets.vue'
import SvFilterFormTadsPane from '@svs/components/SvFilterForm/TadsPane.vue'
import SvFilterFormPatho from '@svs/components/SvFilterForm/Patho.vue'
import SvFilterFormDev from '@svs/components/SvFilterForm/Dev.vue'
import SvFilterFormFooter from '@svs/components/SvFilterForm/Footer.vue'
import { QueryStates } from '@variants/enums'
import { computed, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { useSvQueryStore } from '@svs/stores/svQuery'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'

const svQueryStore = useSvQueryStore()
const caseDetailsStore = useCaseDetailsStore()

const criteriaMatchesPaneRef = ref(null)
const criteriaDefsPaneRef = ref(null)
const frequencyPaneRef = ref(null)
const effectPaneRef = ref(null)
const regulatoryPaneRef = ref(null)
const tadsPaneRef = ref(null)
const genePaneRef = ref(null)
const pathoPaneRef = ref(null)
const devPaneRef = ref(null)

const makePaneHasError = (pane) =>
  computed(() => {
    return pane.value && pane.value.v$ && pane.value.v$.$error
  })

const criteriaMatchesHasError = makePaneHasError(criteriaMatchesPaneRef)
const criteriaDefsHasError = makePaneHasError(criteriaDefsPaneRef)
const frequencyHasError = makePaneHasError(frequencyPaneRef)
const effectHasError = makePaneHasError(effectPaneRef)
const regulatoryHasError = makePaneHasError(regulatoryPaneRef)
const tadsHasError = makePaneHasError(tadsPaneRef)
const pathoHasError = makePaneHasError(pathoPaneRef)
const geneHasError = computed(() => {
  return genePaneRef.value && !genePaneRef.value.isValid()
})

const anyHasError = computed(() => {
  return (
    effectHasError.value ||
    geneHasError.value ||
    criteriaDefsHasError.value ||
    frequencyHasError.value ||
    tadsHasError.value ||
    regulatoryHasError.value ||
    tadsHasError.value
  )
})

const v$ = useVuelidate()

const showOverlay = computed(() =>
  ['initial', 'initializing'].includes(svQueryStore.storeState),
)

const onSubmitCancelButtonClicked = () => {
  const cancelableStates = [
    QueryStates.Running.value,
    QueryStates.Resuming.value,
    QueryStates.Finished.value,
    QueryStates.Fetching.value,
  ]
  if (cancelableStates.includes(svQueryStore.queryState)) {
    svQueryStore.cancelQuery()
  } else {
    svQueryStore.submitQuery()
  }
}
</script>

<template>
  <form class="position-relative">
    <div
      class="card"
      v-if="
        svQueryStore.querySettings !== null &&
        svQueryStore.querySettingsPreset !== null
      "
      :class="{ 'border-danger': v$.$error || geneHasError }"
    >
      <div class="card-header">
        <SvFilterFormQuickPresets
          :show-filtration-inline-help="svQueryStore.showFiltrationInlineHelp"
          :quick-presets="svQueryStore.quickPresets"
          :category-presets="svQueryStore.categoryPresets"
          :query-settings="svQueryStore.querySettings"
          :case="caseDetailsStore.caseObj"
        />
      </div>
      <div class="card-header row border-bottom-1 pt-1 pr-1">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a
              class="nav-link active"
              :class="{ 'border-danger text-danger': criteriaMatchesHasError }"
              id="criteria-matches-tab"
              data-toggle="tab"
              href="#panel-criteria-matches"
              role="tab"
              title="Filter criteria matches"
            >
              Genotypes
              <i-mdi-alert-circle-outline v-if="criteriaMatchesHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ 'border-danger text-danger': criteriaDefsHasError }"
              id="criteria-defs-tab"
              data-toggle="tab"
              href="#panel-criteria-defs"
              role="tab"
              title="Filter criteria definitions"
            >
              Genotype Criterias
              <i-mdi-alert-circle-outline v-if="criteriaDefsHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ 'border-danger text-danger': frequencyHasError }"
              id="frequency-tab"
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
              class="nav-link"
              :class="{ 'border-danger text-danger': geneHasError }"
              id="blocklist-tab"
              data-toggle="tab"
              href="#panel-blocklist"
              role="tab"
              title="Allow-list and block-list genes and genomic regions"
            >
              Gene Lists &amp; Regions
              <i-mdi-alert-circle-outline v-if="geneHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              :class="{ 'text-danger': effectHasError }"
              id="effect-tab"
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
              class="nav-link"
              :class="{ 'text-danger': tadsHasError }"
              id="regulatory-tab"
              data-toggle="tab"
              href="#panel-regulatory"
              role="tab"
              title="Regulatory elements"
            >
              Regulatory
            </a>
          </li>
          <li class="nav-item">
            <a
              ref="tadsPaneRef"
              class="nav-link"
              :class="{ 'text-danger': tadsHasError }"
              id="tads-tab"
              data-toggle="tab"
              href="#panel-tads"
              role="tab"
              title="Configure TADs annotation"
              data-placement="left"
            >
              TADs
              <i-mdi-alert-circle-outline v-if="tadsHasError" />
            </a>
          </li>
          <li class="nav-item">
            <a
              ref="pathoPaneRef"
              class="nav-link"
              :class="{ 'text-danger': pathoHasError }"
              id="tads-tab"
              data-toggle="tab"
              href="#panel-patho"
              role="tab"
              title="Configure ClinVar/known pathologic SVs annotation"
              data-placement="left"
            >
              ClinVar &amp; Known Patho. SVs
              <i-mdi-alert-circle-outline v-if="pathoHasError" />
            </a>
          </li>
          <li
            class="nav-item"
            v-if="svQueryStore.filtrationComplexityMode === 'dev'"
          >
            <a
              ref="devPaneRef"
              class="nav-link"
              id="tads-tab"
              data-toggle="tab"
              href="#panel-dev"
              role="tab"
              title="Perform changes in JSON (wear a hard hat!)"
              data-placement="left"
            >
              Developer Settings
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body p-0">
        <div class="tab-content">
          <div
            ref="criteriaMatchesPaneRef"
            class="tab-pane fade show active"
            id="panel-criteria-matches"
            role="tabpanel"
            aria-labelledby="criteria-matches-tab"
          >
            <SvFilterFormGenotypePane
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              :case-obj="caseDetailsStore.caseObj"
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            ref="criteriaDefsPaneRef"
            class="tab-pane fade"
            id="panel-criteria-defs"
            role="tabpanel"
            aria-labelledby="criteria-defs-tab"
          >
            <SvFilterFormCriteriaDefinitionPane
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            ref="frequencyPaneRef"
            class="tab-pane fade"
            id="panel-frequency"
            role="tabpanel"
            aria-labelledby="frequency-tab"
          >
            <SvFilterFormFrequencyPane
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              :case="caseDetailsStore.caseObj"
              :query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-effect"
            role="tabpanel"
            aria-labelledby="effect-tab"
          >
            <SvFilterFormImpactPane
              ref="effectPaneRef"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-blocklist"
            role="tabpanel"
            aria-labelledby="blocklist-tab"
          >
            <SvFilterFormGenesRegionsPane
              ref="genePaneRef"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-regulatory"
            role="tabpanel"
            aria-labelledby="regulatory-tab"
          >
            <SvFilterFormRegulatoryPane
              ref="regulatoryPaneRef"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-tads"
            role="tabpanel"
            aria-labelledby="tads-tab"
          >
            <SvFilterFormTadsPane
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-patho"
            role="tabpanel"
            aria-labelledby="tads-tab"
          >
            <SvFilterFormPatho
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-dev"
            role="tabpanel"
            aria-labelledby="dev-tab"
          >
            <SvFilterFormDev
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
        </div>
        <SvFilterFormFooter
          :query-state="svQueryStore.queryState"
          :any-has-error="anyHasError"
          :filtration-complexity-mode="svQueryStore.filtrationComplexityMode"
          v-model:database="svQueryStore.querySettings.database"
          @submit-cancel-button-click="onSubmitCancelButtonClicked()"
        />
      </div>
    </div>
    <div v-else class="alert alert-info">
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2">Loading filter form ...</strong>
    </div>
    <Overlay v-if="showOverlay" :message="svQueryStore.storeStateMessage" />
  </form>
</template>

<style>
footer.sodar-footer,
.sodar-sub-navbar-container {
  display: none;
}
</style>

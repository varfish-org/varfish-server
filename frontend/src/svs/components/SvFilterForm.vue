<script setup>
import Overlay from '@/varfish/components/Overlay.vue'
import SvFilterFormGenotypePane from '@/svs/components/SvFilterForm/GenotypePane.vue'
import SvFilterFormCriteriaDefinitionPane from '@/svs/components/SvFilterForm/CriteriaDefinitionPane.vue'
import SvFilterFormFrequencyPane from '@/svs/components/SvFilterForm/FrequencyPane.vue'
import SvFilterFormImpactPane from '@/svs/components/SvFilterForm/ImpactPane.vue'
import SvFilterFormGenesRegionsPane from '@/svs/components/SvFilterForm/GenesRegionsPane.vue'
import SvFilterFormRegulatoryPane from '@/svs/components/SvFilterForm/RegulatoryPane.vue'
import SvFilterFormQuickPresets from '@/svs/components/SvFilterForm/QuickPresets.vue'
import SvFilterFormTadsPane from '@/svs/components/SvFilterForm/TadsPane.vue'
import SvFilterFormPatho from '@/svs/components/SvFilterForm/Patho.vue'
import SvFilterFormDev from '@/svs/components/SvFilterForm/Dev.vue'
import SvFilterFormFooter from '@/svs/components/SvFilterForm/Footer.vue'
import SvFilterFormDevPane from '@/varfish/components/FilterForm//DevPane.vue'
import { QueryStates } from '@/variants/enums'
import { computed, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { useSvQueryStore } from '@/svs/stores/svQuery'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'

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
const exportPaneRef = ref(null)
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
const exportHasError = makePaneHasError(exportPaneRef)
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
      v-if="
        svQueryStore.querySettings !== null &&
        svQueryStore.querySettingsPreset !== null
      "
      class="card"
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
              id="criteria-matches-tab"
              class="nav-link active"
              :class="{ 'border-danger text-danger': criteriaMatchesHasError }"
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
              id="criteria-defs-tab"
              class="nav-link"
              :class="{ 'border-danger text-danger': criteriaDefsHasError }"
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
              id="frequency-tab"
              class="nav-link"
              :class="{ 'border-danger text-danger': frequencyHasError }"
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
              id="blocklist-tab"
              class="nav-link"
              :class="{ 'border-danger text-danger': geneHasError }"
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
              id="regulatory-tab"
              class="nav-link"
              :class="{ 'text-danger': tadsHasError }"
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
              id="tads-tab"
              ref="tadsPaneRef"
              class="nav-link"
              :class="{ 'text-danger': tadsHasError }"
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
              id="tads-tab"
              ref="pathoPaneRef"
              class="nav-link"
              :class="{ 'text-danger': pathoHasError }"
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
            v-if="svQueryStore.filtrationComplexityMode === 'dev'"
            class="nav-item"
          >
            <a
              id="tads-tab"
              ref="devPaneRef"
              class="nav-link"
              :class="{ 'text-danger': exportHasError }"
              data-toggle="tab"
              href="#panel-dev"
              role="tab"
              title="Perform changes in JSON (wear a hard hat!)"
              data-placement="left"
            >
              Developer Settings
              <i-mdi-alert-circle-outline v-if="exportHasError" />
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body p-0">
        <div class="tab-content">
          <div
            id="panel-criteria-matches"
            ref="criteriaMatchesPaneRef"
            class="tab-pane fade show active"
            role="tabpanel"
            aria-labelledby="criteria-matches-tab"
          >
            <SvFilterFormGenotypePane
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
              :case-obj="caseDetailsStore.caseObj"
            />
          </div>
          <div
            id="panel-criteria-defs"
            ref="criteriaDefsPaneRef"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="criteria-defs-tab"
          >
            <SvFilterFormCriteriaDefinitionPane
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-frequency"
            ref="frequencyPaneRef"
            class="tab-pane fade"
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
            id="panel-effect"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="effect-tab"
          >
            <SvFilterFormImpactPane
              ref="effectPaneRef"
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-blocklist"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="blocklist-tab"
          >
            <SvFilterFormGenesRegionsPane
              ref="genePaneRef"
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-regulatory"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="regulatory-tab"
          >
            <SvFilterFormRegulatoryPane
              ref="regulatoryPaneRef"
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-tads"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="tads-tab"
          >
            <SvFilterFormTadsPane
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            id="panel-patho"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="tads-tab"
          >
            <SvFilterFormPatho
              v-model:query-settings="svQueryStore.querySettings"
              :show-filtration-inline-help="
                svQueryStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svQueryStore.filtrationComplexityMode
              "
            />
          </div>
          <div
            v-if="svQueryStore.filtrationComplexityMode === 'dev'"
            id="panel-dev"
            class="tab-pane fade"
            role="tabpanel"
            aria-labelledby="dev-tab"
          >
            <SvFilterFormDevPane
              v-model:query-settings="svQueryStore.querySettings"
            />
          </div>
        </div>
        <SvFilterFormFooter
          v-model:database="svQueryStore.querySettings.database"
          :query-state="svQueryStore.queryState"
          :any-has-error="anyHasError"
          :filtration-complexity-mode="svQueryStore.filtrationComplexityMode"
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

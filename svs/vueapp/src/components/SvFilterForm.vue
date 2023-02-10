<script setup>
import Overlay from '@varfish/components/Overlay.vue'
import SvFilterFormGenotypePane from './SvFilterFormGenotypePane.vue'
import SvFilterFormCriteriaDefinitionPane from './SvFilterFormCriteriaDefinitionPane.vue'
import SvFilterFormFrequencyPane from './SvFilterFormFrequencyPane.vue'
import SvFilterFormImpactPane from './SvFilterFormImpactPane.vue'
import SvFilterFormGenesRegionsPane from './SvFilterFormGenesRegionsPane.vue'
import SvFilterFormRegulatoryPane from './SvFilterFormRegulatoryPane.vue'
import SvFilterFormQuickPresets from './SvFilterFormQuickPresets.vue'
import SvFilterFormTadsPane from './SvFilterFormTadsPane.vue'
import SvFilterFormPatho from './SvFilterFormPatho.vue'
import SvFilterFormFooter from './SvFilterFormFooter.vue'
import { QueryStates } from '@variants/enums.js'
import { computed, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { useSvFilterStore } from '@svs/stores/filterSvs.js'

const svFilterStore = useSvFilterStore()

const criteriaMatchesPaneRef = ref(null)
const criteriaDefsPaneRef = ref(null)
const frequencyPaneRef = ref(null)
const effectPaneRef = ref(null)
const regulatoryPaneRef = ref(null)
const tadsPaneRef = ref(null)
const genePaneRef = ref(null)
const pathoPaneRef = ref(null)

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

const moreHasError = computed(() => {
  return regulatoryHasError.value || tadsHasError.value
})

const anyHasError = computed(() => {
  return (
    effectHasError.value ||
    geneHasError.value ||
    criteriaDefsHasError.value ||
    frequencyHasError.value ||
    tadsHasError.value ||
    moreHasError.value
  )
})

const v$ = useVuelidate()

const showOverlay = computed(() =>
  ['initial', 'initializing'].includes(svFilterStore.storeState)
)

const onSubmitCancelButtonClicked = () => {
  const cancelableStates = [
    QueryStates.Running.value,
    QueryStates.Resuming.value,
    QueryStates.Finished.value,
    QueryStates.Fetching.value,
  ]
  if (cancelableStates.includes(svFilterStore.queryState)) {
    svFilterStore.cancelQuery()
  } else {
    svFilterStore.submitQuery()
  }
}
</script>

<template>
  <form class="position-relative">
    <div
      class="card"
      v-if="
        svFilterStore.querySettings !== null &&
        svFilterStore.querySettingsPreset !== null
      "
      :class="{ 'border-danger': v$.$error || geneHasError }"
    >
      <div class="card-header">
        <SvFilterFormQuickPresets
          :show-filtration-inline-help="svFilterStore.showFiltrationInlineHelp"
          :quick-presets="svFilterStore.quickPresets"
          :category-presets="svFilterStore.categoryPresets"
          :query-settings="svFilterStore.querySettings"
          :case="svFilterStore.caseObj"
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
          <li class="nav-item dropdown">
            <a
              class="nav-link dropdown-toggle"
              :class="{ 'text-danger': moreHasError }"
              id="more-tab"
              data-toggle="dropdown"
              href="#"
              role="button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              More ...
              <i-mdi-alert-circle-outline v-if="moreHasError" />
            </a>
            <div class="dropdown-menu" style="z-index: 1030">
              <a
                class="dropdown-item"
                id="regulatory-tab"
                data-toggle="tab"
                href="#panel-regulatory"
                role="tab"
                title="Regulatory elements"
              >
                Regulatory
              </a>
              <a
                ref="tadsPaneRef"
                :class="{ 'text-danger': tadsHasError }"
                class="dropdown-item"
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
              <a
                ref="pathoPaneRef"
                :class="{ 'text-danger': pathoHasError }"
                class="dropdown-item"
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
            </div>
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              :case-obj="svFilterStore.caseObj"
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              :case="svFilterStore.caseObj"
              :query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
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
                svFilterStore.showFiltrationInlineHelp
              "
              :filtration-complexity-mode="
                svFilterStore.filtrationComplexityMode
              "
              v-model:query-settings="svFilterStore.querySettings"
            />
          </div>
        </div>
        <SvFilterFormFooter
          :query-state="svFilterStore.queryState"
          :any-has-error="anyHasError"
          :filtration-complexity-mode="svFilterStore.filtrationComplexityMode"
          v-model:database="svFilterStore.querySettings.database"
          @submit-cancel-button-click="onSubmitCancelButtonClicked()"
        />
      </div>
    </div>
    <div v-else class="alert alert-info">
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2">Loading filter form ...</strong>
    </div>
    <Overlay v-if="showOverlay" :message="svFilterStore.storeStateMessage" />
  </form>
</template>

<style>
footer.sodar-footer,
.sodar-sub-navbar-container {
  display: none;
}
</style>

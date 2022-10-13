<script setup>
import FilterFormGenotypePane from './FilterFormGenotypePane.vue'
import FilterFormFrequencyPane from './FilterFormFrequencyPane.vue'
import FilterFormFooter from './FilterFormFooter.vue'
import FilterFormPriotizationPane from './FilterFormPrioritizationPane.vue'
import FilterFormEffectPane from './FilterFormEffectPane.vue'
import FilterFormClinvarPane from './FilterFormClinvarPane.vue'
import FilterFormGenesRegionsPane from './FilterFormGenesRegionsPane.vue'
import FilterFormFlagsPane from './FilterFormFlagsPane.vue'
import FilterFormDownloadPane from './FilterFormDownloadPane.vue'
import FilterFormQualityPane from './FilterFormQualityPane.vue'
import FilterFormQuickPresets from './FilterFormQuickPresets.vue'
import { computed, reactive, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { useFilterQueryStore } from '../stores/filterQuery'

const store = useFilterQueryStore()

// TODO: export settings not in query for now
const exportSettings = reactive({
  file_type: 'tsv',
  export_flags: true,
  export_comments: true,
  export_donors: store.case.pedigree.map((member) => member.name),
})

const genotypePaneRef = ref(null)
const frequencyPaneRef = ref(null)
const prioritizationPaneRef = ref(null)
const effectPaneRef = ref(null)
const qualityPaneRef = ref(null)
const exportPaneRef = ref(null)
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
const exportHasError = makePaneHasError(exportPaneRef)
const geneHasError = computed(() => {
  return genePaneRef.value && !genePaneRef.value.isValid()
})

const moreHasError = computed(() => {
  return (
    effectHasError.value ||
    qualityHasError.value ||
    geneHasError.value ||
    exportHasError.value
  )
})

const anyHasError = computed(() => {
  return (
    genotypeHasError.value ||
    frequencyHasError.value ||
    prioritizationHasError.value ||
    moreHasError.value
  )
})

const v$ = useVuelidate()
</script>

<template>
  <form id="filterForm" method="post">
    <div
      class="card"
      :class="{ 'border-danger': v$.$error || geneHasError }"
      v-if="store.querySettings !== null && store.querySettingsPreset !== null"
    >
      <div class="card-header">
        <FilterFormQuickPresets
          :show-filtration-inline-help="store.showFiltrationInlineHelp"
          :quick-presets="store.quickPresets"
          :category-presets="store.categoryPresets"
          :query-settings="store.querySettings"
          :case="store.case"
        />
      </div>
      <div class="card-header row border-bottom-1 pt-1 pr-1">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a
              class="nav-link active"
              :class="{ 'border-danger text-danger': genotypeHasError }"
              id="genotype-tab"
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
              class="nav-link"
              :class="{ 'texborder-danger -danger': frequencyHasError }"
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
          <li class="nav-item d-none d-md-block">
            <a
              class="nav-link"
              :class="{ 'border-danger text-danger': prioritizationHasError }"
              id="prioritization-tab"
              data-toggle="tab"
              href="#panel-prioritization"
              role="tab"
              title="Configure variant prioritization"
            >
              Prioritization
              <i-mdi-alert-circle-outline v-if="prioritizationHasError" />
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
              <a
                class="dropdown-item"
                :class="{ 'text-danger': qualityHasError }"
                id="quality-tab"
                data-toggle="tab"
                href="#panel-quality"
                role="tab"
                title="Quality, allelic balance, coverage"
              >
                Quality
                <i-mdi-alert-circle-outline v-if="qualityHasError" />
              </a>
              <a
                class="dropdown-item"
                id="clinvar-tab"
                data-toggle="tab"
                href="#panel-clinvar"
                role="tab"
                title="Filter based on ClinVar"
              >
                ClinVar
              </a>
              <a
                class="dropdown-item"
                :class="{ 'text-danger': geneHasError }"
                id="blocklist-tab"
                data-toggle="tab"
                href="#panel-blocklist"
                role="tab"
                title="Allow-list and block-list genes and genomic regions"
              >
                Gene Lists &amp; Regions
                <i-mdi-alert-circle-outline v-if="geneHasError" />
              </a>
              <a
                class="dropdown-item"
                id="flags-tab"
                data-toggle="tab"
                href="#panel-flags"
                role="tab"
                title="Filter for user flags and comments"
              >
                Flags &amp; Comments
              </a>
              <a
                ref="exportPaneRef"
                :class="{ 'text-danger': exportHasError }"
                class="dropdown-item"
                id="export-tab"
                data-toggle="tab"
                href="#panel-export"
                role="tab"
                title="Configure downloadable file creation"
                data-placement="left"
              >
                Configure Downloads
                <i-mdi-alert-circle-outline v-if="exportHasError" />
              </a>
            </div>
          </li>
        </ul>
      </div>

      <div class="card-body p-0">
        <div class="tab-content">
          <div
            ref="genotypePaneRef"
            class="tab-pane fade show active"
            id="panel-genotype"
            role="tabpanel"
            aria-labelledby="genotype-tab"
          >
            <FilterFormGenotypePane
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              :case="store.case"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            ref="frequencyPaneRef"
            class="tab-pane fade"
            id="panel-frequency"
            role="tabpanel"
            aria-labelledby="frequency-tab"
          >
            <FilterFormFrequencyPane
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              :case="store.case"
              :query-settings="store.querySettings"
            />
          </div>
          <div
            ref="prioritizationPaneRef"
            class="tab-pane fade"
            id="panel-prioritization"
            role="tabpanel"
            aria-labelledby="prioritization-tab"
          >
            <FilterFormPriotizationPane
              :csrf-token="store.csrfToken"
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :exomiser-enabled="store.exomiserEnabled"
              :cadd-enabled="store.caddEnabled"
              v-model:prio-enabled="store.querySettings.prio_enabled"
              v-model:prio-algorithm="store.querySettings.prio_algorithm"
              v-model:prio-hpo-terms="store.querySettings.prio_hpo_terms"
              v-model:patho-enabled="store.querySettings.patho_enabled"
              v-model:patho-score="store.querySettings.patho_score"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-effect"
            role="tabpanel"
            aria-labelledby="effect-tab"
          >
            <FilterFormEffectPane
              ref="effectPaneRef"
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-quality"
            role="tabpanel"
            aria-labelledby="quality-tab"
          >
            <FilterFormQualityPane
              ref="qualityPaneRef"
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              :case-obj="store.case"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-blocklist"
            role="tabpanel"
            aria-labelledby="blocklist-tab"
          >
            <FilterFormGenesRegionsPane
              ref="genePaneRef"
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-flags"
            role="tabpanel"
            aria-labelledby="flags-tab"
          >
            <FilterFormFlagsPane
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-clinvar"
            role="tabpanel"
            aria-labelledby="clinvar-tab"
          >
            <FilterFormClinvarPane
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              v-model:query-settings="store.querySettings"
            />
          </div>
          <div
            class="tab-pane fade"
            id="panel-export"
            role="tabpanel"
            arial-labelledby="export-tab"
          >
            <FilterFormDownloadPane
              :show-filtration-inline-help="store.showFiltrationInlineHelp"
              :filtration-complexity-mode="store.filtrationComplexityMode"
              :case="store.case"
              v-model:export-settings="exportSettings"
            />
          </div>
        </div>
        <FilterFormFooter
          :query-state="store.queryState"
          :any-has-error="anyHasError"
          v-model:database="store.querySettings.database"
          @submit-button-click="store.submitQuery()"
        />
      </div>
    </div>
    <div v-else class="alert alert-info">
      <i-fa-solid-circle-notch class="spin" />
      <strong class="pl-2">Loading filter form ...</strong>
    </div>
    <!--    {% include "variants/_distiller_resubmit_modal.html" %}-->
    <!--    {% include "variants/_cadd_resubmit_modal.html" %}-->
    <!--    {% include "variants/_spanr_resubmit_modal.html" %}-->
  </form>
</template>

<style>
footer.sodar-footer,
.sodar-sub-navbar-container {
  display: none;
}
</style>

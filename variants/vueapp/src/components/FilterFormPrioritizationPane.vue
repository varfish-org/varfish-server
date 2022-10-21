<script setup>
import HpoTermInput from './HpoTermInput.vue'

import { declareWrapper } from '../helpers.js'
import { useVuelidate } from '@vuelidate/core'

const props = defineProps({
  csrfToken: String,
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  exomiserEnabled: Boolean,
  caddEnabled: Boolean,
  prioEnabled: Boolean,
  prioAlgorithm: String,
  prioHpoTerms: Array,
  pathoEnabled: Boolean,
  pathoScore: String,
})

const emit = defineEmits([
  'update:prioEnabled',
  'update:prioAlgorithm',
  'update:prioHpoTerms',
  'update:pathoEnabled',
  'update:pathoScore',
])

const prioEnabledWrapper = declareWrapper(props, 'prioEnabled', emit)
const prioAlgorithmWrapper = declareWrapper(props, 'prioAlgorithm', emit)
const prioHpoTermsWrapper = declareWrapper(props, 'prioHpoTerms', emit)
const pathoEnabledWrapper = declareWrapper(props, 'pathoEnabled', emit)
const pathoScoreWrapper = declareWrapper(props, 'pathoScore', emit)

const prioEnabledWarning = () => {
  return !prioEnabledWrapper.value && prioHpoTermsWrapper.value.length > 0
}

const v$ = useVuelidate()

defineExpose({ v$ })
</script>

<template>
  <div class="row">
    <div class="col-6 pt-3 mb-2">
      <h5 class="card-title mb-0">Phenotype Prioritization</h5>
      <div
        v-if="prioEnabledWarning()"
        class="alert alert-warning mt-2 mb-0"
        role="alert"
      >
        <strong>
          <i-bi-exclamation-circle />
          HPO terms provided but prioritization not enabled!
        </strong>
      </div>
      <div
        v-if="props.showFiltrationInlineHelp"
        class="alert alert-secondary small mt-2 mb-0 p-2"
      >
        <i-mdi-information />
        Phenotype-based prioritization is based on matching the gene that a
        variant is located in with your patient based on the phenotypes of genes
        and patients. VarFish use
        <a href="http://exomiser.github.io/Exomiser/" target="_blank"
          >Exomiser</a
        >
        for this which already knows about genes. To describe the phenotypes for
        your patient,
        <strong
          >enter phenotypes (HPO) or diseases (OMIM) into the "Type HPO or
          OMIM..." box and click on the appearing suggestions to select
          them</strong
        >. The HPO and OMIM terms will then be added to the text box below.
        These values will then be used for the prioritization. You can also
        paste some terms, e.g., as "HP:0004440; OMIM:122850".
      </div>

      <div class="custom-control custom-checkbox mt-2">
        <input
          v-model="prioEnabledWrapper"
          class="custom-control-input"
          type="checkbox"
          id="prio-enabled"
        />
        <label class="custom-control-label" for="prio-enabled">
          Enable phenotype-based prioritization
        </label>
        <div class="form-text text-muted small">
          Note well that only variants in the first 1000 genes returned by your
          query will be prioritized!
        </div>
      </div>
      <div class="form-group pt-2">
        <label for="prio-algorithm"> Phenotype Similarity Algorithm </label>
        <select
          v-model="prioAlgorithmWrapper"
          class="custom-select"
          id="prio-algorithm"
        >
          <option value="phenix">Phenix</option>
          <option value="phive">Phive</option>
          <option value="hiphive-human">HiPhive (human only)</option>
          <option value="hiphive-mouse">HiPhive (human+mouse)</option>
          <option value="hiphive">HiPhive (human, mouse, fish, PPI)</option>
        </select>
      </div>
      <div class="form-group pt-2">
        <label for="prio-hpo-terms"> HPO Terms </label>
        <HpoTermInput v-model="prioHpoTerms" />
      </div>
    </div>

    <div class="col-6 pt-3">
      <h5 class="card-title mb-0">Pathogenicity Prioritization</h5>
      <div
        v-if="props.showFiltrationInlineHelp"
        class="alert alert-secondary small mt-2 mb-0 p-2"
      >
        <i-mdi-information />
        Enable the pathogenicity-based priotization and (optionally) adjust the
        scoring method below.
      </div>

      <div class="custom-control custom-checkbox mt-2">
        <input
          v-model="pathoEnabledWrapper"
          class="custom-control-input"
          type="checkbox"
          id="patho-enabled"
        />
        <label class="custom-control-label" for="patho-enabled">
          Enable variant pathogenicity-based prioritization
        </label>
        <div class="form-text text-muted small">
          First try to filter your variants without pathogenicity-based
          prioritization before enabling it. Note well that only the first 5000
          variants returned by your query will be prioritized!
        </div>
      </div>
      <div class="form-group">
        <label for="patho-score"> Pathogenicity Score </label>
        <select
          v-model="pathoScoreWrapper"
          class="custom-select"
          id="patho-score"
        >
          <option value="mutationtaster">MutationTaster</option>
          <option v-if="props.caddEnabled" value="cadd">CADD</option>
        </select>
      </div>
    </div>
  </div>
</template>

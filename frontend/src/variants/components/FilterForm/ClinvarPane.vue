<script setup>
import { computed } from 'vue'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

const interpretations = computed(() => {
  return [
    { id: 'pathogenic', label: 'P5 - pathogenic' },
    { id: 'likely_pathogenic', label: 'LP4 - likely pathogenic' },
    { id: 'uncertain_significance', label: 'VUS3 - uncertain significance' },
    { id: 'likely_benign', label: 'LB2 - likely benign' },
    { id: 'benign', label: 'B1 - benign' },
  ]
})
</script>

<template>
  <div
    v-if="querySettings !== null && querySettings !== undefined"
    class="row p-2"
  >
    <div class="col-lg-6 col-md-12">
      <div
        v-if="props.showFiltrationInlineHelp"
        class="alert alert-secondary small p-2 mt-3"
      >
        <i-mdi-information />
        You can require all variants in the results to be present in the local
        ClinVar copy. Please note that the local ClinVar copy is generally out
        of date with the main ClinVar database.
      </div>

      <div class="font-weight-bold mb-2 mt-2">Overall Settings</div>

      <div class="custom-control custom-checkbox">
        <input
          id="clinvar-require-in-clinvar"
          v-model="props.querySettings.require_in_clinvar"
          type="checkbox"
          class="custom-control-input"
        />
        <label class="custom-control-label" for="clinvar-require-in-clinvar">
          require ClinVar membership
        </label>
        <small class="form-text">
          When checking this box, only variants present in ClinVar
          <strong>and</strong>
          fulfilling the criteria from below will be present in the result.
        </small>
      </div>
      <div class="custom-control custom-checkbox">
        <input
          id="clinvar-exclude-conflicting"
          v-model="props.querySettings.clinvar_exclude_conflicting"
          type="checkbox"
          class="custom-control-input"
          :disabled="!props.querySettings.require_in_clinvar"
        />
        <label class="custom-control-label" for="clinvar-exclude-conflicting">
          exclude variants with conflicting interpretations
        </label>
        <small class="form-text">
          When checked, variants with conflicting ClinVar interpretations will
          be excluded from the results. Conflicting means having interpretations
          from different pathogenicity groups (e.g., pathogenic vs benign, or
          pathogenic vs uncertain).
        </small>
      </div>
    </div>
    <div class="col-lg-6 col-md-12">
      <div class="font-weight-bold mt-2">ClinVar Interpretations</div>
      <div class="text-form text-muted small mt-2 mb-2">
        Check the ClinVar (summary) interpretations that you want to limit your
        results to. These filters only apply if "require ClinVar membership" is
        selected above.
      </div>
      <div
        v-for="interpretation in interpretations"
        class="custom-control custom-checkbox"
      >
        <input
          :id="`clinvar-include-${interpretation.id}`"
          v-model="props.querySettings[`clinvar_include_${interpretation.id}`]"
          type="checkbox"
          class="custom-control-input"
          :disabled="!props.querySettings.require_in_clinvar"
        />
        <label
          class="custom-control-label"
          :for="`clinvar-include-${interpretation.id}`"
        >
          {{ interpretation.label }} variants
        </label>
      </div>
    </div>
  </div>

  <!--    <div class="col-12">-->
  <!--      <h5 class="card-title">-->
  <!--        ClinVar Status-->
  <!--        <small class="text-muted"> Only applied if membership required. </small>-->
  <!--      </h5>-->
  <!--    </div>-->

  <!--    <div class="col-12">-->
  <!--      <div class="row">-->
  <!--        <div class="col-6 pl-0 pt-0">-->
  <!--          <div class="form-group">-->
  <!--            <div id="div_id_clinvar_paranoid_mode" class="checkbox">-->
  <!--              <label for="id_clinvar_paranoid_mode" class="">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_paranoid_mode"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_paranoid_mode"-->
  <!--                />-->
  <!--                enable 'paranoid' mode-->

  <!--                <small-->
  <!--                  id="hint_id_clinvar_paranoid_mode"-->
  <!--                  class="form-text text-muted"-->
  <!--                  >When set, then variant assessments with and without assertion-->
  <!--                  are interpreted as equally important. By default, they are not-->
  <!--                  those with assessment override the others.</small-->
  <!--                >-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--      </div>-->
  <!--    </div>-->
  <!--    <div class="col-12">-->
  <!--      <div class="row">-->
  <!--        <div class="col-2 pl-0 pt-0">-->
  <!--          <div class="form-group">-->
  <!--            <div id="div_id_clinvar_include_benign" class="checkbox">-->
  <!--              <label for="id_clinvar_include_benign" class="">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_include_benign"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_include_benign"-->
  <!--                />-->
  <!--                benign-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--        <div class="col-2">-->
  <!--          <div class="form-group">-->
  <!--            <div id="div_id_clinvar_include_likely_benign" class="checkbox">-->
  <!--              <label for="id_clinvar_include_likely_benign" class="">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_include_likely_benign"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_include_likely_benign"-->
  <!--                />-->
  <!--                likely benign-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--        <div class="col-2">-->
  <!--          <div class="form-group">-->
  <!--            <div-->
  <!--              id="div_id_clinvar_include_uncertain_significance"-->
  <!--              class="checkbox"-->
  <!--            >-->
  <!--              <label for="id_clinvar_include_uncertain_significance" class="">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_include_uncertain_significance"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_include_uncertain_significance"-->
  <!--                />-->
  <!--                uncertain significance-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--        <div class="col-2">-->
  <!--          <div class="form-group">-->
  <!--            <div id="div_id_clinvar_include_likely_pathogenic" class="checkbox">-->
  <!--              <label for="id_clinvar_include_likely_pathogenic" class="active">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_include_likely_pathogenic"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_include_likely_pathogenic"-->
  <!--                  checked=""-->
  <!--                />-->
  <!--                likely pathogenic-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--        <div class="col-2">-->
  <!--          <div class="form-group">-->
  <!--            <div id="div_id_clinvar_include_pathogenic" class="checkbox">-->
  <!--              <label for="id_clinvar_include_pathogenic" class="active">-->
  <!--                <input-->
  <!--                  type="checkbox"-->
  <!--                  name="clinvar_include_pathogenic"-->
  <!--                  class="checkboxinput"-->
  <!--                  id="id_clinvar_include_pathogenic"-->
  <!--                  checked=""-->
  <!--                />-->
  <!--                pathogenic-->
  <!--              </label>-->
  <!--            </div>-->
  <!--          </div>-->
  <!--        </div>-->
  <!--      </div>-->
  <!--    </div>-->
  <!--  </div>-->
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>

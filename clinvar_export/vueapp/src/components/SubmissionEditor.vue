<script setup>
import Multiselect from '@vueform/multiselect'
import { useVuelidate } from '@vuelidate/core'
import { helpers, numeric, required } from '@vuelidate/validators'

import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import { getSubmissionLabel } from '@clinvarexport/helpers'
import {
  useClinvarExportStore,
  RECORD_STATUS_OPTIONS,
  RELEASE_STATUS_OPTIONS,
  SIGNIFICANCE_STATUS_OPTIONS,
  SIGNIFICANCE_DESCRIPTION_OPTIONS,
  VARIANT_ASSEMBLY_OPTIONS,
  MODE_OF_INHERITANCE_OPTIONS,
  AGE_OF_ONSET_OPTIONS,
  VARIANT_TYPE,
} from '@clinvarexport/stores/clinvar-export'

import SubmissionCaseList from './SubmissionCaseList.vue'
import { ref, computed, onMounted } from 'vue'

const components = { Multiselect, SubmissionCaseList }

// Define Pinia store and shorcut for currentSubmissionSet
const store = useClinvarExportStore()
const currentSubmissionSet = ref(store.currentSubmissionSet)
const currentSubmission = computed(() => store.currentSubmission)

// Local state used for loading OMIM diseases
const omimDiseasesLoading = ref(false)

const currentSubmissionLabel = computed(() => {
  if (currentSubmission.value) {
    return getSubmissionLabel(currentSubmission.value)
  } else {
    return getSubmissionLabel(null)
  }
})

/**
 * @return {array} List of objects for assertion method options with keys value and text.
 */
const assertionMethodOptions = computed(() => {
  return Object.values(store.assertionMethods).map((o) => ({
    value: o.sodar_uuid,
    text: o.title,
  }))
})

// Helper function to build wrappers that catch the case of currentSubmission not being set.
const _vuelidateWrappers = (keys) =>
  Object.fromEntries(
    keys.map((key) => [
      key,
      computed({
        get() {
          if (!currentSubmission.value) {
            return null
          } else {
            return currentSubmission.value[key]
          }
        },
        set(newValue) {
          if (currentSubmission.value) {
            currentSubmission.value[key] = newValue
          }
        },
      }),
    ]),
  )
// Define object with the data to edit in the form.  We construct custom wrappers so we can easily pass this into vuelidate.
const formState = {
  ..._vuelidateWrappers([
    'record_status',
    'release_status',
    'significance_last_evaluation',
    'significance_status',
    'significance_description',
    'assertion_method',
    'inheritance',
    'age_of_onset',
    'variant_assembly',
    'variant_chromosome',
    'variant_type',
    'variant_start',
    'variant_stop',
    'variant_reference',
    'variant_alternative',
  ]),
  diseases: computed({
    get() {
      if (!currentSubmission.value) {
        return []
      } else {
        return currentSubmission.value.diseases.map((obj) => {
          return {
            value: obj,
            label: `${obj.term_id} -- ${obj.term_name}`,
          }
        })
      }
    },
    set(value) {
      store.updateCurrentSubmission({
        key: 'diseases',
        value: value.map((v) => v.value),
      })
    },
  }),
  variant_gene: computed({
    get() {
      if (!currentSubmission.value) {
        return null
      } else {
        return currentSubmission.value.variant_gene.join(', ')
      }
    },
    set(value) {
      store.updateCurrentSubmission({
        key: 'variant_gene',
        value: value.split(',').map((s) => s.trim()),
      })
    },
  }),
  variant_hgvs: computed({
    get() {
      if (!currentSubmission.value) {
        return null
      } else {
        return currentSubmission.value.variant_hgvs.join(', ')
      }
    },
    set(value) {
      store.updateCurrentSubmission({
        key: 'variant_hgvs',
        value: value.split(',').map((s) => s.trim()),
      })
    },
  }),
}

// Define validation rules.
const rules = {
  record_status: {
    required,
    isValidChoice: (x) => RECORD_STATUS_OPTIONS.includes(x),
    $autoDirty: true,
  },
  release_status: {
    required,
    isValidChoice: (x) => RELEASE_STATUS_OPTIONS.includes(x),
    $autoDirty: true,
  },
  significance_last_evaluation: {
    required,
    isValidDate: (x) => {
      if (!x) {
        return true
      } else {
        return !!x.match(/^\d\d\d\d-\d\d-\d\d$/)
      }
    },
    $autoDirty: true,
  },
  significance_status: {
    required,
    isValidChoice: (x) => SIGNIFICANCE_STATUS_OPTIONS.includes(x),
    $autoDirty: true,
  },
  significance_description: {
    isValidChoice: (x) => !x || SIGNIFICANCE_DESCRIPTION_OPTIONS.includes(x),
    $autoDirty: true,
  },
  assertion_method: {
    required,
    isValidAssertionMethod: (x) =>
      !!store.assertionMethods && x in store.assertionMethods,
    $autoDirty: true,
  },
  inheritance: {
    isValidModeOfInheritance: (x) =>
      !helpers.req(x) || MODE_OF_INHERITANCE_OPTIONS.includes(x),
    $autoDirty: true,
  },
  age_of_onset: {
    isValidAgeOfOnset: (x) =>
      !helpers.req(x) || AGE_OF_ONSET_OPTIONS.includes(x),
    $autoDirty: true,
  },
  variant_assembly: {
    required,
    isValidChoice: (x) => VARIANT_ASSEMBLY_OPTIONS.includes(x),
    $autoDirty: true,
  },
  variant_chromosome: {
    required,
    $autoDirty: true,
  },
  variant_type: {
    required,
    isValidChoice: (x) => VARIANT_TYPE.includes(x),
    $autoDirty: true,
  },
  variant_start: {
    required,
    numeric,
    $autoDirty: true,
  },
  variant_stop: {
    required,
    numeric,
    $autoDirty: true,
  },
  variant_reference: {
    // required
    $autoDirty: true,
  },
  variant_alternative: {
    // required
    $autoDirty: true,
  },
  diseases: {
    $autoDirty: true,
  },
  variant_gene: {
    required,
    $autoDirty: true,
  },
  variant_hgvs: {
    required,
    $autoDirty: true,
  },
}

// Define vuelidate object
const v$ = useVuelidate(rules, formState)

onMounted(() => {
  v$.value.$touch()
})

/**
 * @param up whether to consider up movement (false is down)
 * @return {boolean} whether moving into the given direction is currently disabled
 */
const isMoveCurrentSubmissionDisabled = (up) => {
  const other = currentSubmission.value.sort_order + (up ? -1 : 1)
  return (
    other < 0 ||
    other >= Object.keys(currentSubmissionSet.value.submissions).length
  )
}

/**
 * Called by the Vue Multiselect to obtain OMIM disease terms via the AJAX API.
 */
const asyncFindOmimDiseases = async (query) => {
  omimDiseasesLoading.value = true
  const response = await clinvarExportApi.queryOmim(store.appContext, query)
  const result = response.result.map((obj) => {
    return {
      value: obj,
      label: `${obj.term_id} -- ${obj.term_name}`,
    }
  })
  omimDiseasesLoading.value = false
  return result
}

/**
 * @return {boolean} whether the form is currently valid or not
 */
const isValid = () => {
  return v$.value.$errors.length === 0
}

// Define the exposed functions
defineExpose({
  isValid,
})
</script>

<template>
  <div class="flex-grow-1 mt-1">
    <h4 class="border-bottom pb-2 mb-3">
      Variant: {{ currentSubmissionLabel }}
      <div class="btn-group float-right">
        <button
          ref="buttonMoveCurrentSubmissionUp"
          type="button"
          class="btn btn-sm btn-secondary"
          :disabled="isMoveCurrentSubmissionDisabled(true)"
          @click="store.moveCurrentSubmission(true)"
        >
          <i-mdi-arrow-up-circle />
          move up
        </button>
        <button
          ref="buttonMoveCurrentSubmissionDown"
          type="button"
          class="btn btn-sm btn-secondary"
          :disabled="isMoveCurrentSubmissionDisabled(false)"
          @click="store.moveCurrentSubmission(false)"
        >
          <i-mdi-arrow-down-circle />
          move down
        </button>
        <button
          type="button"
          class="btn btn-sm btn-danger"
          @click="store.deleteCurrentSubmission()"
        >
          <i-mdi-close />
          remove from submission
        </button>
      </div>
    </h4>

    <div class="row">
      <div class="col-6 pl-0">
        <div class="row">
          <div class="col-6 pl-0">
            <div id="input-group-record-status" class="form-group">
              <label for="input-record-status">Record Status</label>
              <select
                id="input-record-status"
                v-model="v$.record_status.$model"
                required
                :class="{
                  'custom-select is-valid': !v$.record_status.$error,
                  'custom-select is-invalid': v$.record_status.$error,
                }"
              >
                <option>Choose...</option>
                <option
                  v-for="recordStatusOption in RECORD_STATUS_OPTIONS"
                  :key="recordStatusOption"
                  :value="recordStatusOption"
                >
                  {{ recordStatusOption }}
                </option>
              </select>
              <div
                v-for="error of v$.record_status.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>
          </div>
          <div class="col-6 pr-0">
            <div id="input-group-release-status" class="form-group">
              <label for="input-release-status">Release Status</label>
              <select
                id="input-release-status"
                v-model="v$.release_status.$model"
                required
                :class="{
                  'custom-select is-valid': !v$.release_status.$error,
                  'custom-select is-invalid': v$.release_status.$error,
                }"
              >
                <option>Choose...</option>
                <option
                  v-for="releaseStatusOption in RELEASE_STATUS_OPTIONS"
                  :key="releaseStatusOption"
                  :value="releaseStatusOption"
                >
                  {{ releaseStatusOption }}
                </option>
              </select>
              <div
                v-for="error of v$.release_status.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>
          </div>
        </div>

        <div id="input-group-significance-last-evaluation" class="form-group">
          <label for="input-significance-last-evaluation"
            >Significance Last Evaluation</label
          >
          <input
            id="input-significance-last-evaluation"
            v-model="v$.significance_last_evaluation.$model"
            required
            :class="{
              'form-control is-valid': !v$.significance_last_evaluation.$error,
              'form-control is-invalid': v$.significance_last_evaluation.$error,
            }"
          />
          <div
            v-for="error of v$.significance_last_evaluation.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
          <small class="form-text text-muted"> Enter as YYYY-MM-DD </small>
        </div>

        <div id="input-group-significance-status" class="form-group">
          <label for="input-significance-status">Significance Status</label>
          <select
            id="input-significance-status"
            v-model="v$.significance_status.$model"
            required
            :class="{
              'custom-select is-valid': !v$.significance_status.$error,
              'custom-select is-invalid': v$.significance_status.$error,
            }"
          >
            <option>Choose...</option>
            <option
              v-for="significanceStatusOption in SIGNIFICANCE_STATUS_OPTIONS"
              :key="significanceStatusOption"
              :value="significanceStatusOption"
            >
              {{ significanceStatusOption }}
            </option>
          </select>
          <div
            v-for="error of v$.significance_status.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </div>

        <div id="input-group-significance-description" class="form-group">
          <label for="input-significance-description"
            >Significance Description</label
          >
          <select
            id="input-significance-description"
            v-model="v$.significance_description.$model"
            required
            :class="{
              'custom-select is-valid': !v$.significance_description.$error,
              'custom-select is-invalid': v$.significance_description.$error,
            }"
          >
            <option
              v-for="significanceDescriptionOption in SIGNIFICANCE_DESCRIPTION_OPTIONS"
              :key="significanceDescriptionOption"
              :value="significanceDescriptionOption"
            >
              {{ significanceDescriptionOption }}
            </option>
          </select>
          <div
            v-for="error of v$.significance_description.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </div>

        <div id="input-group-significance-inheritance" class="form-group">
          <label for="input-mode-of-inheritance">Mode of Inheritance</label>
          <select
            id="input-significance-inheritance"
            v-model="v$.inheritance.$model"
            required
            :class="{
              'custom-select is-valid': !v$.inheritance.$error,
              'custom-select is-invalid': v$.inheritance.$error,
            }"
          >
            <option
              v-for="modeOfInheritanceOption in MODE_OF_INHERITANCE_OPTIONS"
              :key="modeOfInheritanceOption"
              :value="modeOfInheritanceOption"
            >
              {{ modeOfInheritanceOption }}
            </option>
          </select>
          <div
            v-for="error of v$.inheritance.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </div>

        <div id="input-group-significance-age-of-onset" class="form-group">
          <label for="input-age-of-onset">Age of Onset</label>
          <select
            id="input-significance-age-of-onset"
            v-model="v$.age_of_onset.$model"
            required
            :class="{
              'custom-select is-valid': !v$.age_of_onset.$error,
              'custom-select is-invalid': v$.age_of_onset.$error,
            }"
          >
            <option
              v-for="ageOfOnsetOption in AGE_OF_ONSET_OPTIONS"
              :key="ageOfOnsetOption"
              :value="ageOfOnsetOption"
            >
              {{ ageOfOnsetOption }}
            </option>
          </select>
          <div
            v-for="error of v$.age_of_onset.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </div>
      </div>
      <div class="col-6 pr-0">
        <div class="row">
          <div
            id="input-group-variant-type"
            class="form-group col-12 pl-0 pr-0"
          >
            <label for="input-variant-type">Variant Type</label>
            <select
              id="input-variant-type"
              v-model="v$.variant_type.$model"
              required
              :class="{
                'custom-select is-valid': !v$.variant_type.$error,
                'custom-select is-invalid': v$.variant_type.$error,
              }"
            >
              <option
                v-for="variantTypeOption in VARIANT_TYPE"
                :key="variantTypeOption"
                :value="variantTypeOption"
              >
                {{ variantTypeOption }}
              </option>
            </select>
            <div
              v-for="error of v$.variant_type.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
          <div class="row">
            <div
              id="input-group-variant-assembly"
              class="form-group col-3 pl-0"
            >
              <label for="input-variant-assembly">Assembly</label>
              <input
                id="input-variant-assembly"
                v-model="v$.variant_assembly.$model"
                required
                :class="{
                  'form-control is-valid': !v$.variant_assembly.$error,
                  'form-control is-invalid': v$.variant_assembly.$error,
                }"
              />
              <div
                v-for="error of v$.variant_assembly.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>

            <div
              id="input-group-variant-chromosome"
              class="form-group col-3 pl-0"
            >
              <label for="input-variant-chromosome">Chromosome</label>
              <input
                id="input-variant-chromosome"
                v-model="v$.variant_chromosome.$model"
                required
                :class="{
                  'form-control is-valid': !v$.variant_chromosome.$error,
                  'form-control is-invalid': v$.variant_chromosome.$error,
                }"
              />
              <div
                v-for="error of v$.variant_chromosome.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>

            <div id="input-group-variant-start" class="form-group col-3 pl-0">
              <label for="input-variant-start">Start</label>
              <input
                id="input-variant-start"
                v-model="v$.variant_start.$model"
                required
                :class="{
                  'form-control is-valid': !v$.variant_start.$error,
                  'form-control is-invalid': v$.variant_start.$error,
                }"
              />
              <div
                v-for="error of v$.variant_start.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>

            <div
              id="input-group-variant-stop"
              class="form-group col-3 pl-0 pr-0"
            >
              <label for="input-variant-stop">Stop</label>
              <input
                id="input-variant-stop"
                v-model="v$.variant_stop.$model"
                required
                :class="{
                  'form-control is-valid': !v$.variant_stop.$error,
                  'form-control is-invalid': v$.variant_stop.$error,
                }"
              />
              <div
                v-for="error of v$.variant_stop.$errors"
                :key="error.$uid"
                class="invalid-feedback"
              >
                {{ error.$message }}
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-6 pl-0">
              <div id="input-group-variant-reference" class="form-group">
                <label for="input-variant-reference">Reference</label>
                <input
                  id="input-variant-reference"
                  v-model="v$.variant_reference.$model"
                  required
                  :class="{
                    'form-control is-valid': !v$.variant_reference.$error,
                    'form-control is-invalid': v$.variant_reference.$error,
                  }"
                />
                <div
                  v-for="error of v$.variant_reference.$errors"
                  :key="error.$uid"
                  class="invalid-feedback"
                >
                  {{ error.$message }}
                </div>
              </div>
            </div>
            <div class="col-6 pl-0 pr-0">
              <div id="input-group-variant-alternative" class="form-group">
                <label for="input-variant-alternative">Alternative</label>
                <input
                  id="input-variant-alternative"
                  v-model="v$.variant_alternative.$model"
                  required
                  :class="{
                    'form-control is-valid': !v$.variant_alternative.$error,
                    'form-control is-invalid': v$.variant_alternative.$error,
                  }"
                />
                <div
                  v-for="error of v$.variant_alternative.$errors"
                  :key="error.$uid"
                  class="invalid-feedback"
                >
                  {{ error.$message }}
                </div>
              </div>
            </div>
          </div>

          <div
            id="input-group-variant-gene"
            class="form-group col-12 pl-0 pr-0"
          >
            <label for="input-variant-gene">Gene(s)</label>
            <input
              id="input-variant-gene"
              v-model="v$.variant_gene.$model"
              required
              :class="{
                'form-control is-valid': !v$.variant_gene.$error,
                'form-control is-invalid': v$.variant_gene.$error,
              }"
            />
            <div
              v-for="error of v$.variant_gene.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>

          <div
            id="input-group-variant-hgvs"
            class="form-group col-12 pl-0 pr-0"
          >
            <label for="input-variant-hgvs">HGVS Description(s)</label>
            <input
              id="input-variant-hgvs"
              v-model="v$.variant_hgvs.$model"
              required
              :class="{
                'form-control is-valid': !v$.variant_hgvs.$error,
                'form-control is-invalid': v$.variant_hgvs.$error,
              }"
            />
            <div
              v-for="error of v$.variant_hgvs.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
            <small class="form-text text-muted">
              Comma-separated list of HGVS descriptions for each gene..
            </small>
          </div>
          <div
            id="input-group-significance-assertion-method"
            class="form-group col-12 pl-0 pr-0"
          >
            <label for="input-assertion-method">Assertion Method</label>
            <select
              id="input-significance-assertion-method"
              v-model="v$.assertion_method.$model"
              required
              :class="{
                'custom-select is-valid': !v$.assertion_method.$error,
                'custom-select is-invalid': v$.assertion_method.$error,
              }"
            >
              <option
                v-for="assertionMethodOption in assertionMethodOptions"
                :key="assertionMethodOption.value"
                :value="assertionMethodOption.value"
              >
                {{ assertionMethodOption.text }}
              </option>
            </select>
            <div
              v-for="error of v$.assertion_method.$errors"
              :key="error.$uid"
              class="invalid-feedback"
            >
              {{ error.$message }}
            </div>
          </div>
        </div>
      </div>

      <div id="input-group-diseases" class="form-group col-12 pl-0 pr-0">
        <label for="input-diseases">Disease(s)</label>
        <multiselect
          id="input-diseases"
          v-model="v$.diseases.$model"
          placeholder="Select OMIM disease(s) for this variant"
          mode="tags"
          :filter-results="false"
          :allow-empty="true"
          :close-on-select="true"
          :searchable="true"
          :object="true"
          :resolve-on-load="false"
          :loading="omimDiseasesLoading"
          :delay="1"
          :min-chars="2"
          style="white-space: nowrap"
          :class="{
            'is-valid': !v$.diseases.$error,
            'is-invalid': v$.diseases.$error,
          }"
          :options="asyncFindOmimDiseases"
        ></multiselect>
        <small class="form-text text-muted">
          Select zero, one, or more OMIM diseases for annotating the submission
          with.
        </small>
      </div>

      <div>
        <submission-case-list></submission-case-list>
      </div>

      <div class="border-top w-100">
        <h4 class="border-bottom pt-3 pb-1 mb-3">ClinVar Submission Reports</h4>

        <h5>Submitter Report</h5>

        <template v-if="store.currentSubmission.clinvar_submitter_report">
          <div
            v-for="(entry, key) in store.currentSubmission
              .clinvar_submitter_report"
            class="row"
          >
            <div class="col-3">
              {{ key }}
            </div>
            <div class="col-9">
              {{ entry }}
            </div>
          </div>
        </template>
        <div v-else class="text-muted font-italic">
          No ClinVar submitter report (yet).
        </div>

        <h5 class="mt-3">Error Report</h5>

        <template v-if="store.currentSubmission.clinvar_error_report">
          <div
            v-for="(entry, key) in store.currentSubmission.clinvar_error_report"
            class="row"
          >
            <div class="col-3">
              {{ key }}
            </div>
            <div class="col-9">
              {{ entry }}
            </div>
          </div>
        </template>
        <div v-else class="text-muted font-italic">
          No ClinVar submitter report (yet).
        </div>
      </div>
    </div>
  </div>
</template>

<template>
  <div class="flex-grow-1 mt-1">
    <h4 class="border-bottom pb-2 mb-3">
      Variant: {{ getSubmissionLabel(currentSubmission) }}
      <div class="btn-group float-right">
        <button
          ref="buttonMoveCurrentSubmissionUp"
          type="button"
          class="btn btn-sm btn-secondary"
          :disabled="isMoveCurrentSubmissionDisabled(true)"
          @click="moveCurrentSubmission(true)"
        >
          <i class="iconify" data-icon="mdi:arrow-up-circle"></i>
          move up
        </button>
        <button
          ref="buttonMoveCurrentSubmissionDown"
          type="button"
          class="btn btn-sm btn-secondary"
          :disabled="isMoveCurrentSubmissionDisabled(false)"
          @click="moveCurrentSubmission(false)"
        >
          <i class="iconify" data-icon="mdi:arrow-down-circle"></i>
          move down
        </button>
        <button
          type="button"
          class="btn btn-sm btn-danger"
          @click="deleteCurrentSubmission()"
        >
          <span
            class="iconify"
            data-icon="mdi:close"
            data-inline="false"
          ></span>
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
                v-model="record_status"
                required
                :class="{
                  'custom-select is-valid': !$v.record_status.$error,
                  'custom-select is-invalid': $v.record_status.$error,
                }"
              >
                <option>Choose...</option>
                <option
                  v-for="recordStatusOption in recordStatusOptions"
                  :key="recordStatusOption"
                  :value="recordStatusOption"
                >
                  {{ recordStatusOption }}
                </option>
              </select>
              <div v-if="!$v.record_status.required" class="invalid-feedback">
                Must be provided.
              </div>
              <div
                v-if="!$v.record_status.isValidChoice"
                class="invalid-feedback"
              >
                Must be valid record status.
              </div>
            </div>
          </div>
          <div class="col-6 pr-0">
            <div id="input-group-release-status" class="form-group">
              <label for="input-release-status">Release Status</label>
              <select
                id="input-release-status"
                v-model="release_status"
                required
                :class="{
                  'custom-select is-valid': !$v.release_status.$error,
                  'custom-select is-invalid': $v.release_status.$error,
                }"
              >
                <option>Choose...</option>
                <option
                  v-for="releaseStatusOption in releaseStatusOptions"
                  :key="releaseStatusOption"
                  :value="releaseStatusOption"
                >
                  {{ releaseStatusOption }}
                </option>
              </select>
              <div v-if="!$v.release_status.required" class="invalid-feedback">
                Must be provided.
              </div>
              <div
                v-if="!$v.release_status.isValidChoice"
                class="invalid-feedback"
              >
                Must be valid release status.
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
            v-model="significance_last_evaluation"
            required
            :class="{
              'form-control is-valid': !$v.significance_last_evaluation.$error,
              'form-control is-invalid': $v.significance_last_evaluation.$error,
            }"
          />
          <div
            v-if="!$v.significance_last_evaluation.required"
            class="invalid-feedback"
          >
            Must be provided.
          </div>
          <div
            v-if="!$v.significance_last_evaluation.isValidDate"
            class="invalid-feedback"
          >
            Must be valid date YYYY-MM-DD.
          </div>
        </div>

        <div id="input-group-significance-status" class="form-group">
          <label for="input-significance-status">Significance Status</label>
          <select
            id="input-significance-status"
            v-model="significance_status"
            required
            :class="{
              'custom-select is-valid': !$v.significance_status.$error,
              'custom-select is-invalid': $v.significance_status.$error,
            }"
          >
            <option>Choose...</option>
            <option
              v-for="significanceStatusOption in significanceStatusOptions"
              :key="significanceStatusOption"
              :value="significanceStatusOption"
            >
              {{ significanceStatusOption }}
            </option>
          </select>
          <div v-if="!$v.significance_status.required" class="invalid-feedback">
            Must be provided.
          </div>
          <div
            v-if="!$v.significance_status.isValidChoice"
            class="invalid-feedback"
          >
            Must be valid significance status.
          </div>
        </div>

        <div id="input-group-significance-description" class="form-group">
          <label for="input-significance-description"
            >Significance Description</label
          >
          <select
            id="input-significance-description"
            v-model="significance_description"
            required
            :class="{
              'custom-select is-valid': !$v.significance_description.$error,
              'custom-select is-invalid': $v.significance_description.$error,
            }"
          >
            <option
              v-for="significanceDescriptionOption in significanceDescriptionOptions"
              :key="significanceDescriptionOption"
              :value="significanceDescriptionOption"
            >
              {{ significanceDescriptionOption }}
            </option>
          </select>
          <div
            v-if="!$v.significance_description.required"
            class="invalid-feedback"
          >
            Must be provided.
          </div>
          <div
            v-if="!$v.significance_description.isValidChoice"
            class="invalid-feedback"
          >
            Must be valid significance description.
          </div>
        </div>

        <div id="input-group-significance-inheritance" class="form-group">
          <label for="input-mode-of-inheritance">Mode of Inheritance</label>
          <select
            id="input-significance-inheritance"
            v-model="inheritance"
            required
            :class="{
              'custom-select is-valid': !$v.inheritance.$error,
              'custom-select is-invalid': $v.inheritance.$error,
            }"
          >
            <option
              v-for="modeOfInheritanceOption in modeOfInheritanceOptions"
              :key="modeOfInheritanceOption"
              :value="modeOfInheritanceOption"
            >
              {{ modeOfInheritanceOption }}
            </option>
          </select>
          <div v-if="!$v.inheritance.required" class="invalid-feedback">
            Must be provided.
          </div>
          <div v-if="!$v.inheritance.isValidChoice" class="invalid-feedback">
            Must be valid mode of inheritance.
          </div>
        </div>

        <div id="input-group-significance-age-of-onset" class="form-group">
          <label for="input-age-of-onset">Age of Onset</label>
          <select
            id="input-significance-age-of-onset"
            v-model="age_of_onset"
            required
            :class="{
              'custom-select is-valid': !$v.age_of_onset.$error,
              'custom-select is-invalid': $v.age_of_onset.$error,
            }"
          >
            <option
              v-for="ageOfOnsetOption in ageOfOnsetOptions"
              :key="ageOfOnsetOption"
              :value="ageOfOnsetOption"
            >
              {{ ageOfOnsetOption }}
            </option>
          </select>
          <div v-if="!$v.age_of_onset.required" class="invalid-feedback">
            Must be provided.
          </div>
          <div v-if="!$v.age_of_onset.isValidChoice" class="invalid-feedback">
            Must be valid mode of age of onset.
          </div>
        </div>

        <div id="input-group-significance-assertion-method" class="form-group">
          <label for="input-assertion-method">Assertion Method</label>
          <select
            id="input-significance-assertion-method"
            v-model="assertion_method"
            required
            :class="{
              'custom-select is-valid': !$v.assertion_method.$error,
              'custom-select is-invalid': $v.assertion_method.$error,
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
          <div v-if="!$v.assertion_method.required" class="invalid-feedback">
            Must be provided.
          </div>
          <div
            v-if="!$v.assertion_method.isValidChoice"
            class="invalid-feedback"
          >
            Must be valid mode of age of onset.
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
              v-model="variant_type"
              required
              :class="{
                'custom-select is-valid': !$v.variant_type.$error,
                'custom-select is-invalid': $v.variant_type.$error,
              }"
            >
              <option
                v-for="variantTypeOption in variantTypeOptions"
                :key="variantTypeOption"
                :value="variantTypeOption"
              >
                {{ variantTypeOption }}
              </option>
            </select>
            <div v-if="!$v.assertion_method.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div
              v-if="!$v.assertion_method.isValidChoice"
              class="invalid-feedback"
            >
              Must be valid mode of age of onset.
            </div>
          </div>
        </div>
        <div class="row">
          <div id="input-group-variant-assembly" class="form-group col-3 pl-0">
            <label for="input-variant-assembly">Assembly</label>
            <input
              id="input-variant-assembly"
              v-model="variant_assembly"
              required
              :class="{
                'form-control is-valid': !$v.variant_assembly.$error,
                'from-control is-invalid': $v.variant_assembly.$error,
              }"
            />
            <div v-if="!$v.variant_assembly.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div
              v-if="!$v.variant_assembly.isValidChoice"
              class="invalid-feedback"
            >
              Must be valid assembly name.
            </div>
          </div>

          <div
            id="input-group-variant-chromosome"
            class="form-group col-3 pl-0"
          >
            <label for="input-variant-chromosome">Chromosome</label>
            <input
              id="input-variant-chromosome"
              v-model="variant_chromosome"
              required
              :class="{
                'form-control is-valid': !$v.variant_chromosome.$error,
                'from-control is-invalid': $v.variant_chromosome.$error,
              }"
            />
            <div
              v-if="!$v.variant_chromosome.required"
              class="invalid-feedback"
            >
              Must be provided.
            </div>
          </div>

          <div id="input-group-variant-start" class="form-group col-3 pl-0">
            <label for="input-variant-start">Start</label>
            <input
              id="input-variant-start"
              v-model="variant_start"
              required
              :class="{
                'form-control is-valid': !$v.variant_start.$error,
                'from-control is-invalid': $v.variant_start.$error,
              }"
            />
            <div v-if="!$v.variant_start.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div v-if="!$v.variant_start.numeric" class="invalid-feedback">
              Must be valid start position.
            </div>
          </div>

          <div id="input-group-variant-stop" class="form-group col-3 pl-0 pr-0">
            <label for="input-variant-stop">Stop</label>
            <input
              id="input-variant-stop"
              v-model="variant_stop"
              required
              :class="{
                'form-control is-valid': !$v.variant_stop.$error,
                'from-control is-invalid': $v.variant_stop.$error,
              }"
            />
            <div v-if="!$v.variant_stop.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div v-if="!$v.variant_stop.numeric" class="invalid-feedback">
              Must be valid stop position.
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-6 pl-0">
            <div id="input-group-variant-reference" class="form-group">
              <label for="input-variant-reference">Stop</label>
              <input
                id="input-variant-reference"
                v-model="variant_reference"
                required
                :class="{
                  'form-control is-valid': !$v.variant_reference.$error,
                  'from-control is-invalid': $v.variant_reference.$error,
                }"
              />
              <div
                v-if="!$v.variant_reference.required"
                class="invalid-feedback"
              >
                Must be provided.
              </div>
            </div>
          </div>
          <div class="col-6 pl-0 pr-0">
            <div id="input-group-variant-alternative" class="form-group">
              <label for="input-variant-alternative">Stop</label>
              <input
                id="input-variant-alternative"
                v-model="variant_alternative"
                required
                :class="{
                  'form-control is-valid': !$v.variant_alternative.$error,
                  'from-control is-invalid': $v.variant_alternative.$error,
                }"
              />
              <div
                v-if="!$v.variant_alternative.required"
                class="invalid-feedback"
              >
                Must be provided.
              </div>
            </div>
          </div>
        </div>

        <div id="input-group-variant-gene" class="form-group col-12 pl-0 pr-0">
          <label for="input-variant-gene">Gene(s)</label>
          <input
            id="input-variant-gene"
            v-model="variant_gene"
            required
            :class="{
              'form-control is-valid': !$v.variant_gene.$error,
              'from-control is-invalid': $v.variant_gene.$error,
            }"
          />
          <div v-if="!$v.variant_gene.required" class="invalid-feedback">
            Must be provided.
          </div>
          <small class="form-text text-muted">
            Comma-separated list of affected genes with their official symbols.
          </small>
        </div>

        <div id="input-group-variant-hgvs" class="form-group col-12 pl-0 pr-0">
          <label for="input-variant-hgvs">HGVS Description(s)</label>
          <input
            id="input-variant-hgvs"
            v-model="variant_hgvs"
            required
            :class="{
              'form-control is-valid': !$v.variant_hgvs.$error,
              'from-control is-invalid': $v.variant_hgvs.$error,
            }"
          />
          <div v-if="!$v.variant_hgvs.required" class="invalid-feedback">
            Must be provided.
          </div>
          <small class="form-text text-muted">
            Comma-separated list of HGVS descriptions for each gene..
          </small>
        </div>

        <div id="input-group-diseases" class="form-group col-12 pl-0 pr-0">
          <label for="input-diseases">Disease(s)</label>
          <multiselect
            id="input-dieases"
            v-model="diseases"
            placeholder="Select OMIM disease(s) for this variant"
            track-by="term_id"
            :options="omimDiseaseOptions"
            :custom-label="getOmimDiseaseLabel"
            :loading="omimDiseasesLoading"
            :internal-search="false"
            :hide-selected="true"
            :multiple="true"
            :allow-empty="true"
            :close-on-select="true"
            style="white-space: nowrap"
            :class="{
              'is-valid': !$v.diseases.$error,
              'is-invalid': $v.diseases.$error,
            }"
            @search-change="asyncFindOmimDiseases"
          ></multiselect>
          <small class="form-text text-muted">
            Select zero, one, or more OMIM diseases for annotating the
            submission with.
          </small>
        </div>
      </div>
    </div>

    <div>
      <submission-case-list></submission-case-list>
    </div>
  </div>
</template>

<script>
/* eslint camelcase: ["off"] */

import Multiselect from 'vue-multiselect'
import { validationMixin } from 'vuelidate'
import { helpers, numeric, required } from 'vuelidate/lib/validators'
import { mapActions, mapState } from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'
import { getSubmissionLabel } from '@/helpers'

import SubmissionCaseList from './SubmissionCaseList'

const RECORD_STATUS_OPTIONS = Object.freeze(['novel', 'update', 'delete'])
const RELEASE_STATUS_OPTIONS = Object.freeze(['public', 'hold until published'])
const SIGNIFICANCE_STATUS_OPTIONS = Object.freeze([
  'no assertion provided',
  'no assertion criteria provided',
  'criteria provided, single submitter',
  'criteria provided, multiple submitters, no conflicts',
  'criteria provided, conflicting interpretations',
  'reviewed by expert panel',
  'practice guideline',
])
const SIGNIFICANCE_DESCRIPTION_OPTIONS = Object.freeze([
  '',
  'Benign',
  'Likely benign',
  'Uncertain significance',
  'Likely pathogenic',
  'Pathogenic',
])
const VARIANT_ASSEMBLY_OPTIONS = Object.freeze(['GRCh37', 'GRCh38'])
const MODE_OF_INHERITANCE_OPTIONS = Object.freeze([
  '',
  'Other',
  'Autosomal dominant contiguous gene syndrome',
  'Autosomal dominant germline de novo mutation',
  'Autosomal dominant inheritance',
  'Autosomal dominant inheritance with maternal imprinting',
  'Autosomal dominant inheritance with paternal imprinting',
  'Autosomal dominant somatic cell mutation',
  'Autosomal recessive inheritance',
  'Contiguous gene syndrome',
  'Digenic inheritance',
  'Genetic anticipation',
  'Genetic anticipation with paternal anticipation bias',
  'Gonosomal inheritance',
  'Heterogeneous',
  'Male-limited autosomal dominant',
  'Mitochondrial inheritance',
  'Multifactorial inheritance',
  'Oligogenic inheritance',
  'Polygenic inheritance',
  'Semidominant mode of inheritance',
  'Sex-limited autosomal dominant',
  'Sex-limited autosomal recessive inheritance',
  'Somatic mosaicism',
  'Somatic mutation',
  'Sporadic',
  'Uniparental disomy',
  'Uniparental heterodisomy',
  'Uniparental isodisomy',
  'X-linked dominant inheritance',
  'X-linked inheritance',
  'X-linked recessive inheritance',
])
const AGE_OF_ONSET_OPTIONS = Object.freeze([
  '',
  'Antenatal',
  'Embryonal',
  'Fetal',
  'Pediatric',
  'Infantile',
  'Childhood',
  'Juvenile',
  'Adult',
  'Neonatal',
  'Young adult',
  'Middle age',
  'Late',
  'Congenital',
])
const VARIANT_TYPE = Object.freeze(['Variation', 'Deletion', 'Duplication'])

function isValidAssertionMethod(value) {
  return !!this.assertionMethods && value in this.assertionMethods
}

function generateVuexVuelidateWrappers(names) {
  return Object.fromEntries(
    names.map((name) => [
      name,
      {
        get() {
          return this.currentSubmission[name]
        },
        set(value) {
          this.updateCurrentSubmission({ key: name, value })
          this.$v[name].$touch()
        },
      },
    ])
  )
}

export default {
  components: { Multiselect, SubmissionCaseList },
  mixins: [validationMixin],
  data() {
    return {
      omimDiseaseOptions: [],
      omimDiseasesLoading: false,
      recordStatusOptions: RECORD_STATUS_OPTIONS,
      releaseStatusOptions: RELEASE_STATUS_OPTIONS,
      significanceStatusOptions: SIGNIFICANCE_STATUS_OPTIONS,
      significanceDescriptionOptions: SIGNIFICANCE_DESCRIPTION_OPTIONS,
      modeOfInheritanceOptions: MODE_OF_INHERITANCE_OPTIONS,
      ageOfOnsetOptions: AGE_OF_ONSET_OPTIONS,
      variantTypeOptions: VARIANT_TYPE,
    }
  },
  computed: {
    ...mapState({
      appContext: (state) => state.clinvarExport.appContext,
      submissions: (state) => state.clinvarExport.submissions,
      currentSubmissionSet: (state) => state.clinvarExport.currentSubmissionSet,
      currentSubmission: (state) => state.clinvarExport.currentSubmission,
      assertionMethods: (state) => state.clinvarExport.assertionMethods,
    }),

    assertionMethodOptions: function () {
      return Object.values(this.assertionMethods).map((o) => ({
        value: o.sodar_uuid,
        text: o.title,
      }))
    },

    ...generateVuexVuelidateWrappers([
      'record_status',
      'release_status',
      'significance_last_evaluation',
      'significance_status',
      'significance_description',
      'assertion_method',
      'variant_allele_count',
      'inheritance',
      'age_of_onset',

      'variant_type',
      'variant_assembly',
      'variant_chromosome',
      'variant_start',
      'variant_stop',
      'variant_reference',
      'variant_alternative',

      'diseases',
    ]),

    // computed properties for automated split at commas

    variant_gene: {
      get() {
        return this.currentSubmission.variant_gene.join(', ')
      },
      set(value) {
        this.updateCurrentSubmission({
          key: 'variant_gene',
          value: value.split(',').map((s) => s.trim()),
        })
      },
    },
    variant_hgvs: {
      get() {
        return this.currentSubmission.variant_hgvs.join(', ')
      },
      set(value) {
        this.updateCurrentSubmission({
          key: 'variant_hgvs',
          value: value.split(',').map((s) => s.trim()),
        })
      },
    },
  },
  mounted() {
    this.$v.$touch()
    this.currentSubmission._isInvalid = this.$v.$invalid
  },
  validations: {
    record_status: {
      required,
      isValidChoice: (x) => RECORD_STATUS_OPTIONS.includes(x),
    },
    release_status: {
      required,
      isValidChoice: (x) => RELEASE_STATUS_OPTIONS.includes(x),
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
    },
    significance_status: {
      required,
      isValidChoice: (x) => SIGNIFICANCE_STATUS_OPTIONS.includes(x),
    },
    significance_description: {
      isValidChoice: (x) => !x || SIGNIFICANCE_DESCRIPTION_OPTIONS.includes(x),
    },
    assertion_method: {
      required,
      isValidAssertionMethod,
    },
    inheritance: {
      isValidModeOfInheritance: (x) =>
        !helpers.req(x) || MODE_OF_INHERITANCE_OPTIONS.includes(x),
    },
    age_of_onset: {
      isValidAgeOfOnset: (x) =>
        !helpers.req(x) || AGE_OF_ONSET_OPTIONS.includes(x),
    },
    variant_assembly: {
      required,
      isValidChoice: (x) => VARIANT_ASSEMBLY_OPTIONS.includes(x),
    },
    variant_chromosome: {
      required,
    },
    variant_type: {
      required,
      isValidChoice: (x) => VARIANT_TYPE.includes(x),
    },
    variant_start: {
      required,
      numeric,
    },
    variant_stop: {
      required,
      numeric,
    },
    variant_reference: {
      // required
    },
    variant_alternative: {
      // required
    },
    diseases: {},
    variant_gene: {
      required,
    },
    variant_hgvs: {
      required,
    },
  },
  methods: {
    ...mapActions('clinvarExport', [
      'updateCurrentSubmission',
      'moveCurrentSubmission',
      'deleteCurrentSubmission',
    ]),

    getSubmissionLabel,
    getOmimDiseaseLabel(o) {
      return `${o.term_id} - ${o.term_name}`
    },

    /**
     * @param up whether to consider up movement (false is down)
     * @return {boolean} whether moving into the given direction is currently disabled
     */
    isMoveCurrentSubmissionDisabled(up) {
      const other = this.currentSubmission.sort_order + (up ? -1 : 1)
      return (
        other < 0 ||
        other >= Object.keys(this.currentSubmissionSet.submissions).length
      )
    },

    /**
     * Called by the Vue Multiselect to obtain OMIM disease terms via the AJAX API.
     */
    asyncFindOmimDiseases(query) {
      this.omimDiseasesLoading = true
      clinvarExportApi.queryOmim(this.appContext, query).then(
        (response) => {
          this.omimDiseaseOptions = response.result
          this.omimDiseasesLoading = false
        },
        (reject) => {
          throw new Error(`Could not query for OMIM terms: ${reject}`)
        }
      )
    },
    /**
     * Validate form input state for the given property.
     */
    validateState(name) {
      this.updateCurrentSubmission({
        key: '_isInvalid',
        value: !this.isValid(),
      })
      const { $dirty, $error } = this.$v[name]
      return $dirty ? !$error : null
    },
    /**
     * @return {boolean} whether the form is currently invalid or not
     */
    isValid() {
      return !this.$v.$invalid
    },
  },
}
</script>

<style>
.is-invalid .multiselect__tags {
  border-color: #dc3545;
}
.is-valid .multiselect__tags {
  border-color: #28a745;
}
</style>

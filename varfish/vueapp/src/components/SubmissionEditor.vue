e<template>
  <div class="flex-grow-1 mt-1">
    <h4 class="border-bottom pb-2 mb-3">
      Variant: {{ getSubmissionLabel(currentSubmission) }}
      <b-button-group class="float-right">
        <b-button
            size="sm"
            variant="secondary"
            @click="moveCurrentSubmission(true)"
            :disabled="isMoveCurrentSubmissionDisabled(true)"
        >
          <i class="fa fa-arrow-up"></i>
          move up
        </b-button>
        <b-button
            size="sm"
            variant="secondary"
            @click="moveCurrentSubmission(false)"
            :disabled="isMoveCurrentSubmissionDisabled(false)"
        >
          <i class="fa fa-arrow-down"></i>
          move down
        </b-button>
        <b-button
            size="sm"
            variant="danger"
            @click="deleteCurrentSubmission()"
        >
          <span class="iconify" data-icon="mdi:close" data-inline="false"></span>
          remove from submission
        </b-button>
      </b-button-group>
    </h4>

    <div class="row">
      <div class="col-6 pl-0">
        <div class="row">
          <div class="col-6 pl-0">
            <b-form-group
              id="input-group-record-status"
              label-for="input-title"
              label="Record Status"
              description="Action to perform on ClinVar database"
            >
              <b-select
                id="input-record-status"
                required
                v-model="record_status"
                :options="recordStatusOptions"
                :state="validateState('record_status')"
                aria-describedby="input-group-record-status-feedback"
              ></b-select>
              <b-form-invalid-feedback
                id="input-group-record-status-feedback"
              >Must select a valid record status.</b-form-invalid-feedback>
            </b-form-group>
          </div>
          <div class="col-6 pr-0">
            <b-form-group
                id="input-group-release-status"
                label-for="input-release-status"
                label="Release Status"
            >
              <b-select
                id="input-release-status"
                required
                v-model="release_status"
                :options="releaseStatusOptions"
                :state="validateState('release_status')"
                aria-describedby="input-group-release-status-feedback"
              ></b-select>
              <b-form-invalid-feedback
                id="input-group-release-status-feedback"
              >Must select a valid release status.</b-form-invalid-feedback>
            </b-form-group>
          </div>
        </div>

        <b-form-group
            id="input-group-significance-last-evaluation"
            label-for="input-significance-last-evaluation"
            label="Significance Last Evaluation"
        >
          <b-form-datepicker
            id="input-significance-last-evaluation"
            required
            v-model="significance_last_evaluation"
            :state="validateState('significance_last_evaluation')"
            aria-describedby="input-group-significance-last-evaluation-feedback"
          ></b-form-datepicker>
          <b-form-invalid-feedback
            id="input-group-release-last-evaluation-feedback"
          >Must select a valid last evaluation date.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-significance-status"
            label-for="input-significance-status"
            label="Significance Status"
        >
          <b-select
            id="input-significance-status"
            required
            v-model="significance_status"
            :options="significanceStatusOptions"
            :state="validateState('significance_status')"
            aria-describedby="input-group-significance-status-feedback"
          ></b-select>
          <b-form-invalid-feedback
            id="input-group-release-status-feedback"
          >Must select a valid significance status.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-significance-description"
            label-for="input-significance-description"
            label="Significance Description"
        >
          <b-select
            id="input-significance-description"
            required
            v-model="significance_description"
            :options="significanceDescriptionOptions"
            :state="validateState('significance_description')"
            aria-describedby="input-group-significance-description-feedback"
          ></b-select>
          <b-form-invalid-feedback
            id="input-group-significance-description-feedback"
          >Must select a valid significance description.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-inheritance"
            label-for="input-inheritance"
            label="Mode of Inheritance"
        >
          <b-select
            id="input-inheritance"
            required
            v-model="inheritance"
            :options="modeOfInheritanceOptions"
            :state="validateState('inheritance')"
            aria-describedby="input-group-inheritance-feedback"
          ></b-select>
          <b-form-invalid-feedback
            id="input-group-inheritance-feedback"
          >Must select a valid mode of inheritance.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-age-of-onset"
            label-for="input-age-of-onset"
            label="Age of Onset"
        >
          <b-select
            id="input-age-of-onset"
            required
            v-model="age_of_onset"
            :options="ageOfOnsetOptions"
            :state="validateState('age_of_onset')"
            aria-describedby="input-group-age-of-onset-feedback"
          ></b-select>
          <b-form-invalid-feedback
            id="input-group-age-of-onset-feedback"
          >Must select a valid age of onset.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-assertion-method"
            label-for="input-assertion-method"
            label="Assertion Method"
        >
          <b-select
            id="input-assertion-method"
            required
            v-model="assertion_method"
            :options="assertionMethodOptions"
            :state="validateState('assertion_method')"
            aria-describedby="input-group-assertion-method-feedback"
          ></b-select>
          <b-form-invalid-feedback
            id="input-group-assertion-method-feedback"
          >Must select a valid assertion method.</b-form-invalid-feedback>
        </b-form-group>
      </div>
      <div class="col-6 pr-0">
        <div class="row">
          <b-form-group
              class="col-12 pl-0"
              id="input-group-variant-type"
              label-for="input-variant-type"
              label="Variant Type"
          >
            <b-select
              id="input-variant-type"
              required
              v-model="variant_type"
              :options="variantTypeOptions"
              :state="validateState('variant_type')"
              aria-describedby="input-group-variant-type-feedback"
            ></b-select>
            <b-form-invalid-feedback
              id="input-group-variant-type-feedback"
            >Specify a valid type.</b-form-invalid-feedback>
          </b-form-group>
        </div>
        <div class="row">
          <b-form-group
              class="col-3 pl-0"
              id="input-group-variant-assembly"
              label-for="input-variant-assembly"
              label="Assembly"
          >
            <b-input
              id="input-variant-assembly"
              required
              v-model="variant_assembly"
              :state="validateState('variant_assembly')"
              aria-describedby="input-group-variant-assembly-feedback"
            ></b-input>
            <b-form-invalid-feedback
              id="input-group-variant-assembly-feedback"
            >Specify a valid assembly.</b-form-invalid-feedback>
          </b-form-group>

          <b-form-group
              class="col-3"
              id="input-group-variant-chromosome"
              label-for="input-variant-chromosome"
              label="Chromosome"
          >
            <b-input
              id="input-variant-chromosome"
              required
              v-model="variant_chromosome"
              :state="validateState('variant_chromosome')"
              aria-describedby="input-group-variant-chromosome-feedback"
            ></b-input>
            <b-form-invalid-feedback
              id="input-group-variant-chromosome-feedback"
            >Specify a valid chromosome.</b-form-invalid-feedback>
          </b-form-group>

          <b-form-group
              class="col-3"
              id="input-group-variant-start"
              label-for="input-variant-start"
              label="Start"
          >
            <b-input
              id="input-variant-start"
              required
              v-model="variant_start"
              :state="validateState('variant_start')"
              aria-describedby="input-group-variant-start-feedback"
            ></b-input>
            <b-form-invalid-feedback
              id="input-group-variant-start-feedback"
            >Specify a valid start position.</b-form-invalid-feedback>
          </b-form-group>

          <b-form-group
              class="col-3 pr-0"
              id="input-group-variant-stop"
              label-for="input-variant-stop"
              label="Stop"
          >
            <b-input
              id="input-variant-stop"
              required
              v-model="variant_stop"
              :state="validateState('variant_stop')"
              aria-describedby="input-group-variant-stop-feedback"
            ></b-input>
            <b-form-invalid-feedback
              id="input-group-variant-stop-feedback"
            >Specify a valid stop position.</b-form-invalid-feedback>
          </b-form-group>
        </div>

        <div class="row">
          <div class="col-6 pl-0">
            <b-form-group
                id="input-group-variant-reference"
                label-for="input-variant-reference"
                label="Reference Allele"
            >
              <b-input
                id="input-variant-reference"
                required
                v-model="variant_reference"
                :state="validateState('variant_reference')"
                aria-describedby="input-group-variant-reference-feedback"
              ></b-input>
              <b-form-invalid-feedback
                id="input-group-variant-stop-feedback"
              >Specify reference allele.</b-form-invalid-feedback>
            </b-form-group>
          </div>
          <div class="col-6 pr-0">
            <b-form-group
                id="input-group-variant-alternative"
                label-for="input-variant-alternative"
                label="Alternative Allele"
            >
              <b-input
                id="input-variant-alternative"
                required
                v-model="variant_alternative"
                :state="validateState('variant_alternative')"
                aria-describedby="input-group-variant-alternative-feedback"
              ></b-input>
              <b-form-invalid-feedback
                id="input-group-variant-alternative-feedback"
              >Specify alternative allele.</b-form-invalid-feedback>
            </b-form-group>
          </div>
        </div>

        <b-form-group
            id="input-group-variant-gene"
            label-for="input-variant-gene"
            label="Gene(s)"
            description="Comma-separated list of affected genes with their official symbols"
        >
          <b-input
            id="input-variant-gene"
            required
            v-model="variant_gene"
            :state="validateState('variant_gene')"
            aria-describedby="input-group-variant-gene-feedback"
          ></b-input>
          <b-form-invalid-feedback
            id="input-group-variant-gene-feedback"
          >Specify at least one gene.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-variant-hgvs"
            label-for="input-variant-hgvs"
            label="HGVS Description(s)"
            description="Comma-separated list of HGVS changes, must match list of genes above"
        >
          <b-input
            id="input-variant-hgvs"
            required
            v-model="variant_hgvs"
            :state="validateState('variant_hgvs')"
            aria-describedby="input-group-variant-hgvs-feedback"
          ></b-input>
          <b-form-invalid-feedback
            id="input-group-variant-hgvs-feedback"
          >Specify at least one HGVS change.</b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
            id="input-group-diseases"
            label-for="input-diseases"
            label="Disease(s)"
            description="List of OMIM disease terms"
        >
          <multiselect
            id="input-variant-dieases"
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
            @search-change="asyncFindOmimDiseases"
            style="white-space: nowrap"
          ></multiselect>
        </b-form-group>
      </div>
    </div>

    <div>
      <submission-case-list></submission-case-list>
    </div>
  </div>
</template>

<script>
/* eslint camelcase: ["off"] */

import { validationMixin } from 'vuelidate'
import { mapActions, mapState } from 'vuex'
import Multiselect from 'vue-multiselect'
import SubmissionCaseList from './SubmissionCaseList'
import { helpers, numeric, required } from 'vuelidate/lib/validators'
import { getSubmissionLabel } from '@/helpers'
import clinvarExportApi from '@/api/clinvarExport'

const RECORD_STATUS_OPTIONS = Object.freeze(['novel', 'update', 'delete'])
const RELEASE_STATUS_OPTIONS = Object.freeze(['public', 'hold until published'])
const SIGNIFICANCE_STATUS_OPTIONS = Object.freeze([
  'no assertion provided',
  'no assertion criteria provided',
  'criteria provided, single submitter',
  'criteria provided, multiple submitters, no conflicts',
  'criteria provided, conflicting interpretations',
  'reviewed by expert panel',
  'practice guideline'
])
const SIGNIFICANCE_DESCRIPTION_OPTIONS = Object.freeze([
  'Benign',
  'Likely benign',
  'Uncertain significance',
  'Likely pathogenic',
  'Pathogenic'
])
const VARIANT_ASSEMBLY_OPTIONS = Object.freeze([
  'GRCh37',
  'GRCh38'
])
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
  'X-linked recessive inheritance'
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
  'Congenital'
])
const VARIANT_TYPE = Object.freeze([
  'Variation',
  'Deletion',
  'Duplication'
])

function isValidAssertionMethod (value) {
  return (!!this.assertionMethods) && (value in this.assertionMethods)
}

function generateVuexVuelidateWrappers (names) {
  return Object.fromEntries(
    names.map(name => [name, {
      get () {
        return this.currentSubmission[name]
      },
      set (value) {
        this.updateCurrentSubmission({ key: name, value })
        this.$v[name].$touch()
      }
    }])
  )
}

export default {
  mixins: [validationMixin],
  components: { Multiselect, SubmissionCaseList },
  mounted () {
    this.$v.$touch()
    this.currentSubmission._isInvalid = this.$v.$invalid
  },
  data () {
    return {
      omimDiseaseOptions: [],
      omimDiseasesLoading: false,
      recordStatusOptions: RECORD_STATUS_OPTIONS,
      releaseStatusOptions: RELEASE_STATUS_OPTIONS,
      significanceStatusOptions: SIGNIFICANCE_STATUS_OPTIONS,
      significanceDescriptionOptions: SIGNIFICANCE_DESCRIPTION_OPTIONS,
      modeOfInheritanceOptions: MODE_OF_INHERITANCE_OPTIONS,
      ageOfOnsetOptions: AGE_OF_ONSET_OPTIONS,
      variantTypeOptions: VARIANT_TYPE
    }
  },
  validations: {
    record_status: {
      required,
      isValidChoice: (x) => RECORD_STATUS_OPTIONS.includes(x)
    },
    release_status: {
      required,
      isValidChoice: (x) => RELEASE_STATUS_OPTIONS.includes(x)
    },
    significance_last_evaluation: {
      required
    },
    significance_status: {
      required,
      isValidChoice: (x) => SIGNIFICANCE_STATUS_OPTIONS.includes(x)
    },
    significance_description: {
      required,
      isValidChoice: (x) => SIGNIFICANCE_DESCRIPTION_OPTIONS.includes(x)
    },
    assertion_method: {
      required,
      isValidAssertionMethod
    },
    inheritance: {
      isValidModeOfInheritance: (x) => (!helpers.req(x) || MODE_OF_INHERITANCE_OPTIONS.includes(x))
    },
    age_of_onset: {
      isValidAgeOfOnset: (x) => (!helpers.req(x) || AGE_OF_ONSET_OPTIONS.includes(x))
    },
    variant_assembly: {
      required,
      isValidChoice: (x) => VARIANT_ASSEMBLY_OPTIONS.includes(x)
    },
    variant_chromosome: {
      required
    },
    variant_type: {
      required,
      isValidChoice: (x) => VARIANT_TYPE.includes(x)
    },
    variant_start: {
      required,
      numeric
    },
    variant_stop: {
      required,
      numeric
    },
    variant_reference: {
      // required
    },
    variant_alternative: {
      // required
    },
    diseases: {
    },
    variant_gene: {
      required
    },
    variant_hgvs: {
      required
    }
  },
  computed: {
    ...mapState({
      appContext: state => state.clinvarExport.appContext,
      submissions: state => state.clinvarExport.submissions,
      currentSubmissionSet: state => state.clinvarExport.currentSubmissionSet,
      currentSubmission: state => state.clinvarExport.currentSubmission,
      assertionMethods: state => state.clinvarExport.assertionMethods
    }),

    assertionMethodOptions: function () {
      return Object.values(this.assertionMethods).map(o => ({ value: o.sodar_uuid, text: o.title }))
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

      'diseases'
    ]),

    // computed properties for automated split at commas

    variant_gene: {
      get () {
        return this.currentSubmission.variant_gene.join(', ')
      },
      set (value) {
        this.updateCurrentSubmission({
          key: 'variant_gene',
          value: value.split(',').map(s => s.trim())
        })
      }
    },
    variant_hgvs: {
      get () {
        return this.currentSubmission.variant_hgvs.join(', ')
      },
      set (value) {
        this.updateCurrentSubmission({
          key: 'variant_hgvs',
          value: value.split(',').map(s => s.trim())
        })
      }
    }
  },
  methods: {
    ...mapActions('clinvarExport', [
      'updateCurrentSubmission',
      'moveCurrentSubmission',
      'deleteCurrentSubmission'
    ]),

    getSubmissionLabel,
    getOmimDiseaseLabel (o) {
      return `${o.term_id} - ${o.term_name}`
    },

    /**
     * @param up whether to consider up movement (false is down)
     * @return {boolean} whether moving into the given direction is currently disabled
     */
    isMoveCurrentSubmissionDisabled (up) {
      const other = this.currentSubmission.sort_order + (up ? -1 : 1)
      return (other < 0 || other >= Object.keys(this.currentSubmissionSet.submissions).length)
    },

    /**
     * Called by the Vue Multiselect to obtain OMIM disease terms via the AJAX API.
     */
    asyncFindOmimDiseases (query) {
      this.omimDiseasesLoading = true
      clinvarExportApi
        .queryOmim(this.appContext, query)
        .then(
          response => {
            this.omimDiseaseOptions = response.result
            this.omimDiseasesLoading = false
          },
          reject => {
            throw new Error(`Could not query for OMIM terms: ${reject}`)
          }
        )
    },
    /**
     * Validate form input state for the given property.
     */
    validateState (name) {
      this.updateCurrentSubmission({ key: '_isInvalid', value: !this.isValid() })
      const { $dirty, $error } = this.$v[name]
      return $dirty ? !$error : null
    },
    /**
     * @return {boolean} whether the form is currently invalid or not
     */
    isValid () {
      return !this.$v.$invalid
    }
  }
}
</script>

<style scoped>
</style>

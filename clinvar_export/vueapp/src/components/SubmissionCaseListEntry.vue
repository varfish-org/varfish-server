<template>
  <b-card header-tag="header">
    <template #header>
      <h4 class="mb-0 ml-0">
        Case &raquo;{{ individual ? individual.name : 'null' }}&laquo;
        <b-button-group class="float-right pb-0 mb-0">
          <b-button
            size="sm"
            variant="secondary"
            :disabled="isMoveDisabled(true)"
            @click="
              moveSubmissionIndividual({
                submissionIndividual: value,
                up: true,
              })
            "
          >
            <i class="iconify" data-icon="mdi:arrow-up-circle"></i>
            move up
          </b-button>
          <b-button
            size="sm"
            variant="secondary"
            :disabled="isMoveDisabled(false)"
            @click="
              moveSubmissionIndividual({
                submissionIndividual: value,
                up: false,
              })
            "
          >
            <i class="iconify" data-icon="mdi:arrow-down-circle"></i>
            move down
          </b-button>
          <b-button
            size="sm"
            variant="danger"
            @click="removeSubmissionIndividualFromCurrentSubmission(value)"
          >
            <span
              class="iconify"
              data-icon="mdi:close"
              data-inline="false"
            ></span>
            remove from variant
          </b-button>
        </b-button-group>
      </h4>
    </template>
    <b-card-text class="px-2">
      <div class="row">
        <div class="col-12 px-0">
          <b-form-group
            id="input-group-phenotypes"
            label-for="input-phenotypes"
            label="Phenotype HPO Terms"
          >
            <multiselect
              id="input-phenotypes"
              v-model="phenotypes"
              placeholder="Add phenotypes for this individual"
              track-by="term_id"
              :options="hpoTermsOptions"
              :custom-label="getHpoTermLabel"
              :loading="hpoTermsLoading"
              :internal-search="false"
              :hide-selected="true"
              :multiple="true"
              :allow-empty="true"
              :close-on-select="true"
              style="white-space: nowrap"
              @search-change="asyncFindHpoTerms"
            ></multiselect>
          </b-form-group>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <b-form-group
            id="input-group-source"
            label-for="input-source"
            label="Sample Source"
          >
            <b-select
              id="input-source"
              v-model="source"
              required
              :options="sampleSourceOptions"
              :state="validateState('source')"
              aria-describedby="input-group-source-feedback"
            ></b-select>
            <b-form-invalid-feedback id="input-group-source-feedback"
              >Must select a valid sample source.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
        <div class="col-4">
          <b-form-group
            id="input-group-tissue"
            label-for="input-tissue"
            label="Tissue"
          >
            <b-input
              id="input-tissue"
              v-model="tissue"
              required
              :state="validateState('tissue')"
              aria-describedby="input-group-tissue-feedback"
            ></b-input>
            <b-form-invalid-feedback id="input-group-tissue-feedback"
              >Specify the sampled tissue.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
        <div class="col-4 pr-0">
          <b-form-group
            id="input-group-citations"
            label-for="input-citations"
            label="PubMed Citations"
          >
            <b-input
              id="input-citations"
              v-model.trim="citations"
              required
              :state="validateState('citations')"
              aria-describedby="input-group-citations-feedback"
            ></b-input>
            <b-form-invalid-feedback id="input-group-citations-feedback"
              >Specify the citations as &raquo;PMID:123
              PMID:456&laquo;.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <b-form-group
            id="input-group-variant-origin"
            label-for="input-variant-origin"
            label="Variant Origin"
          >
            <b-select
              id="input-variant-origin"
              v-model="variant_origin"
              required
              :options="variantOriginOptions"
              :state="validateState('variant_origin')"
              aria-describedby="input-group-variant-origin-feedback"
            ></b-select>
            <b-form-invalid-feedback id="input-group-variant-origin-feedback"
              >Must select a valid variant origin.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
        <div class="col-4">
          <b-form-group
            id="input-group-variant-allele-count"
            label-for="input-variant-allele-count"
            label="Variant Allele Count"
          >
            <b-input
              id="input-variant-allele-count"
              v-model="variant_allele_count"
              required
              :state="validateState('variant_allele_count')"
              aria-describedby="input-group-variant-allele-count-feedback"
            ></b-input>
            <b-form-invalid-feedback
              id="input-group-variant-allele-count-feedback"
              >Specify either allele count as a number or
              zygosity.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
        <div class="col-4 pr-0">
          <b-form-group
            id="input-group-variant-zygosity"
            label-for="input-variant-zygosity"
            label="Zygosity"
          >
            <b-select
              id="input-variant-zygosity"
              v-model="variant_zygosity"
              required
              :options="variantZygosityOptions"
              :state="validateState('variant_zygosity')"
              aria-describedby="input-group-variant-zygosity-feedback"
            ></b-select>
            <b-form-invalid-feedback id="input-group-variant-zygosity-feedback"
              >Specify either allele count or zygosity.</b-form-invalid-feedback
            >
          </b-form-group>
        </div>
      </div>
    </b-card-text>
  </b-card>
</template>

<script>
import Multiselect from 'vue-multiselect'
import { validationMixin } from 'vuelidate'
import { helpers, numeric, required } from 'vuelidate/lib/validators'
import { mapActions, mapState } from 'vuex'

import clinvarExportApi from '@/api/clinvarExport'

const VARIANT_ZYGOSITY_OPTIONS = Object.freeze([
  'Homozygote',
  'Single heterozygote',
  'Compound heterozygote',
  'Hemizygote',
  'not provided',
])
const VARIANT_ORIGIN_OPTIONS = Object.freeze([
  'not provided',
  'germline',
  'somatic',
  'de novo',
  'unknown',
  'inherited',
  'maternal',
  'paternal',
  'uniparental',
  'biparental',
  'not-reported',
  'tested-inconclusive',
  'not applicable',
  'experimentally generated',
])
const SAMPLE_SOURCE_OPTIONS = Object.freeze([
  'curation',
  'literature only',
  'provider interpretation',
  'phenotyping only',
  'case-control',
  'clinical testing',
  'in vitro',
  'in vivo',
  'research',
  'not provided',
])

function generateVuexVuelidateWrappers(keys) {
  return Object.fromEntries(
    keys.map((key) => [
      key,
      {
        get() {
          if (!this.value) {
            return null
          }
          return this.submissionIndividuals[this.value.sodar_uuid][key]
        },
        set(value) {
          const submissionIndividual =
            this.submissionIndividuals[this.value.sodar_uuid]
          this.updateSubmissionIndividual({ submissionIndividual, key, value })
          this.$v[key].$touch()
        },
      },
    ])
  )
}

export default {
  components: { Multiselect },
  mixins: [validationMixin],
  props: {
    value: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      hpoTermsLoading: false,
      hpoTermsOptions: [],
      variantOriginOptions: VARIANT_ORIGIN_OPTIONS,
      variantZygosityOptions: VARIANT_ZYGOSITY_OPTIONS,
      sampleSourceOptions: SAMPLE_SOURCE_OPTIONS,
    }
  },
  computed: {
    ...mapState({
      appContext: (state) => state.clinvarExport.appContext,
      currentSubmission: (state) => state.clinvarExport.currentSubmission,
      individuals: (state) => state.clinvarExport.individuals,
      submissionIndividuals: (state) =>
        state.clinvarExport.submissionIndividuals,
    }),

    ...generateVuexVuelidateWrappers([
      'source',
      'tissue',
      'variant_origin',
      'variant_allele_count',
      'variant_zygosity',
    ]),

    phenotypes: {
      get() {
        if (!this.value) {
          return []
        }
        return this.submissionIndividuals[this.value.sodar_uuid].phenotypes
      },
      set(value) {
        this.updateSubmissionIndividual({
          submissionIndividual: this.value,
          key: 'phenotypes',
          value,
        })
      },
    },

    citations: {
      get() {
        if (!this.value) {
          return ''
        }
        const submissionIndividual =
          this.submissionIndividuals[this.value.sodar_uuid]
        return submissionIndividual.citations.join(' ')
      },
      set(value) {
        const submissionIndividual =
          this.submissionIndividuals[this.value.sodar_uuid]
        this.updateSubmissionIndividual({
          submissionIndividual,
          key: 'citations',
          value: value.split(/[ ,]+/),
        })
        this.$v.citations.$touch()
      },
    },

    individual() {
      if (!this.value || !this.individuals) {
        return null
      } else {
        return this.individuals[this.value.individual]
      }
    },
  },
  validations: {
    variant_allele_count: {
      required,
      isValid: (x) => numeric(x),
    },
    variant_zygosity: {
      isValidChoice: (x) => VARIANT_ZYGOSITY_OPTIONS.includes(x),
    },
    variant_origin: {
      required,
      isValidChoice: (x) => VARIANT_ORIGIN_OPTIONS.includes(x),
    },
    source: {
      required,
      isValidChoice: (x) => SAMPLE_SOURCE_OPTIONS.includes(x),
    },
    tissue: {
      required,
    },
    citations: {
      isValidChoice: (pmids) =>
        !helpers.req(pmids) ||
        pmids.split(/[ ,]+/).every((s) => s.match(/^PMID:\d+$/)),
    },
  },
  mounted() {
    this.$v.$touch()
  },
  methods: {
    ...mapActions('clinvarExport', [
      'updateSubmissionIndividual',
      'moveSubmissionIndividual',
      'removeSubmissionIndividualFromCurrentSubmission',
    ]),

    /**
     * @param up whether to consider up movement (false is down)
     * @return {boolean} whether moving into the given direction is currently disabled
     */
    isMoveDisabled(up) {
      if (!this.value) {
        return true
      }
      const other = this.value.sort_order + (up ? -1 : 1)
      return (
        other < 0 ||
        other >= this.currentSubmission.submission_individuals.length
      )
    },
    /**
     * @param o Object with `term_id` and `term_name` entires.
     * @returns {string} Appropriate label for the term.
     */
    getHpoTermLabel(o) {
      if (o.term_name.length < 10) {
        return `${o.term_id} - ${o.term_name}`
      } else {
        return `${o.term_id} - ${o.term_name.slice(0, 10)}...`
      }
    },
    /**
     * Find HPO term matching the `query` nad set into appropriate local stae.
     *
     * @param query The query string to search for.
     */
    asyncFindHpoTerms(query) {
      this.hpoTermsLoading = true
      clinvarExportApi.queryHpo(this.appContext, query).then(
        (response) => {
          this.hpoTermsOptions = response.result
          this.hpoTermsLoading = false
        },
        (reject) => {
          throw new Error(`Could not query for HPO terms: ${reject}`)
        }
      )
    },
    /**
     * Validate form input state for the given property.
     */
    validateState(name) {
      if (!this.value) {
        return null
      }
      const submissionIndividual =
        this.submissionIndividuals[this.value.sodar_uuid]
      this.updateSubmissionIndividual({
        submissionIndividual,
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

<style scoped></style>

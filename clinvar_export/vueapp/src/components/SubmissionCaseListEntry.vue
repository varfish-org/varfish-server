<template>
  <div class="card">
    <div class="card-header">
      <h4 class="mb-0 ml-0">
        Case &raquo;{{ individual ? individual.name : 'null' }}&laquo;
        <div class="btn-group float-right pb-0 mb-0">
          <button
            type="button"
            class="btn btn-sm btn-secondary"
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
          </button>
          <button
            type="button"
            class="btn btn-sm btn-secondary"
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
          </button>
          <button
            type="button"
            class="btn btn-sm btn-danger"
            @click="removeSubmissionIndividualFromCurrentSubmission(value)"
          >
            <span
              class="iconify"
              data-icon="mdi:close"
              data-inline="false"
            ></span>
            remove from variant
          </button>
        </div>
      </h4>
    </div>
    <div class="card-body px-2">
      <div class="row">
        <div class="col-12 px-0">
          <div id="input-group-phenotypes" class="form-group">
            <label for="input-phenotypes">Phenotype HPO Terms</label>
            <multiselect
              id="input-phenotypes"
              v-model="phenotypes"
              placeholder="Add HPO terms for this individual"
              track-by="term_id"
              :class="{
                'is-valid': !$v.phenotypes.$error,
                'is-invalid': $v.phenotypes.$error,
              }"
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
            <small class="form-text text-muted">
              Add any HPO terms that are present in the individual.
            </small>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <div id="input-group-source" class="form-group">
            <label for="input-source">Sample Source</label>
            <select
              id="input-source"
              v-model="source"
              required
              :options="sampleSourceOptions"
              :class="{
                'custom-select is-valid': !$v.source.$error,
                'custom-select is-invalid': $v.source.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="sampleSourceOption in sampleSourceOptions"
                :key="sampleSourceOption"
                :value="sampleSourceOption"
              >
                {{ sampleSourceOption }}
              </option>
            </select>
            <div v-if="!$v.source.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div v-if="!$v.source.isValidChoice" class="invalid-feedback">
              Must be a valid sample source.
            </div>
          </div>
        </div>
        <div class="col-4">
          <div id="input-group-tissue" class="form-group">
            <label for="input-source">Tissue</label>
            <input
              id="input-tissue"
              v-model="tissue"
              required
              :class="{
                'form-control is-valid': !$v.tissue.$error,
                'form-control is-invalid': $v.tissue.$error,
              }"
            />
            <div v-if="!$v.tissue.required" class="invalid-feedback">
              Must be provided.
            </div>
          </div>
        </div>
        <div class="col-4 pr-0">
          <div id="input-group-citations" class="form-group">
            <label for="input-citations">Citations</label>
            <input
              id="input-citations"
              v-model.trim="citations"
              required
              :class="{
                'form-control is-valid': !$v.citations.$error,
                'form-control is-invalid': $v.citations.$error,
              }"
            />
            <div v-if="!$v.citations.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div v-if="!$v.citations.isValidChoice" class="invalid-feedback">
              Specify the citations as &laquo;PMID:123 PID:456&raquo;
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-4 pl-0">
          <div id="input-group-variant-origin" class="form-group">
            <label for="input-source">Variant Origin</label>
            <select
              id="input-variant-origin"
              v-model="variant_origin"
              required
              :options="variantOriginOptions"
              :class="{
                'custom-select is-valid': !$v.variant_origin.$error,
                'custom-select is-invalid': $v.variant_origin.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="variantOriginOption in variantOriginOptions"
                :key="variantOriginOption"
                :value="variantOriginOption"
              >
                {{ variantOriginOption }}
              </option>
            </select>
            <div v-if="!$v.variant_origin.required" class="invalid-feedback">
              Must be provided.
            </div>
            <div
              v-if="!$v.variant_origin.isValidChoice"
              class="invalid-feedback"
            >
              Must be a valid variant origin.
            </div>
          </div>
        </div>
        <div class="col-4">
          <div id="input-group-alle-count" class="form-group">
            <label for="input-source">Variant Allele Count</label>
            <input
              id="input-variant-allele-count"
              v-model="variant_allele_count"
              required
              :class="{
                'form-control is-valid': !$v.variant_allele_count.$error,
                'form-control is-invalid': $v.variant_allele_count.$error,
              }"
            />
            <div
              v-if="!$v.variant_allele_count.required"
              class="invalid-feedback"
            >
              Must be provided.
            </div>
            <div
              v-if="!$v.variant_allele_count.isValidChoice"
              class="invalid-feedback"
            >
              Must be a valid variant allele count.
            </div>
          </div>
        </div>
        <div class="col-4 pr-0">
          <div id="input-group-variant-zygosity" class="form-group">
            <label for="input-source">Variant Zygosity</label>
            <select
              id="input-variant-zygosity"
              v-model="variant_zygosity"
              required
              :options="variantZygosityOptions"
              :class="{
                'custom-select is-valid': !$v.variant_zygosity.$error,
                'custom-select is-invalid': $v.variant_zygosity.$error,
              }"
            >
              <option>Chose...</option>
              <option
                v-for="variantZygosityOption in variantZygosityOptions"
                :key="variantZygosityOption"
                :value="variantZygosityOption"
              >
                {{ variantZygosityOption }}
              </option>
            </select>
            <div v-if="!$v.variant_zygosity.required" class="invalid-feedback">
              Must be provided.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
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
    phenotypes: {},
    variant_allele_count: {
      required,
      isValid: (x) => !x || numeric(x),
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

<style>
.is-invalid .multiselect__tags {
  border-color: #dc3545;
}
.is-valid .multiselect__tags {
  border-color: #28a745;
}
</style>
